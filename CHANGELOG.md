# Changelog

## [0.6.1] - 2026-10-18
- Added **VS Code** launch configurations for viewing test **coverage** and running **flake8**.
- Updated and expanded the **GitHub Pages** documentation.
- Added **CONTRIBUTING.md** to clarify the project's contribution policy.

## [0.6.0] - 2026-10-18
- **Rewrote the application from scratch**, replacing the built-in file repository with S3-compatible storage and resetting the codebase.
- Added **VersityGW** as the S3-compatible gateway. It provides the S3 API, IAM, and WebGUI, while **FastAPI** manages the **gocryptfs** lifecycle through the OpenAPI interface. The S3 API listens on port **9000** and the WebGUI on port **8080**; the management API remains on port **8081**.
- Stored S3 objects and IAM state as POSIX files and directories inside the **gocryptfs** cipherdir, so the encrypted volume can be mounted and recovered directly with gocryptfs without the application.
- Added management operations to **initialize**, **mount**, and **unmount** encrypted storage, **rotate the master password**, **reveal** the gocryptfs passphrase and VersityGW root credentials, and **reset** storage to an uninitialized state. Initialization generates the gocryptfs passphrase, encrypts it with the **master password**, and creates the VersityGW root credentials.
- Updated the **health check** to report whether the cipherdir is initialized and mounted, whether VersityGW credentials exist and the gateway is running, and whether the watchdog is alive.
- Reworked the **watchdog** to stop **VersityGW** and unmount the decrypted filesystem when the encrypted passphrase is missing or empty or the application process is not running. The parent of the secrets volume is bind-mounted with **rslave** propagation, so unmounting the removable media on the host is visible inside the container.
- Replaced the project license with **Apache-2.0** (SPDX-License-Identifier: Apache-2.0).

## [0.5.17] - 2026-07-19
- Updated **pillow** from **12.2.0** to **12.3.0** to address security vulnerabilities reported by dependency auditing tools.
- Made small documentation improvements.

## [0.5.16] - 2026-07-05
- Updated **pydantic-settings** from **2.13.1** to **2.14.2** to address security vulnerabilities reported by dependency auditing tools.

## [0.5.15] - 2026-06-28
- Updated **python-multipart** from **0.0.27** to **0.0.31** to address security vulnerabilities reported by dependency auditing tools.

## [0.5.14] - 2026-06-21
- Added **decompression bomb protection** for image processing: all image manipulation operations (rotate, flip, thumbnail) now check the pixel count against the new **IMAGE_MAX_PIXELS** configuration value (default: **50 MP**) immediately after opening the image header and before decoding any pixel data. Images exceeding the limit are rejected.
- Updated **cryptography** from **46.0.7** to **48.0.1** to address security vulnerabilities reported by dependency auditing tools.

## [0.5.13] - 2026-06-14
- Added the `develop` **Makefile target** and marked it as phony; development-only Git and OpenSSH client tooling is now installed on demand.

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
