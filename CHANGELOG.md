# Changelog

### [0.1.2] - 2025-08-17
- Tuned parameters for **safer, more accurate indexing** of encrypted fields.
- Updated documentation and **open-sourced the code** (repo now public).
- Changed license: applied a **non-commercial software license** (source-available; no commercial use).

### [0.1.1] - 2025-08-10
- Optimized **chunk sizes** to **1 MiB** for all major file operations including **upload**, **copy** and **read**, which reduces the number of syscalls and improves throughput for large files.  
- Refined **shard size** selection algorithm — now uses a more granular scale from **1 KB** up to **512 MB**, ensuring better balance between the number of shards and their size for different file sizes.
- Improved initial **data validation** for forms on the frontend.

### [0.1.0] - 2025-08-03
- Added default **frontend** built with **React** and **Bootstrap**, including registration, authorization, login, profile editing, password change, and management of users, collections, and documents.
- Added interface for managing the **secret key**.

### [0.0.21] - 2025-07-27
- Improved annotation for **Public API**.

### [0.0.20] - 2025-07-20
- Removed full links to **userpics** and **thumbnails**. Instead, only the filenames are returned.

### [0.0.19] - 2025-07-13
- Refactored **LRU** to support caching of files stored in sharded form, allowing explicit insertion of decrypted data and retrieval by **key** rather than file paths.

### [0.0.18] - 2025-07-06
- Added **split** and **merge** methods for handling binary file sharding and reconstruction.
- Introduced logic to determine optimal shard size for splitting files into up to 5 parts.
- Added mechanism to randomly **shuffle shards**. This masks their original creation order by maximizing timestamp noise.
- Added splitting of encrypted data into random shards and their mixing during upload.
- Added reverse recovery and decryption of the original data from separate shards during download.
- Added a configuration setting to set the **intensity of shard mixing**.

### [0.0.17] - 2025-06-29
- Added **tag list** router to retrieve a list of document tags grouped by name.
- Improved sorting for **document list** and **collection list**.

### [0.0.16] - 2025-06-22
- Added **value_empty** error type for handling validation of missing values.
- Set **setting_value** to allow undefined text length.

### [0.0.15] - 2025-06-15
- Limited **create_thumbnail** to merge a maximum of 2 images, down from 4.
- Changed default width and height for **userpics** and **thumbnails**.

### [0.0.14] - 2025-06-08
- Fixed an issue with the **collection model** thumbnail path definition.
- Added **collection library** for complex operations on collections.
- Added **create_thumbnail** to the **collection library** to generate collection thumbnails by merging 1 to 4 document thumbnails.

### [0.0.13] - 2025-06-01
- Enabled automatic collection **thumbnail generation** when a document is uploaded, updated, or deleted.

### [0.0.12] - 2025-05-25
- Added a **documents_count** field to the **collection model** to store the number of documents in a collection.
- Added **PostgreSQL** triggers to automatically maintain **documents_count** in the **collections** table when documents are inserted, updated, or deleted.
- Prevented **SQLAlchemy** from writing to **documents_count**, ensuring it remains read-only at the ORM level.

### [0.0.11] - 2025-05-18
- Split the document upload endpoint into two separate routes: one with the collection ID passed in the path, and one without the collection ID.

### [0.0.10] - 2025-05-11
- Added **uptime** helper and included app uptime in telemetry output.
- Introduced **serial** number generation and included it in telemetry data.
- Added **secret key** creation date to the **secret key** API endpoint.
- Improved handling of HTTP errors **403**, **404**, and **423** with proper **CORS** headers.

### [0.0.9] - 2025-05-09
- Added **CORS** support for the JavaScript frontend with a different origin.
- Integrated **psutil** package for monitoring system-level metrics.
- Introduced **/telemetry** endpoint to provide basic system information.

### [0.0.8] - 2025-05-04
- Added video thumbnail generation with the new **video helper**.
- Enabled uploading documents to specific collections.
- Improved docstrings, increased unit test coverage, and renamed several helper functions.

### [0.0.7] - 2025-05-01
- Added static routers for serving document, thumbnail, and userpic files.
- Introduced **_meta** classes and a **MetaMixin** to support flexible metadata handling.

### [0.0.6] - 2025-04-27
- Added support for uploading and managing **userpics** through the API.
- Implemented input validators for **username**, **password**, **user summary**, and **TOTP codes**.
- Introduced an **image helper** utility for resizing, validating, and transforming image files.

### [0.0.5] - 2025-04-20
- Implemented role-based authentication with **reader**, **writer**, **editor**, and **admin** roles.
- Added **LRU** cache to optimize static file access with bounded memory usage.
- Introduced **html** directory to serve frontend static assets.
- Added API routers for managing **token**, **user**, **secret**, and **lock** entities.
- Implemented support for secure token issuance and invalidation workflows.

### [0.0.4] - 2025-04-06
- Enabled automatic **secret.key** generation during Docker image builds.
- Introduced persistent **secret.key** generation during application startup.
- Added a universal handler for bidirectional encryption of numeric, string, and binary data using the **AES** algorithm and a unique secret key.
- Enabled encryption for all uploaded user files.
- Enabled encryption for all sensitive data stored in the database.
- Added **sort helper** to generate sortable numeric indexes for encrypted values.

### [0.0.3] - 2025-03-30
- Introduced **timed** decorator to measure and log execution time of async functions.
- Added **CacheManager** for managing SQLAlchemy entities using Redis.
- Added **EntityManager** to handle ORM operations backed by PostgreSQL.
- Added **FileManager** module to centralize and simplify file and directory operations.
- Implemented **hook** module for internal event handling via trigger-like mechanisms.
- Implemented a unified **Repository** layer combining cache and database logic.

### [0.0.2] - 2025-03-22
- Integrated Prometheus exporters for **node**, **PostgreSQL**, and **Redis** monitoring.
- Exposed ports **9100**, **9187**, and **9121** for Prometheus metric scraping.
- Added **Sphinx** based documentation accessible at the **/autodoc** endpoint.
- Enabled automatic generation of project documentation on application startup.

### [0.0.1] - 2025-03-09
- Created initial **FastAPI** application with a structured project layout.
- Added **launch.json** and **settings.json** for Visual Studio Code integration.
- Introduced **Makefile**, **Dockerfile**, and **entrypoint.sh** for streamlined development and deployment.
- Added core modules: **config**, **context**, **postgres**, **redis**, and **log**.
- Pinned Python package versions for reproducible builds.
