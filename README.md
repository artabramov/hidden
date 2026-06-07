# Hidden — encrypted file storage

Hidden is a self-hosted encrypted file storage application focused on
data ownership, privacy, and operational independence. It targets
personal use and co-located teams that prefer to manage sensitive
information within their own infrastructure rather than relying
exclusively on third-party storage providers.

The application is delivered as a `Docker` image and can run anywhere
Docker is supported. Built with `gocryptfs` and `FastAPI`, it exposes
a `REST API` for file operations (upload, move, rename, edit, tag,
comment, download, delete) over an encrypted userspace filesystem.
File operations follow `POSIX` semantics with atomic guarantees where
applicable.

Two volumes are used: `cipherdir` (encrypted data storage) and `secrets`.
The cipherdir is unlocked using a `gocryptfs passphrase` stored in the
secrets volume. The passphrase itself is encrypted and requires a
`master password` for each use. Removing the encrypted passphrase
triggers an automatic unmount of the decrypted view. Without the
passphrase and master password, data remains inaccessible.

The encrypted storage remains accessible without the application itself.
In emergency scenarios, the `cipherdir` can be mounted directly with
`gocryptfs` using the decrypted passphrase. The complete application
instance, including all data, metadata, users, and cryptographic
material, can also be restored from the two volumes and the master
password.

The application supports multi-user access with role-based permissions
(`RBAC`) and TOTP-based multi-factor authentication (`MFA`).

The application follows a modular architecture with a hook-based
extension mechanism, allowing functionality to be extended without
modifying the core application code.

Feedback on architecture, security assumptions, and design trade-offs is
welcome:
[linkedin.com/in/art-abramov](https://www.linkedin.com/in/art-abramov/)

![version](https://img.shields.io/badge/version-0.5.11-2f81f7)
![test coverage](https://img.shields.io/badge/test%20coverage-99.9%25-2f81f7)
![security audit](https://img.shields.io/badge/security%20audit-2026--06--07-2f81f7)
[![license](https://img.shields.io/badge/license-SSPL--1.0-2f81f7)](./LICENSE)

If you like it, star it ⭐ — it helps discoverability. Thank you!


## References

- Userspace filesystem: [FUSE](https://www.kernel.org/doc/html/next/filesystems/fuse.html)
- Encrypted overlay filesystem: [gocryptfs](https://nuetzlich.net/gocryptfs/)
- Architectural decisions: [ADR.md](./ADR.md)
- OWASP self-assessment: [SECURITY.md](./SECURITY.md)


## Quick start

Build and run the container. By default, the application is exposed on
port `80`:

```sh
make install
```

To use a custom port:

```sh
make install PORT=8080
```

Open in browser:

```sh
http://localhost:8080/docs
```

The container exposes two persistent volumes (application-managed data only):

- **hidden-cipherdir** — encrypted data storage
- **hidden-secrets** — storage for the encrypted passphrase and internal keys

The storage model is based on three independent components:

- **Master password** — decrypts encrypted passphrase
- **Encrypted passphrase** — unlocks cipherdir when decrypted
- **gocryptfs cipherdir** — stores encrypted data

The decrypted passphrase can be revealed with:

```sh
make passphrase
```

If the correct master password is provided, the decrypted passphrase is
displayed in the current terminal session. The passphrase can be used to
mount the encrypted storage directly with `gocryptfs`.


## Key features

The application extends the encrypted filesystem with storage control,
multi-user access, file management, auditing, monitoring, and
integration features:

- **Encrypted storage management** — storage initialization, mount and
  unmount operations, master-password rotation, lockdown control, and
  health monitoring.
- **User management** — user registration, activation, role assignment,
  and profile updates.
- **Role-based access control** — administrators, editors, writers, and
  readers with clearly separated permissions.
- **Two-factor authentication** — TOTP authentication, recovery codes,
  token invalidation, and account recovery workflows.
- **Audit logging** — per-user audit trail of data access, modifications,
  and administrative events.
- **Hierarchical folder structure** — nested folders with metadata,
  filtering, ordering, and recursive write protection for entire folder
  subtrees.
- **File organization and discovery** — metadata, thumbnails, starred
  files, filtering, search, and file summaries.
- **File annotations** — tags and comments for content organization and
  contextual information.
- **Built-in file operations** — upload, download, move, rename, text
  editing, image rotation, and image flipping.
- **File versioning** — revision history and access to previous file
  versions.
- **Extensibility** — hook-based events and extension mechanisms for
  integrating custom functionality into system events and workflows.
- **Automation and integrations** — REST API with OpenAPI documentation
  and support for custom clients.
- **Metrics and monitoring** — runtime, system, process, database, and
  cache metrics for operational visibility.


## Use cases

The project is intentionally **not** designed as a large-scale cloud
platform, real-time collaborative editor, CDN, or distributed object
storage system. Typical use cases include:

- **Personal encrypted storage** — financial documents, private archives,
  personal photos and media, scans, notes, and backups.
- **Co-located teams and studios** — internal assets, contracts,
  production materials, and collaborative document storage without
  external SaaS dependencies.
- **Self-hosted family or homelab storage** — private photos, videos,
  documents, and archives that do not require sharing, publishing, or
  social features.
- **Secure document repositories** — legal, accounting, research, or
  administrative documents requiring controlled access and auditability.
- **Sensitive creative work** — manuscripts, drafts, source assets,
  recordings, design files, and unpublished media.
- **Internal company storage backends** — encrypted file storage exposed
  through a REST API for integration with other applications or services.
- **Backup and archival targets** — encrypted long-term storage for
  snapshots, revisions, exported datasets, and offline archives.
- **Air-gapped or isolated deployments** — environments where external
  network connectivity is restricted or intentionally unavailable.


## How it works

The application is a **REST API wrapper around gocryptfs**. It uses an
internal mountpoint to access the decrypted view of the cipherdir, while
exposing data through the API. A watchdog monitors the presence and
validity of the encrypted passphrase data, as well as application health,
and performs automatic unmount at runtime.

```sh
┌───────────────────────┐
│ FastAPI application   │───── REST API provides access
│ (API layer)           │      to the encrypted storage
└───────────────────────┘
            │
┌───────────────────────┐
│ gocryptfs mountpoint  │───── Decrypted data is exposed
│ (decrypted view)      │      through the mountpoint
└───────────────────────┘
            │
┌───────────────────────┐
│ watchdog              │───── Monitors secrets presence
│ (mount supervisor)    │      and unmounts the mountpoint
╞═══════════════════════╡
│ gocryptfs engine      │----- Uses detachable secrets
│ (FUSE layer)          │      (gocryptfs passphrase)
└───────────────────────┘
            │
┏━━━━━━━━━━━━━━━━━━━━━━━┓
┃ gocryptfs cipherdir   ┃----- Without the passphrase and
┃ (encrypted storage)   ┃      master password, all data
┃ ┌───────────────────┐ ┃      becomes unreadable blobs
┃ │ Database, files,  │ ┃
┃ │ revisions, meta   │ ┃
┃ └───────────────────┘ ┃
┗━━━━━━━━━━━━━━━━━━━━━━━┛
```


## What is protected

The application is designed to protect encrypted data against
unauthorized access and storage exposure scenarios. These protections
remain effective even if an attacker obtains the application volumes
(including the secrets volume) or physically steals the host system.

- **Stolen device or disk.** All data (files, revisions, thumbnails,
  metadata DB) remains encrypted blobs. Mounting requires the encrypted
  passphrase from the secrets volume **and** the master password.
- **Unauthorized low-level disk access.** The cipherdir never stores
  plaintext data, even temporarily. After unmount, attempts to recover
  data directly from the disk — including raw sector scanning, undelete
  tools, or filesystem carving — cannot restore decrypted file contents.
- **Leaked backup of cipherdir.** The volume contains only ciphertext;
  without encrypted passphrase **and** the master password, the leak
  yields no plaintext.
- **Leaked secrets volume alone**. The passphrase inside is itself
  encrypted (scrypt + AES-GCM); the master password is required to
  use it.
- **Compromised user account.** Role-based access limits scope.
  Recursive folder write-protect prevents modification of finalized
  subtrees even for higher roles. Logout, password change, and admin
  actions invalidate previously issued tokens through JTI rotation.
  User actions are recorded in the audit log.
- **Brute-force of the master password**. Verification cost is dominated
  by scrypt and the decryption attempt itself; in-process attempt spacing
  acts as an auxiliary defense layer. Default master password
  requirements, together with the computational cost of scrypt-based
  verification, place exhaustive password search beyond practical reach.
- **Unexpected access to the trusted environment.** Shutting down the
  host, restarting the container, or unmounting the cipherdir volume
  immediately makes the encrypted storage inaccessible. Missing or
  corrupted encrypted passphrase data in the secrets volume, as well as
  application crash, has the same effect after a short watchdog delay.
- **Container destruction or environment corruption.** The application
  can be fully restored from the application volumes if both volumes and
  the master password remain available.
- **Loss or corruption of the secrets volume.** If the cipherdir volume,
  passphrase, and master password remain available, the encrypted storage
  can still be mounted directly through `gocryptfs` without the
  application itself.


## What is not protected against

The following risks become relevant only after an attacker gains access
to the trusted environment or host itself. These risks are outside the
protection scope of the application itself and require additional
security controls such as reverse proxies and network filtering.

- **Compromised host**. While mounted, the decrypted view exists inside
  the container; an attacker with root inside the container can read
  plaintext.
- **Malicious extensions.** Extensions are treated as part of the
  application itself and operate inside the same trust boundary.
  Installing extensions requires the same level of access to the
  container as direct modification of the application code, so
  extensions are considered equivalent to modifying the application
  itself.
- **Cipherdir metadata**. The confidentiality guarantees provided by
  `gocryptfs` apply to file contents and names. Certain filesystem
  metadata, including tree shape and timestamps, remains visible by
  design. This may reveal high-level characteristics of the encrypted
  volume, but not plaintext names or contents.
- **Network attacks.** The trusted environment is not assumed to be
  network-safe. DDoS attacks, malicious internal traffic, and abuse of
  application endpoints are considered possible and must be mitigated
  by reverse proxies or traffic filters.


## Cautions

- **Forgotten master password.** There is no recovery path. The master
  password is not stored anywhere; losing it makes the cipherdir
  unrecoverable.
- **Direct modification of the volumes.** Application-managed files and
  metadata should not be modified manually. Direct access to the
  application volumes is intended only for backup, migration, and
  emergency recovery purposes. Manual modifications may break internal
  consistency guarantees and lead to data corruption.


## Cipherdir layout

The `hidden-cipherdir` volume stores user content, revision history,
application metadata, and thumbnails (along with a small amount of
cryptographic overhead introduced by `gocryptfs`):

```sh
 Files and                            File        Application
 thumbnails                           revisions   metadata
 │                                    │           │
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓
```

As a result, the size of the `hidden-cipherdir` volume may exceed the
size of the current file set, particularly in deployments that retain
large numbers of file revisions.


## Backup recommendations

Regular backups of the `hidden-cipherdir` volume are recommended. The
application is designed so that user data is stored on disk only in
encrypted form, so backups can be stored on external or remote systems
without exposing unencrypted file contents. Example tools:

- **Restic** — encrypted, deduplicated backups with snapshot support
- **rsync** — incremental filesystem synchronization

It is also recommended to back up the `hidden-secrets` volume separately
from the `hidden-cipherdir` volume. **The master password must not be
stored together with them.**


## Application updates

Application updates are performed without modifying the application
volumes:

1. Stop and remove the existing container.
2. Download the latest version of the repository.
3. Create a new container using the existing application volumes.

The container contains only the application code and runtime environment.
All encrypted data, metadata, users, and cryptographic material are
stored in the application volumes.

**The application volumes must not be removed, recreated, or modified
during the update process.**


## Project stack

The project uses open source technologies and libraries that are widely
used, and easy to maintain and extend:

- **Python 3.12** — core language
- **FastAPI** — HTTP API
- **Pydantic** — data validation
- **gocryptfs / FUSE** — encrypted filesystem
- **SQLite / aiosqlite** — database
- **SQLAlchemy** — database access
- **Alembic** — database schema migrations
- **cryptography** — encryption primitives
- **PyJWT** — authentication tokens
- **pyotp** — TOTP authentication
- **libmagic / python-magic** — MIME detection
- **Pillow** — image processing
- **psutil** — system and process metrics
- **Uvicorn** — ASGI server
- **unittest** — unit tests


## Security audit

The project is periodically reviewed for security issues in application
code, Python dependencies, and the container image. Audit results are
used to identify and prioritize remediation work, with `CRITICAL` and
`HIGH` severity findings receiving the highest priority. Audit tools:

- **bandit** — static code analysis
- **pip-audit** — dependency vulnerability scanning
- **trivy** — container image vulnerability scanning

Container image scans may report vulnerabilities inherited from the
upstream `python:3.12-slim` base image rather than from application
code or Python dependencies. Such findings are reviewed individually to
determine relevance, exploitability, and remediation options before
changes are planned.


## License

This project is licensed under the **Server Side Public License,
version 1** (`SSPL-1.0`).

You may use, modify, and distribute this software in accordance with
the terms of the SSPL. If you provide the software as a service, you
must make the complete corresponding source code of the service
available, as required by the license.

See [LICENSE](./LICENSE) for full license text.

Copyright (c) 2026 Artem Abramov
