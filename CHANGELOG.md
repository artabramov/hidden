# Changelog

Follow the project's Telegram channel for real-time development updates, release announcements, security advisories, and upcoming events:
[t.me/hiddenupdates](https://t.me/hiddenupdates)

## [0.5.12] - 2026-06-13
- Updated **PyJWT** from **2.12.1** to **2.13.0** to address security vulnerabilities reported by dependency auditing tools.
- Replaced the project license with **GPL-3.0** (SPDX-License-Identifier: GPL-3.0-only), updated license headers across the codebase, and transitioned the project to a fully open-source model.
- Revised **project documentation** and updated comments for better readability and consistency.

## [0.5.11] - 2026-06-07
- Fixed **database corruption on gocryptfs**: SQLite WAL journal mode is incompatible with FUSE-based encrypted filesystems; the shared-memory index file write cycle is not atomic through block-level encryption, causing deterministic corruption. Switched to DELETE journal mode and FULL synchronous level to eliminate the root cause.
- Fixed **database corruption on storage unmount**: SQLAlchemy connections are now disposed before gocryptfs unmount to prevent partially flushed SQLite writes through FUSE.
- Added **database integrity check on storage mount**: runs PRAGMA integrity_check after migrations and aborts mount if the database is corrupted, preventing silent propagation of pre-existing damage.
- Replaced the **cron-based watchdog** with a background sleep-loop and removed the cron daemon and crontab configuration from the container.
- Improved **thumbnail first-load responsiveness**: removed redundant file existence/metadata lookups in the thumbnail retrieval path and enabled CORS preflight caching via **CORS_MAX_AGE_SECONDS**, reducing repeated browser OPTIONS overhead for thumbnail requests.

## [0.5.10] - 2026-05-31
- Added **in-memory LRU thumbnail cache** to avoid repeated reads through the encrypted filesystem; cache size is configurable via the **LRU_CACHE_MAX_BYTES** environment variable and defaults to 50 MB. Cache is invalidated on file operations and storage unmount.
- Added support for **filtering files by tag** in file listings: returns only files matching the given tag.
- Added **tag list endpoint**: returns the most frequently used tags ordered by usage count descending; accepts a single **limit** parameter; responds with tag names and per-tag usage counts.
- Added support for **tokens without expiration** using optional flag, gated behind the **AUTH_ALLOW_PERMANENT_TOKENS** environment variable (disabled by default).
- Changed **recursive write-protection check** to consider only parent folders, not the folder itself; callers now combine it with the folder's own flag for full write-protection logic.
- Changed **file download endpoint** to download any revision by number; revision 0 returns the current version, revision 1 and above return historical revisions.
- Fixed **logging stopping after storage mount**: Alembic logging configuration overwrote the application logger during mount; logging is now preserved after unlocking encrypted storage.

## [0.5.9] - 2026-05-24
- Reduced the default **authentication session lifetime** from 24 hours to 12 hours.
- Updated fields returned by the **health check** response.

## [0.5.8] - 2026-05-17
- Added **per-process master password attempt throttling** for low-level services that verify the master password.
- Added **Cursor rules** for openness, clarity, and security priorities.
- Added **recovery-code-based TOTP reset** with MFA suspension policy on repeated failures.
- Added authenticated **recovery code rotation** with JTI invalidation.
- Fixed an issue where **low-level services** required active database sessions while the cipherdir is unmounted.

## [0.5.7] - 2026-05-10
- Removed **user deletion** operation to preserve audit integrity and maintain consistent user–audit relationships.
- Reviewed the current security model and updated **SECURITY** file.
- Removed the **scripts/** directory and migrated required utilities to **Makefile** targets.
- Added **Alembic**-based database migrations for self-hosted upgrade support.
- Refactored database initialization and schema management logic.
- Added **CORS** middleware for local frontend development environments.
- Refactored test configuration setup to reduce duplication and centralize defaults.
- Added an **LLM**-oriented project overview and architectural context.

## [0.5.6] - 2026-05-03
- Added security audit section with **bandit**, **pip-audit**, and **Trivy**.
- Added an **OWASP**-based self-assessment.
- Added **counters** for folders, files, and comments, along with **latest revision number** for files.
- Added file **tags** and **comments**.
- Added **image rotation** and **image flip** operations for image files, with automatic revision creation and thumbnail regeneration.
- Added **file edit** operation for text files, with automatic revision creation.
- Added a **metrics endpoint** with runtime, system, process, and SQLite diagnostics.

## [0.5.5] - 2026-05-03
- Added an **image repository** for image-related operations.
- Added **file upload support**, including revision creation, thumbnail generation, and proper rollback when an upload operation fails.
- Added the **is_write_protected** flag to protect folders from accidental modification, including inherited checks across all parent folders.
- Added **select_parent_chain** to the ORM repository for CTE-based parent-chain queries.

## [0.5.4] - 2026-04-19
- Removed ability for clients to control JWT lifetime. Token TTL is now defined server-side through **AUTH_TOKEN_TTL_SECONDS** environment variable.
- Added **registration request throttling** to reduce username enumeration surface.
- Added strict **JTI invalidation on password change**, immediately revoking all previously issued tokens.
- Introduced **variables subsystem** for extension data storage.

## [0.5.3] - 2026-04-12
- Removed **CLI** and replaced it with standalone scripts located in **scripts/**.
- Introduced **Pydantic validation errors** (422) usable at the service layer for input validation.
- Reworked and unified the **hook and event system** used by extensions.
- Added **ADR-XX** comments across the codebase and a central ADR registry.
- Introduced **lockdown mode** independent of cipherdir, allowing the application to switch into maintenance mode.

## [0.5.2] - 2026-04-05
- Reworked the automatic unmount **watchdog**: it now verifies the presence of the encrypted passphrase and the availability of the application, and immediately unmounts on any inconsistency.
- Implemented **encryption of the gocryptfs passphrase**, introducing a second factor: mounting now requires both access to the encrypted passphrase and the password needed to decrypt it.
- Introduced a **CLI** for direct interaction with the system, allowing direct work with the cipherdir in emergency scenarios.
- Removed **Restic** from the base installation; it can be used on the host system for backing up the cipherdir if needed.
- Performed general naming cleanup and minor internal refactoring.

## [0.5.1] - 2026-03-22
- Updated the **extensions** structure and revised the hook system.
- Added cron-based jobs for **Restic** backups.
- Added minor improvements and updated documentation.

## [0.5.0] - 2026-03-15
- **Rewrote the application from scratch**, establishing a new architecture and resetting the codebase.
- Introduced **SSPL license** (SPDX-License-Identifier: SSPL-1.0) for the project.
- Added **Restic** integration for encrypted backups of the storage repository.
- Reworked and optimized **entrypoint**, simplifying initialization logic and improving first-boot handling.
- Updated **.env.example** to reflect the current environment configuration and newly introduced variables.
- Refactored the internal application structure and reorganized the layout of stored data.
