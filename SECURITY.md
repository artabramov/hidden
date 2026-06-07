# Security (OWASP Top 10: 2025)

This document maps the current backend implementation to the `OWASP Top 10`
(2025) categories. It is an informal self-assessment based on the reviewed
application code and does not constitute a full security audit.

OWASP Top 10 (2025): [owasp.org/Top10/2025/](https://owasp.org/Top10/2025/)


## Threat model

Hidden is intended as a **self-hosted**, **single-tenant** backend:
the operator controls the host, container, volumes, reverse proxy, TLS,
and who may reach the API. Many risks that dominate public multi-tenant
SaaS (e.g. cross-customer isolation, abuse of shared infrastructure at
scale) are **out of scope** or **materially reduced** here because trust
boundaries are drawn around the operator’s environment rather than
anonymous Internet users.

**Operator responsibilities** (not enforced by the app alone): network
exposure, TLS at the gateway, volumetric DDoS and edge-layer flooding,
rate limits and WAF-style rules on `/init` and `/auth` routes, backups,
OS and image hardening, and vetting of `extensions` as trusted in-process
code (see A03/A06/A08).


## A01: Broken Access Control

1. Application access control is enforced through a central
   `require_access()` dependency, attached to routes and evaluated by
   the framework before the handler logic is executed. It validates the
   bearer token structure, JWT signature and claims (`sub`, `jti`,
   and `exp` when present), along with the current user state and
   required permissions.

2. Authentication tokens include a `jti` (unique token identifier) and
   are time-limited by default. When `AUTH_ALLOW_PERMANENT_TOKENS` is
   enabled, users may request tokens without an expiration date; JTI
   rotation on logout and password change still applies, but such
   tokens remain valid indefinitely until explicitly invalidated. This
   is a deliberate trade-off for integration use cases; operators
   should enable this only in trusted deployments. Tokens are
   invalidated on logout and password change by rotating the stored
   `jti`, ensuring that previously issued tokens can no longer be used.

3. The system relies on role-based access (`reader`, `writer`, `editor`,
   `admin`), combined with object-level checks implemented in the service
   layer. For example, comment operations are restricted to their owners,
   while user management logic explicitly prevents users from modifying
   their own role or account status, even if they have sufficient
   permissions to modify other users.

4. An additional restriction layer is implemented through the
   `is_write_protected` flag on folders. This flag propagates recursively
   and blocks all write operations within the subtree, even if the user
   would normally have sufficient role permissions.

5. Low-level operations are protected by the `master password` rather
   than standard user authentication. These include initialization and
   storage management actions (e.g. mount, unmount, lockdown), acting as
   a control layer independent from the JWT-based access model. Routes
   that **verify** the master password against the stored encrypted
   passphrase enforce a **short per-process spacing** between attempts
   and may return **HTTP 429** when calls arrive too quickly;
   **first-time cipherdir create** is excluded from this throttle.

6. The master password is defined during the initial application setup
   and is not persisted. It is provided by the user for each operation
   and used only transiently during verification. Each check is performed
   indirectly by attempting to decrypt the stored encrypted passphrase;
   a successful decryption confirms that the provided master password is
   valid.

7. Shared download links are intentionally unsupported. The primary
   goal of the project is reliable and secure storage of sensitive data,
   so features that intentionally expose files outside the authenticated
   storage boundary are excluded from the architecture and security
   model.


## A02: Security Misconfiguration

1. The application is designed to run behind an external reverse proxy,
   and TLS termination is handled outside of the backend. The service is
   not intended to be exposed directly to untrusted networks, and direct
   access without a properly configured gateway is considered an insecure
   deployment.

2. The API schema and documentation endpoints (`/docs`, `/openapi.json`)
   are always accessible. This simplifies administration and development,
   but also exposes endpoint structure and request/response models to
   anyone who can reach the service. In a self-hosted deployment this is
   usually an operator trade-off (convenience vs. reconnaissance);
   restrict or shield these paths at the reverse proxy if the API is
   reachable from untrusted networks.

3. When **lockdown mode** is enabled, most routes return `503`, but
   `/docs`, `/openapi.json`, and `/init` paths remain available by design
   so operators can still run control-plane and documentation flows.

4. Swagger UI is configured with persisted authorization, meaning bearer
   tokens may be stored in the browser environment during use. This
   improves usability but introduces a risk if the client environment is
   shared or otherwise untrusted.

5. The application relies on environment-based configuration (e.g. `.env`
   for local runs or variables injected by the container runtime). Secret
   handling assumes a controlled runtime environment and does not include
   external secret management or rotation mechanisms.

6. The backend runs as a single worker process to avoid concurrency
   issues with the filesystem and SQLite. This is a deliberate safety
   constraint that prioritizes consistency and data integrity over
   parallel request processing.

7. The container environment is kept minimal, including only required
   runtime dependencies. This reduces the overall attack surface by
   limiting the number of available system components and potential
   vectors.

8. Sensitive data is separated at the storage level. Encrypted
   application data (files and database), encrypted passphrase, and
   internal keys are stored in distinct volumes, reducing the risk of
   accidental exposure or misconfiguration affecting all components at
   once. This separation also simplifies recovery after failures.

9. **CORS** is driven by `CORS_ALLOW_ORIGINS`. An empty value yields
   an empty allow-list: browsers will not treat arbitrary cross-origin
   sites as authorized for credentialed access. Operators must set
   explicit origins for browser-based clients; `allow_methods` and
   `allow_headers` are broad by design once an origin is listed.

10. **HTTP security headers** added by the app include
    `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy`.
    There is no `Content-Security-Policy` on API JSON responses (low
    impact for typical non-browser API clients; `/docs` is served by
    the framework).

11. The unauthenticated **`/init/health`** endpoint returns operational
    flags (e.g. cipherdir initialized, mount state, lockdown, watchdog
    liveness, coarse time metadata). It is useful for orchestration and
    monitoring but assists reconnaissance if the API is exposed; gate it
    at the network or proxy layer when needed.


## A03: Software Supply Chain Failures

1. Application dependencies are explicitly defined and pinned in
   `requirements.txt`. The project references security scanning tools
   such as `pip-audit` and `trivy`, which can be used to identify known
   vulnerabilities in dependencies and container images.

2. The runtime environment is built from a minimal container image with
   a limited set of system packages (e.g. `gocryptfs`, `fuse3`,
   `libmagic`). Reducing the number of installed components helps limit
   the potential attack surface introduced through third-party software.

3. The application supports dynamically loaded extensions implemented as
   Python modules. These extensions are imported and executed in-process,
   with full access to the application context and internal APIs.

4. Extensions are treated as fully trusted code. There is no sandboxing,
   no permission model, and no isolation between extensions and the core
   application, meaning a compromised or malicious extension can affect
   the entire system.

5. There is no mechanism for verifying extension integrity. Extensions
   are not signed, and there is no checksum validation or allowlist of
   trusted modules, which introduces a risk of unauthorized code
   execution if the deployment environment is compromised.

6. Dependency and image scanning are not enforced automatically as part
   of the application runtime. Security of the supply chain depends on
   external processes and the deployment environment.


## A04: Cryptographic Failures

1. All persistent data is stored within a `gocryptfs`-encrypted
   filesystem. This includes user files, file revisions, thumbnails, and
   the database, ensuring that data at rest is protected at the storage
   level.

2. While `gocryptfs` encrypts file **contents** and file/directory
   **names**, a number of structural properties of the encrypted
   directory (`cipherdir`) remain **observable to anyone with read
   access to the host filesystem**: the number of files per directory,
   the approximate size of each file (block-aligned ciphertext length),
   the directory hierarchy depth and branching, and filesystem
   timestamps (mtime/atime/ctime). Per the Threat model, the host is
   operator-controlled, so this is an **accepted trade-off**.

3. The encryption passphrase for the storage is generated randomly during
   initialization and stored in encrypted form. Access to the storage is
   only possible after successful decryption of this passphrase using
   the master password.

4. The passphrase encryption scheme uses a memory-hard key derivation
   function (scrypt) and authenticated encryption (AES-GCM), providing
   resistance against brute-force attacks and ensuring integrity of the
   encrypted data.

5. User passwords are hashed using PBKDF2-HMAC-SHA256 with a per-user
   random salt and a high iteration count. Password verification is
   performed using constant-time comparison to reduce the risk of timing
   attacks.

6. Authentication tokens are implemented as JWTs signed with a symmetric
   key (HS256). Token integrity is ensured through signature validation.
   Token lifetime is limited via expiration claims by default; when
   `AUTH_ALLOW_PERMANENT_TOKENS` is enabled, tokens without `exp` may
   be issued and remain valid until the JTI is rotated.

7. Sensitive application data, including TOTP secrets and token
   identifiers (`jti`), is encrypted at rest using Fernet symmetric
   encryption.

8. Cryptographic key material (e.g. JWT signing key, Fernet key) is
   stored locally within the application environment and protected by
   filesystem permissions, assuming a trusted deployment context.

9. The application does not implement key rotation mechanisms for
   internal cryptographic keys or storage passphrases. Long-lived keys
   are expected to be managed at the operational level.

10. Transport-level security (TLS) is not handled by the application
    itself and must be provided by the deployment environment. Unencrypted
    transport is considered insecure.

11. The **in-memory thumbnail cache** (`app/cache/thumbnail.py`) holds
    decoded thumbnail bytes in process memory to avoid repeated reads
    through the encrypted filesystem. While this data is never written
    to the cipherdir or any application-controlled file, the OS may
    page process memory to swap, transiently materialising plaintext
    thumbnail bytes on disk. Operators on sensitive deployments should
    disable swap or use OS-level encrypted swap. The cache is cleared
    on cipherdir unmount as a defense-in-depth measure; the
    availability middleware blocks requests even if the cache contains
    stale entries.

12. **Emergency passphrase CLI** (`python -m app.runtime.passphrase`,
    module `app.runtime.passphrase`): an **offline recovery path** outside
    the HTTP API. It reads the encrypted passphrase blob from a filesystem
    path, prompts for the master password on the TTY (no echo), and writes
    **decrypted passphrase material to standard output**. This is not
    subject to the same in-app throttling or audit trail as `/init` routes
    that verify the master password over the API. Operational risks
    include **shoulder surfing** or terminal scrollback on shared sessions,
    **unsafe redirection** of stdout to a world-readable file, weak **POSIX
    permissions** on the blob or on any file receiving the plaintext, and
    **host-local exposure** of the process to other OS users. Operators
    should run it only on a trusted machine, with minimal privilege, and
    treat the output like a live root secret (e.g. pipe into a `tmpfs`
    file with `0600`, then consume immediately). The README’s emergency
    `gocryptfs` mount flow is an alternative with the same trust
    assumptions.


## A05: Injection

1. Database access is implemented using SQLAlchemy ORM, avoiding direct
   string-based query construction. Queries are built through expression
   APIs, reducing the risk of SQL injection.

2. The application does not construct shell commands dynamically. External
   tools (e.g. gocryptfs) are invoked using fixed argument lists, without
   shell interpolation, preventing command injection.

3. File and path inputs are strictly validated. Only single path segments
   are allowed, and special values such as `.`, `..`, path separators,
   null bytes, and control characters are explicitly rejected.

4. Structured validators are used for user-controlled inputs such as tags,
   variable keys, and identifiers. These validators enforce type and
   format constraints before values are used in application logic.

5. No direct execution of user-supplied code or expressions is supported
   within the application, limiting the risk of code injection.

6. Input validation is primarily structural and does not include deep
   inspection of file contents. In particular, mismatches between file
   metadata (e.g. MIME type, extension) and actual content are not fully
   enforced.

7. The application does not implement a generic sanitization layer.
   Validation is performed per-field, and correctness depends on the
   completeness of individual validators.


## A06: Insecure Design

1. The application is designed with the database as the source of truth,
   while the filesystem acts as a projection of that state. Consistency
   between the two is maintained at the service layer rather than through
   atomic storage guarantees.

2. File operations (upload, edit, delete, transform) rely on a combination
   of temporary files, locking, and compensation logic. While this
   approach handles most failure scenarios, it does not guarantee full
   atomicity.

3. Folder deletion is not atomic. Direct file entries may be removed
   before the operation fully completes, and a failure during the process
   can lead to partial inconsistency between the database and filesystem.

4. Cleanup of temporary and intermediate artifacts is best-effort. In the
   event of crashes or unexpected termination, orphaned files may remain
   on disk.

5. The system does not enforce global resource limits for operations such
   as file upload, text editing, or image processing. This allows
   potential resource exhaustion (CPU, memory, disk) under heavy or
   malicious input.

6. Image processing operations do not enforce limits on image dimensions
   or pixel count. This introduces a risk of decompression bomb-style
   attacks and excessive resource consumption.

7. File type handling is based on metadata (e.g. MIME type) and does not
   fully verify consistency with actual file content, allowing potential
   mismatches to go undetected.

8. The authentication flow separates password verification and TOTP
   validation without a strongly bound intermediate session, relying on
   transient state between steps (for example `mfa_session_uuid` and a
   password-verification timestamp).

9. **Registration throttling** limits the count of **successfully created** 
   users within a time window. Failed attempts that stop at “username
   already exists” **do not** consume the throttle budget. That trade-off
   favors clarity for legitimate users but is not equivalent to per-request
   or per-IP registration flooding controls; rely on network placement
   or proxy limits if that threat matters.

10. The system assumes a trusted deployment environment and does not
    attempt to defend against malicious extensions or compromised runtime
    environments as part of its core design.

11. **Volumetric DDoS**, connection floods, and similar **network-** or
    **edge-layer** abuse are **not** mitigated inside the application;
    rely on reverse proxy, firewall, or equivalent. **Brute-force** and
    high-frequency **application-level** abuse (e.g. against `/auth`)
    are not uniformly covered by in-app rate limiters; use operator-side
    controls when exposure warrants them. Per-process master-password
    spacing on selected `/init` routes (see item 5) is auxiliary and
    does not replace those controls.


## A07: Authentication Failures

1. Authentication is implemented as a two-step process consisting of
   password verification followed by TOTP validation. A JWT token is
   issued only after both steps are successfully completed.

2. User passwords are stored as salted hashes using PBKDF2-HMAC-SHA256
   with a high iteration count. Password verification uses constant-time
   comparison to reduce the risk of timing attacks.

3. TOTP is used as a second authentication factor. TOTP secrets are
   stored in encrypted form and are never exposed in plaintext after
   initial setup.

4. Authentication tokens include a `jti` (unique token identifier).
   Token validity is enforced through signature verification, matching
   against the current stored `jti`, and expiration checks when an
   `exp` claim is present. When `AUTH_ALLOW_PERMANENT_TOKENS` is
   enabled, tokens without `exp` may be issued and do not expire; JTI
   rotation on logout and password change is the sole revocation
   mechanism for such tokens.

5. Tokens are invalidated on logout and password change by rotating the
   stored `jti`, ensuring that previously issued tokens can no longer be
   used.

6. Repeated authentication failures (password or TOTP) result in temporary
   user suspension, limiting the effectiveness of brute-force attacks.

7. The authentication flow does not use a strongly bound intermediate
   session between password and MFA second-factor (TOTP) steps, relying
   instead on transient state (for example `mfa_session_uuid` and a
   password-verification timestamp). This introduces a potential risk in
   edge-case scenarios.

8. Rate limiting is not uniformly enforced across all authentication
   endpoints. While some protections exist (e.g. suspension), they do
   not fully prevent high-frequency attack patterns.

9. The system does not fully mitigate username enumeration via timing
   or behavioral differences between valid and invalid authentication
   attempts.

10. Initial user provisioning grants elevated privileges to the first
    registered user, after which new users are created with restricted
    access by default. Creation of that first admin is **serialized**
    with a dedicated lock; subsequent users default to non-admin roles
    unless changed by an administrator.


## A08: Software or Data Integrity Failures

1. The application maintains an append-only audit log that records
   security-relevant events, preserving historical integrity of actions
   performed within the system.

2. File modifications are implemented through a revision-based model.
   Changes result in new revisions rather than in-place updates, allowing
   previous states to be retained and reducing the risk of silent data
   corruption.

3. The system includes a hook mechanism that allows extensions to react
   to events after operations are completed. Hooks are executed **after**
   the main operation’s transaction is **committed**; they do not
   participate in that transaction and cannot change its outcome.

4. For a **successful file download**, the audit record is written and
   **committed before** post-commit hooks run. Hooks thus see a persisted
   audit entry for that path; they cannot roll back the audit row as part
   of the same service transaction.

5. Extensions are dynamically loaded and executed in-process as trusted
   code. They have full access to the application context and can interact
   with internal APIs and data.

6. There is no isolation, sandboxing, or permission model for extensions.
   A compromised or malicious extension can modify application behavior,
   access sensitive data, or bypass security controls.

7. The application does not implement integrity verification for
   extensions. Extensions are not signed, and no checksum or allowlist
   validation is performed before loading.

8. The system does not perform integrity validation of stored files
   beyond what is provided by the underlying encrypted filesystem.
   Application-level checksums or verification mechanisms are not
   implemented.

9. There is no mechanism for verifying the integrity of application
   code, dependencies, or runtime artifacts after deployment. Integrity
   assurance relies on external processes and a trusted deployment
   environment.


## A09: Security Logging and Alerting Failures

1. The application implements structured logging and maintains an
   append-only audit log for security-relevant events. Each request is
   associated with a unique identifier, allowing correlation between
   logs and audit records.

2. Audit records include key metadata such as user identifier, resource
   identifier, event type, and timestamp, providing a traceable history
   of actions performed within the system.

3. Logging explicitly avoids sensitive data exposure. Passwords, tokens,
   cryptographic keys, TOTP secrets, and file contents are not written
   to logs or audit records.

4. Security-relevant operations (e.g. authentication, authorization,
   file and user management) are consistently recorded, ensuring that
   critical actions can be reviewed after the fact.

5. Logs and audit data are stored locally and are not exported to
   external systems. There is no built-in log aggregation, centralized
   storage, or integration with monitoring platforms.

6. The application does not implement alerting or notification mechanisms
   based on log or audit events. Suspicious activity is not automatically
   detected or escalated.

7. No anomaly detection or behavioral analysis is performed. Detection
   of security incidents relies entirely on manual inspection or external
   monitoring systems.

8. Optional client-supplied **`X-Request-ID`** is accepted only when it
   matches a bounded length and allowed character set; otherwise a new
   identifier is generated. This limits unbounded or hostile header
   values in logs and correlation fields.


## A10: Mishandling of Exceptional Conditions

1. The application defines a structured exception model and returns
   controlled HTTP responses for expected error conditions. Internal
   errors result in generic responses without exposing implementation
   details.

2. Critical operations (e.g. file manipulation, storage actions) include
   rollback or compensation logic to reduce the impact of partial failures
   and maintain consistency between the database and filesystem.

3. Locking mechanisms are used to prevent concurrent conflicts during
   state-changing operations, and lock-related failures are handled
   explicitly at the service level.

4. Temporary files and intermediate artifacts are used during operations
   to avoid direct modification of persistent data. In case of failure,
   the system attempts to clean up or restore the previous state.

5. Exception handling in some parts of the system relies on broad catch
   blocks, prioritizing system stability over strict failure isolation.
   This may obscure specific failure causes in certain scenarios.

6. Cleanup and recovery logic is implemented on a best-effort basis.
   Under crash or abrupt termination conditions, orphaned files or
   partially applied operations may remain.

7. The system does not guarantee full atomicity for multi-step operations.
   Failures occurring between steps may result in temporary inconsistency
   between components until corrected.

8. Service availability is explicitly controlled through states such as
   lockdown or unmounted storage. In such cases, operations fail with
   controlled responses (e.g. 503), preventing undefined behavior.


## Reporting Security Issues

Security issues should be reported privately to the author:
[linkedin.com/in/art-abramov](https://www.linkedin.com/in/art-abramov/)
