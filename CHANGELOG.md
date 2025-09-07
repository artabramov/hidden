# Changelog

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
