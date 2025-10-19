# Changelog

## [0.2.16] - 2025-10-19
- Updated module docstrings; Sphinx Markdown documentation is now bundled under **docs/md**.
- Updated **security scan** and regenerated **SECURITY_SCAN.md**.

## [0.2.15] - 2025-10-18
- Major refactor: renamed collections to **folders** and documents to **files** (routers, schemas, models, hooks, and configuration were adjusted accordingly).
- Removed redundant **logging**.

## [0.2.14] - 2025-10-18
- Added **static HTML** hosting: the backend now serves files from **/hidden/html** (ships with a placeholder **index.html**); a custom frontend can be placed there.
- **Enabled CORS**: responses now include headers permitting cross-origin requests from external origins.
- Added **telemetry** endpoint (admin-only). Returns runtime metrics including app version, Python interpreter details, timestamp and timezone, SQLite version and size, Redis version and memory, OS/platform details, and CPU/memory/disk stats.

## [0.2.13] - 2025-10-12
- Implemented **document tagging**: introduced endpoints to add and remove tags from individual documents, with input validation and consistent responses.
- Enhanced document listing: added **tag-based filtering** to retrieve documents by tag value.
- Document payloads updated a **document_tags** array is returned in both detail and list responses to expose assigned tags.

## [0.2.12] - 2025-10-11
- Minor configuration fixes.
- Updated **security scan** report with latest audit results and regenerated **SECURITY_SCAN.md**.

## [0.2.11] - 2025-10-05
- Increased overall unit test coverage to **83%**.
- Updated **security scan** report with latest audit results and regenerated **SECURITY_SCAN.md**.

## [0.2.10] - 2025-10-04
- Secrets volume is renamed to **hidden-secrets**.
- Secret key file is renamed to **gocryptfs.key**.
- Updated application code and unit tests to use the new paths and environment variable names.
- Minor docs and config tweaks to reflect the new secret layout.

## [0.2.9] - 2025-10-04
- Added **readonly** property for collections: when enabled, documents inside them cannot be modified; added **value_readonly** error on modification attempts.
- Added **Sphinx** documentation generation through the **Makefile apidoc** target; runs **sphinx-apidoc** over app (excluding tests) and produces Markdown output.
- Moved installation of security-scan packages from the **Dockerfile** to the **Makefile scan** target.
- Pruned **requirements** to remove redundant dependencies.

## [0.2.8] - 2025-09-28
- Added **Makefile scan** target that runs vulnerability scans (**pip-audit**, **bandit**) and generates the report **SECURITY_SCAN.md**.
- Security fixes: bumped **aiohttp** (3.12.x), **Starlette** (0.47.2), **Pillow** (11.3.0).
- Increased overall unit test coverage to **82%**.

## [0.2.7] - 2025-09-27
- Fixed minor issues in the **pydantic models**, improving validation and error messages.
- Increased overall unit test coverage to **81%**.
- Minor fixes and improvements.

## [0.2.6] - 2025-09-21
- Added **collection deletion** endpoint; removes all documents (thumbnails, revisions, head files) with a per-collection **write** lock, performs best-effort filesystem cleanup (missing files ignored), and purges LRU cache.
- Fixed **delete** method in **EntityManager**: now merges the entity into the current session before deletion, preventing SQLAlchemy InvalidRequestError.
- Added **short-circuit on checksum match** for uploads: if the uploaded content equals the current head, skip DB/FS changes and return **201 Created** with the revision unchanged.
- Added **collection listing** endpoint with filtering (creator, timestamps, readonly, name), pagination, and ordering.
- Added **VS Code configurations** for development workflow: flake8 linting, running tests with coverage, and generating coverage reports.

## [0.2.5] - 2025-09-20
- Unified thumbnail path handling via **thumbnail mixin**; applied to document and user thumbnails.
- Added document **thumbnail retrieval** endpoint with LRU caching.
- Added conditional response **304 Not Modified** to thumbnail endpoints to avoid redundant data traffic.
- Added **document deletion** endpoint with per-document file lock; removes thumbnail, revisions, and head; purges LRU.
- Added global **document listing** endpoint (cross-collection) with filtering, pagination, and ordering.
- Added collection-level **read–write lock** (RWLock) with hierarchical coordination above per-file locks: file operations acquire **read**, directory operations acquire **write**; prevents races and blocks concurrent file operations (single-process scope).
- Added **collection update** endpoint (rename and summary); performs atomic directory rename.
- Standardized **NOTE** comments: each begins with a scope cue; use a repo-wide search for "NOTE" to find design/behavior caveats.
- Minor fixes and improvements.

## [0.2.4] - 2025-09-14
- Improved **revision management** through model adjustment and added revision data to document responses.
- Added **file download** endpoint to retrieve the document file (latest or any specific historical revision) within its collection.
- Added **document update** endpoint: atomic rename/move and summary update in a single transaction; deterministic per-path dual locks to prevent AB–BA deadlocks; strict DB/FS conflict checks and clean error codes.
- Switched **userpic** and **document thumbnail** filenames to UUIDs for simplicity and clarity.
- Added **hash verification** for static file responses (thumbnails, document files). Additionally, the hash is included in the **ETag header**.
- Minor fixes and improvements.

## [0.2.3] - 2025-09-13
- Added **locks** on file operations to avoid race conditions (within one process).
- Added **file upload** endpoint: per-document locks to prevent races; on update the previous head is copied into a revision, the new file atomically replaces the head with safe rollback on commit failure; thumbnails are regenerated under the same lock.
- Added **thumbnail generation** for image files.
- Added **collection retrieval** endpoint that returns collection data by its ID.
- Added **document retrieval** endpoint that returns document data by its ID.
- **Hook execution** is wrapped in a try-except so that the main code does not crash when there are errors in custom hooks.
- Minor fixes and improvements.

## [0.2.2] - 2025-09-07
- Added content-based **MIME detection** using libmagic and filetype; filename-extension detection remains a last resort.

## [0.2.1] - 2025-09-07
- Added **collection creation**. Each collection now has its own home in the documents directory — folders are created automatically to keep files strictly organized.

## [0.2.0] - 2025-09-06
- Moved encryption to the OS layer via **gocryptfs** (FS-level encryption; app works with the cleartext mount).
- Extracted the **secret key** and **encrypted data** into Docker volumes.
- Added a **watchdog** to hot mount/unmount the cleartext view based on secret-key presence — no app restart required.
- Replaced **PostgreSQL** with **SQLite**.
- Removed all exporters except **node_exporter**.
- Rewrote the application core (managers, helpers, schemas, models).
- Updated **LRU**: configurable total size in **bytes** (not item count) and a per-item size cap.
- Rewrote routers for **user management** and **authentication**.

## [0.1.3] - 2025-08-23
- Minor fixes and improvements.

## [0.1.2] - 2025-08-17
- Tuned parameters for **safer and more accurate indexing** of encrypted fields.
- Updated documentation and **opened the repository for public access**.
- Changed license to a **non-commercial software license** (source-available, no commercial use).

## [0.1.1] - 2025-08-10
- Set **chunk size** to 1 MiB for all major file operations (upload, copy, read), reducing the number of system calls and improving throughput for large files.
- Refined **shard size** selection algorithm with a scale from 1 KB to 512 MB, providing better balance between shard count and shard size.
- Improved validation.

## [0.1.0] - 2025-07-27
- Improved annotation for **Public API**.

## [0.0.18] - 2025-07-20
- Removed full links to **userpics** and **thumbnails**. Only filenames are now returned.

## [0.0.17] - 2025-07-13
- Refactored **LRU** cache to support files stored in sharded form, with insertion of decrypted data and retrieval by key instead of file paths.
- Added split and merge methods for handling **file sharding** and reconstruction.
- Introduced logic to determine optimal **shard size** for splitting files into up to 5 parts.
- Added random **shuffling of shards** to mask original order using timestamp noise.
- Added **splitting** of encrypted data into random shards and mixing during upload.
- Added **recovery** and decryption of original data from shards during download.
- Added configuration option to control shard **mixing intensity**.

## [0.0.16] - 2025-06-29
- Added **tag list** endpoint to retrieve document tags grouped by name.
- Improved **sorting** for document lists and collection lists.

## [0.0.15] - 2025-06-22
- Added **value_empty** error type for handling validation of missing values.
- Set **setting_value** to allow undefined text length.

## [0.0.14] - 2025-06-15
- Limited **create_thumbnail** to merge a maximum of 2 images, down from 4.
- Changed default width and height for **userpics** and **thumbnails**.

## [0.0.13] - 2025-06-08
- Fixed an issue with the **collection model** thumbnail path definition.
- Added **collection library** for complex operations on collections.
- Added **create_thumbnail** to the **collection library** to generate collection thumbnails by merging 1 to 4 document thumbnails.

## [0.0.12] - 2025-06-01
- Enabled automatic collection **thumbnail generation** when a document is uploaded, updated, or deleted.

## [0.0.11] - 2025-05-25
- Added a **documents_count** field to the **collection model** to store the number of documents in a collection.
- Added **PostgreSQL** triggers to automatically maintain **documents_count** in the **collections** table when documents are inserted, updated, or deleted.
- Prevented **SQLAlchemy** from writing to **documents_count**, ensuring it remains read-only at the ORM level.

## [0.0.10] - 2025-05-18
- Split the document upload endpoint into two separate routes: one with the collection ID passed in the path, and one without the collection ID.

## [0.0.9] - 2025-05-11
- Added **uptime** helper and included app uptime in telemetry output.
- Introduced **serial** number generation and included it in telemetry data.
- Added **secret key** creation date to the **secret key** API endpoint.
- Improved handling of HTTP errors **403**, **404**, and **423** with proper **CORS** headers.

## [0.0.8] - 2025-05-09
- Added **CORS** support for the JavaScript frontend with a different origin.
- Integrated **psutil** package for monitoring system-level metrics.
- Introduced **/telemetry** endpoint to provide basic system information.

## [0.0.7] - 2025-05-04
- Added video thumbnail generation with the new **video helper**.
- Enabled uploading documents to specific collections.
- Improved docstrings, increased unit test coverage, and renamed several helper functions.

## [0.0.6] - 2025-05-01
- Added static routers for serving document, thumbnail, and userpic files.
- Introduced **_meta** classes and a **MetaMixin** to support flexible metadata handling.

## [0.0.5] - 2025-04-27
- Added support for uploading and managing **userpics** through the API.
- Implemented input validators for **username**, **password**, **user summary**, and **TOTP codes**.
- Introduced an **image helper** utility for resizing, validating, and transforming image files.

## [0.0.4] - 2025-04-20
- Implemented role-based authentication with **reader**, **writer**, **editor**, and **admin** roles.
- Added **LRU** cache to optimize static file access with bounded memory usage.
- Introduced **HTML** directory to serve frontend static assets.
- Added API routers for managing **token**, **user**, **secret**, and **lock** entities.
- Implemented support for secure token issuance and invalidation workflows.
- Enabled automatic **secret.key** generation during Docker image builds.
- Introduced persistent **secret.key** generation during application startup.
- Added a universal handler for bidirectional encryption of numeric, string, and binary data using the **AES** algorithm and a unique secret key.
- Enabled encryption for all uploaded user files.
- Enabled encryption for all sensitive data stored in the database.
- Added **sort helper** to generate sortable numeric indexes for encrypted values.

## [0.0.3] - 2025-03-30
- Introduced **timed** decorator to measure and log execution time of async functions.
- Added **CacheManager** for managing SQLAlchemy entities using Redis.
- Added **EntityManager** to handle ORM operations backed by PostgreSQL.
- Added **FileManager** module to centralize and simplify file and directory operations.
- Implemented **hook** module for internal event handling via trigger-like mechanisms.
- Implemented a unified **Repository** layer combining cache and database logic.

## [0.0.2] - 2025-03-22
- Integrated Prometheus exporters for **node**, **PostgreSQL**, and **Redis** monitoring.
- Exposed ports **9100**, **9187**, and **9121** for Prometheus metric scraping.
- Added **Sphinx** based documentation accessible at the **/autodoc** endpoint.
- Enabled automatic generation of project documentation on application startup.

## [0.0.1] - 2025-03-09
- Created initial **FastAPI** application with a structured project layout.
- Added **launch.json** and **settings.json** for Visual Studio Code integration.
- Introduced **Makefile**, **Dockerfile**, and **entrypoint** for streamlined development and deployment.
- Added core modules: **config**, **context**, **postgres**, **redis**, and **log**.
- Pinned Python package versions for reproducible builds.
