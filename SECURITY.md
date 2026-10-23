# Security (OWASP Top 10: 2025)

This document maps the current implementation of Hidden S3 to the
`OWASP Top 10` (2025) categories. It is an informal self-assessment
based on the reviewed application code, container build, and deployment
scripts and does not constitute a full security audit.

OWASP Top 10 (2025): [owasp.org/Top10/2025/](https://owasp.org/Top10/2025/)


## Known security limitations

Hidden S3 protects stored data primarily while the encrypted filesystem
is locked. It is intended for trusted, privately managed infrastructure,
not direct exposure of its management API to the public Internet.

- **No built-in TLS.** The management API, S3 API, and WebGUI use HTTP.
  The operator must secure network transport and restrict access.
- **No protection against a compromised running system.** While storage
  is unlocked, sufficiently privileged host or container processes can
  access decrypted files and credentials.
- **No limit on password attempts.** The management API does not impose
  rate limits, delays, or lockouts. Network access must be controlled.
- **Automatic locking is not instantaneous.** The watchdog checks
  periodically. Stopping VersityGW or unmounting gocryptfs can fail;
  lazy unmount can leave open files accessible to surviving processes.
- **In-progress writes can be interrupted.** Container shutdown and
  emergency unmount do not guarantee completion of active S3 requests.
- **Loss of recovery secrets can make data inaccessible.** Keep secure
  backups of the master password or recovered gocryptfs passphrase,
  according to your recovery policy.
- **Encryption does not prevent deletion or rollback.** Someone with
  write access to encrypted storage can delete files or restore older
  encrypted copies without knowing the password.
- **Reset is destructive.** It deletes stored data and secrets. Cleanup
  and recovery after interrupted operations are not transactional.

These are current implementation limitations, not guarantees that every
listed failure will occur. Details follow.


## Threat model

Hidden S3 is intended as a **self-hosted**, **single-tenant** storage
appliance: the operator controls the host, container, volumes, network,
TLS, and who may reach the exposed ports. The container provides three
interfaces: the `FastAPI` management API (port `8081`), the `VersityGW`
S3 API (port `9000`), and the `VersityGW` WebGUI (port `8080`). Many
risks that dominate public multi-tenant SaaS (e.g. cross-customer
isolation, abuse of shared infrastructure at scale) are **out of scope**
or **materially reduced** here because trust boundaries are drawn around
the operator’s environment rather than anonymous Internet users.

The primary protected asset is **data at rest** in two volumes: the
`cipherdir` with encrypted S3 objects and IAM state, and the `secrets`
volume with the encrypted `gocryptfs` passphrase and encrypted `VersityGW`
root credentials. Access to the encrypted volumes alone is intended not
to expose plaintext without the required decryption secrets; this does
not cover compromise of the running host, memory, or previously revealed
keys. While the storage is mounted, decrypted data exists inside the
container, and its protection relies on the runtime environment and
on the S3 access controls of `VersityGW`.

**Operator responsibilities** (not enforced by the app alone): network
exposure of ports `8081`, `9000`, and `8080`, TLS at the gateway,
volumetric DDoS and edge-layer flooding, rate limits and access rules
for the management API, physical handling of the removable `secrets`
media, backups of the `cipherdir`, host and Docker hardening, and
management of `VersityGW` IAM users and bucket policies (see A01/A02/A06).


## A01: Broken Access Control

1. The management API has no user accounts, sessions, or tokens.
   Operations on the encrypted storage (`mount`, `unmount`, `reveal`,
   `rotate`, `reset`) are authorized solely by the `master password`.
   Each check is performed indirectly by attempting to decrypt the
   stored encrypted passphrase; a successful decryption confirms that
   the provided master password is valid.

2. The master password is defined during initialization and is not
   persisted. It is provided in the request body for each operation and
   used only transiently in memory during verification.

3. **`POST /gocryptfs/init`** is unauthenticated by design. It is
   accepted only while the `cipherdir` is not initialized, the storage
   is not mounted, no encrypted passphrase exists, and the credential
   check does not find **both** non-empty `VersityGW` credential files.
   A missing, empty, or unreadable credential file can cause that check
   to return false even if another credential file remains.
   Until initialization is complete, anyone who can reach port `8081` can
   initialize the storage with their own master password and receive the
   `VersityGW` root credentials. Operators should initialize the storage
   immediately after installation, before exposing the port.

4. Route preconditions are enforced through a central
   `require_gocryptfs()` dependency, attached to routes and evaluated
   by the framework before the handler logic is executed. Per route, it
   requires, forbids, or ignores the presence of the `cipherdir`, the
   mountpoint, and the encrypted passphrase, and returns `503` or `502`
   when the storage state does not match.

5. **`POST /gocryptfs/reveal`** returns the decrypted `gocryptfs`
   passphrase together with the `VersityGW` root credentials to anyone
   who presents the master password. This is an intentional recovery
   path; the response must be treated as a live root secret.

6. **`POST /gocryptfs/reset`** attempts to irreversibly delete the
   contents of the `cipherdir` and stored secrets after a single master
   password check. There is no additional confirmation step. It uses
   lazy unmount before deletion when storage is mounted; cleanup is not
   transactional and does not verify that all prior file users exited.

7. Access to buckets and objects is controlled by `VersityGW` and its
   IAM. The application creates the root credentials during
   initialization and passes them to `VersityGW` on mount. Additional
   users, bucket policies, and per-user permissions are managed through
   `VersityGW` and are outside the scope of this application.

8. The unauthenticated **`GET /gocryptfs/health`** endpoint returns
   operational flags (cipherdir initialized and mounted, `VersityGW`
   credentials present and process running, watchdog liveness) together
   with the current Unix time and the host timezone name. It is useful
   for orchestration and monitoring but assists reconnaissance if the
   API is exposed; gate it at the network or proxy layer when needed.


## A02: Security Misconfiguration

1. TLS termination is handled outside of the container. The management
   API, the S3 API, and the WebGUI all listen over plain HTTP, the
   default configuration binds them to `0.0.0.0`, and `make install`
   publishes ports `8081`, `9000`, and `8080` on all host interfaces.
   The master password, the revealed passphrase, and S3 credentials
   cross the network in cleartext unless a TLS gateway or a private
   network is placed in front of the container. Direct access from
   untrusted networks is considered an insecure deployment.

2. The API schema and documentation endpoints (`/docs`, `/openapi.json`)
   are always accessible, and Swagger UI has "try it out" enabled. This
   simplifies administration, but also exposes endpoint structure and
   request/response models to anyone who can reach the service, and the
   master password is typed into request bodies in the browser. Restrict
   or shield these paths at the reverse proxy if the API is reachable
   from untrusted networks.

3. The container runs as `root` with `--cap-add SYS_ADMIN`,
   `--device /dev/fuse`, and `--security-opt apparmor:unconfined`, which
   are required for `FUSE`. This privilege level increases the impact of
   a compromise of any process inside the container.

4. `make install` bind-mounts the parent directory of the `secrets`
   volume with `rslave` propagation and marks it as a shared mount on the
   host, so that removal of the media on the host is visible inside the
   container. With `make install FORCE=1`, the `secrets` directory is
   created as a local directory on the host filesystem; the detachable
   secret protection then depends on the operator removing the media or
   files manually.

5. The application relies on environment-based configuration. On the
   first start, the entrypoint copies the bundled `.env` to
   `/etc/hidden/.env` with mode `0600`; the default file contains no
   secrets. Runtime files are created with `umask 077`. Secret handling
   assumes a controlled runtime environment and does not include
   external secret management.

6. The backend runs as a single worker process. The in-process lock that
   serializes storage operations relies on this constraint; running
   several workers would break that guarantee.

7. Sensitive data is separated at the storage level. Encrypted S3 data
   and IAM state reside in the `cipherdir` Docker volume, while the
   encrypted passphrase and the encrypted `VersityGW` credentials reside
   in the bind-mounted `secrets` volume (ADR-07). This separation allows
   the `secrets` volume to be kept on removable media or a remote host.

8. **CORS** for the management API is driven by `CORS_ALLOW_ORIGINS`.
   An empty value yields an empty allow-list. Listed origins receive
   credentialed access, and `allow_methods` and `allow_headers` are broad
   by design. The default `.env` lists local development origins, which
   operators should replace for production. CORS for the WebGUI is
   configured separately through `VERSITY_WEBGUI_CORS_ALLOW_ORIGIN`.

9. **HTTP security headers** added by the management API include
   `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy`.
   There is no `Content-Security-Policy` on API JSON responses (`/docs`
   is served by the framework). These headers do not apply to the
   `VersityGW` S3 API and WebGUI.

10. `.dockerignore` excludes only Python bytecode, so the image includes
    the whole build context, such as `.git`, tests, and local tooling
    configuration.


## A03: Software Supply Chain Failures

1. Python dependencies are explicitly defined and pinned to exact
   versions in `requirements.txt`, without hash verification. The same
   file includes development tools (`coverage`, `flake8`), which are
   installed into the runtime image.

2. `VersityGW` is installed from a fixed GitHub release (`v1.8.0`). The
   downloaded `.deb` package is verified against a SHA-256 checksum
   stored in the `Dockerfile`, and the build fails on mismatch.

3. The base image `python:3.12-slim` is referenced by tag, and
   `gocryptfs` and `fuse3` are installed from Debian repositories without
   version pinning. Rebuilding the image may therefore pick up different
   system packages.

4. The runtime environment is built from a minimal container image with a
   limited set of system packages (`gocryptfs`, `fuse3`, `VersityGW`, and
   their dependencies). The image targets `amd64` only, matching the
   `VersityGW` release artifact.

5. Dependency and image scanning are not enforced automatically as part
   of the build or runtime. Security of the supply chain depends on
   external processes and the deployment environment.

6. The application does not download or install updates at runtime and
   does not send telemetry. Upgrades remain under operator control.


## A04: Cryptographic Failures

1. All S3 objects and IAM state are stored within a `gocryptfs`-encrypted
   filesystem using a POSIX layout. File contents and file and directory
   names are encrypted at rest.

2. A number of structural properties of the `cipherdir` remain
   **observable to anyone with read access to it**: the number of files
   per directory, the approximate size of each file, the directory
   hierarchy, and filesystem timestamps. This is an **accepted
   trade-off** (ADR-03).

3. The `gocryptfs` passphrase is generated randomly during initialization
   as an 80-character string of letters and digits using the `secrets`
   module. It is stored only in encrypted form on the `secrets` volume.

4. The passphrase encryption scheme uses a memory-hard key derivation
   function (`scrypt`, `N=2^15`, `r=8`, `p=1`, 16-byte random salt) and
   authenticated encryption (`AES-256-GCM`, 12-byte random nonce),
   providing resistance against brute-force attacks and ensuring
   integrity of the encrypted data. The format header (magic and
   version) is not bound as associated data, and the `scrypt` cost is
   below the current OWASP recommendation for password storage.

5. The master password must be 16–1024 characters long and contain a
   lowercase letter, an uppercase letter, and a digit when it is set or
   changed. Passwords are not Unicode-normalized, so visually identical
   strings in different normalization forms are treated as different
   passwords.

6. The `VersityGW` root access key and secret key (20 and 40 random
   characters) are stored on the `secrets` volume encrypted with the
   `gocryptfs` passphrase using the same scheme. Possession of the
   `secrets` volume does not expose S3 root credentials without the
   master password. Master password rotation leaves the credential
   files unchanged, because the passphrase that protects them stays the
   same.

7. The passphrase is provided to `gocryptfs` through a temporary file in
   `tmpfs` (`/dev/shm`) with owner-only permissions and passed with
   `-passfile`. The file exists only for the duration of the command and
   is removed immediately after use; the passphrase never appears in
   process arguments (ADR-05).

8. `VersityGW` receives its root credentials through the
   `ROOT_ACCESS_KEY` and `ROOT_SECRET_KEY` environment variables. They
   are visible to privileged processes inside the container through
   `/proc`.

9. Master password rotation re-encrypts the stored passphrase, while the
   `gocryptfs` passphrase itself stays the same. Earlier copies of the
   encrypted passphrase remain decryptable with the previous master
   password, and anyone who has already revealed the passphrase retains
   the ability to mount the `cipherdir`. There is no rotation mechanism
   for the `gocryptfs` passphrase or the `VersityGW` root credentials.

10. Decrypted secrets exist in Python process memory as immutable objects
    that cannot be wiped explicitly. The OS may page process memory to
    swap; operators on sensitive deployments should disable swap or use
    OS-level encrypted swap.

11. Transport-level security (TLS) is not handled by the application
    itself and must be provided by the deployment environment.
    Unencrypted transport is considered insecure.

12. **Emergency recovery** is possible without the application: the
    passphrase returned by `/gocryptfs/reveal` can be used to mount the
    `cipherdir` directly with `gocryptfs`. This path shares the trust
    assumptions of `reveal`: the passphrase grants full access to the
    stored data, so it should be used only on a trusted machine and
    treated like a live root secret.


## A05: Injection

1. The application does not construct shell commands dynamically.
   External tools (`gocryptfs`, `fusermount3`, `versitygw`) are invoked
   using fixed argument lists, without shell interpolation, preventing
   command injection.

2. Filesystem paths are derived from configuration only. User-controlled
   input is limited to master password fields, which are never used to
   build paths, commands, or queries.

3. Request schemas reject unknown fields and validate types and field
   constraints before values are used in application logic.

4. The application has no database and builds no queries. Object storage,
   object metadata, and IAM state are handled by `VersityGW`.

5. No direct execution of user-supplied code or expressions is supported
   within the application, limiting the risk of code injection.


## A06: Insecure Design

1. The **detachable secrets volume** is a core design element. Without
   the encrypted passphrase, the storage cannot be mounted, and the
   watchdog unmounts the decrypted filesystem when the passphrase becomes
   unavailable.

2. The watchdog runs as a separate process every
   `WATCHDOG_INTERVAL_SECONDS` (60 by default). Loss of the passphrase
   may remain undetected until the next check. Stopping `VersityGW` and
   unmounting the filesystem take additional time and can fail. There
   is no guaranteed maximum time until decrypted data becomes
   inaccessible.

3. The watchdog checks only that the encrypted passphrase file exists and
   is not empty, and that the application process is running. It does
   not verify the content of the passphrase file.

4. Emergency unmount **attempts** to stop `VersityGW` and then performs
   a lazy unmount (`fusermount3 -uz`) regardless of the stop result.
   The stop exception is silently ignored by this caller. Lazy unmount
   detaches the mountpoint but does not guarantee immediate loss of
   access through already open file descriptors. A surviving process
   may retain access to decrypted data (tracked as a TODO in the code).

5. The watchdog is not synchronized with the management API. Storage
   operations in the API are serialized by an in-process lock, while the
   watchdog runs in a separate process and may act during a `mount` or
   `unmount` in progress.

6. There is no rate limiting or lockout for master password attempts.
   Storage operations are serialized by a single lock, and each attempt
   costs one `scrypt` derivation, which slows online guessing without
   bounding it. Restrict access to the management API at the network or
   proxy level.

7. Password fields used for authentication have no maximum length, and
   the application does not limit request body size. Size limits should
   be enforced at the reverse proxy.

8. **Volumetric DDoS**, connection floods, and similar **network-** or
   **edge-layer** abuse are **not** mitigated inside the application or
   `VersityGW`; rely on reverse proxy, firewall, or equivalent.

9. The system assumes a trusted deployment environment and does not
   attempt to defend against a compromised host or container while the
   storage is mounted.


## A07: Authentication Failures

1. Authentication on the management API uses a single factor: the master
   password. There is no MFA, session, or token model.

2. Verification is performed by decrypting the stored passphrase with a
   key derived through `scrypt`. A wrong password and a corrupted
   passphrase file both produce the same `401` response with an empty
   body.

3. Password composition rules apply only when the master password is set
   during initialization or changed through rotation. Authentication
   requests do not re-check composition.

4. Repeated authentication failures are logged as warnings and do not
   trigger lockout, delays, or suspension (see A06).

5. S3 and WebGUI authentication is implemented by `VersityGW`. The root
   credentials are generated by the application; additional users are
   managed through `VersityGW` IAM.

6. Request validation errors (`422`) use the framework default format,
   which echoes the submitted value of the failing field back to the
   client. A master password rejected by composition rules is therefore
   returned in the response body; it is not written to logs.


## A08: Software or Data Integrity Failures

1. The encrypted passphrase and the encrypted `VersityGW` credentials
   are protected by `AES-GCM` authentication. Any modification is
   detected during decryption and rejected.

2. `gocryptfs` authenticates encrypted file contents, so tampering with
   data blocks in the `cipherdir` is detected on read. Deletion of whole
   files or rollback to an earlier copy of a file is not detected.

3. Secrets are written atomically: data is written to a temporary file,
   flushed, fsynced, atomically replaced, and the parent directory is
   fsynced.

4. The `VersityGW` package is verified by SHA-256 at build time (see
   A03). There is no mechanism for verifying the integrity of
   application code, Python dependencies, or system packages after
   deployment. Integrity assurance relies on external processes and a
   trusted deployment environment.

5. The application does not perform integrity validation of stored
   objects beyond what is provided by the underlying encrypted
   filesystem. Object versioning, when required, is provided by
   `VersityGW`.


## A09: Security Logging and Alerting Failures

1. The application writes `key=value` log messages to the container
   standard output. Request-start logs include method, full URL, and
   client address; completion logs include status code and elapsed time.

2. Each request is associated with a unique identifier. A client-supplied
   **`X-Request-ID`** is accepted only when it matches a bounded length
   and allowed character set; otherwise a new identifier is generated.
   The identifier is returned in the response headers.

3. The application does not intentionally log request bodies, master
   passwords, passphrases, or S3 credentials. **However, it logs the
   full request URL, including its query string.** Secrets supplied in
   URL parameters can therefore enter container logs. Command error
   output from `gocryptfs` and `fusermount3` is also logged on failure.
   Do not place secrets in URLs; restrict access to logs.

4. Many security-relevant events, such as an invalid master password,
   conflicting storage state, or watchdog emergency unmount, are logged
   as warnings or errors. Not every cleanup failure is logged: several
   `versity_stop()` exceptions are silently suppressed by callers.

5. There is no audit log, centralized storage, or integration with
   monitoring platforms. Logs are retained by the container runtime.

6. The application does not implement alerting or notification
   mechanisms. Detection of security incidents relies on external
   monitoring of container logs and the `/gocryptfs/health` endpoint.

7. `VersityGW` writes its own output to the container standard error.
   The application does not enable `VersityGW` access logging.


## A10: Mishandling of Exceptional Conditions

1. The application defines a structured exception model and returns
   controlled HTTP responses with empty bodies (`401`, `500`, `502`,
   `503`). Unexpected errors result in a generic `500` response without
   exposing implementation details; the traceback is written only to the
   logs.

2. Storage operations are serialized by a process-wide lock. Under the
   lock, `mount` and `unmount` re-check the mount state before acting.

3. Initialization is not transactional. On failure, the service
   attempts to delete the encrypted passphrase, `gocryptfs` configuration
   files, and both `VersityGW` credential files. Cleanup is not limited
   to files demonstrably created by the current attempt. Because the
   credential precheck requires both non-empty files, a partially
   initialized state can lead to an existing credential file being
   overwritten or deleted during a later failed initialization.
   Interrupted initialization may require manual recovery (ADR-06).

4. If a step fails after `cipherdir_mount()` returns successfully,
   including credential decryption or `VersityGW` startup, the service
   **attempts** to stop `VersityGW` and unmount the storage. Either
   cleanup action can fail; successful rollback is not guaranteed.

5. `versity_stop()` attempts `SIGTERM` and, after
   `VERSITY_STOP_TIMEOUT_SECONDS`, `SIGKILL` if the process is still
   running. Startup failures are reported as internal errors. The
   `mount`, `unmount`, `reset`, and emergency-unmount callers suppress
   exceptions from `versity_stop()` without logging those exceptions
   themselves, and still attempt to unmount where applicable.

6. A failed watchdog run is logged, and the next run starts on schedule,
   so a single error does not stop monitoring.

7. Some cleanup paths deliberately suppress errors so that an unmount
   attempt still runs. This is intentional for rapid access shutdown,
   but can hide a failed stop and does not guarantee successful unmount.

8. On container stop, the application does not run an explicit shutdown
   sequence for `VersityGW` and `gocryptfs`. Container termination can
   interrupt active S3 requests and leave incomplete operations. The
   container's mount namespace is removed when its processes exit;
   this is not a guarantee of graceful write completion.

9. Service availability is explicitly controlled by the storage state.
   Operations on an uninitialized, unmounted, or conflicting storage fail
   with controlled responses (`502` or `503`), preventing undefined
   behavior.
