# Changelog

### [0.0.11] - 2025-05-18
- Changed default width and height for `userpics` and `thumbnails`.
- Fixed an issue with the `collection model` thumbnail path definition.
- Added `collection library` for complex operations on collections.
- Added `create_thumbnail` to the `collection library` to generate collection thumbnails by merging 1 to 4 document thumbnails.
- Enabled automatic collection thumbnail generation when a document is uploaded, updated, or deleted.
- Added a `documents_count` field to the `collection model` to store the number of documents in a collection.
- Added `PostgreSQL` triggers to automatically maintain `documents_count` in the `collections` table when documents are inserted, updated, or deleted.
- Prevented `SQLAlchemy` from writing to `documents_count`, ensuring it remains read-only at the ORM level.
- Split the document upload endpoint into two separate routes: one with the collection ID passed in the path, and one without the collection ID.

### [0.0.10] - 2025-05-11
- Added `uptime` helper and included app uptime in telemetry output.
- Introduced `serial` number generation and included it in telemetry data.
- Added `secret key` creation date to the `secret key` API endpoint.
- Improved handling of HTTP errors `403`, `404`, and `423` with proper `CORS` headers.

### [0.0.9] - 2025-05-09
- Added `CORS` support for the JavaScript frontend with a different origin.
- Integrated `psutil` package for monitoring system-level metrics.
- Introduced `/telemetry` endpoint to provide basic system information.

### [0.0.8] - 2025-05-04
- Added video thumbnail generation with the new `video helper`.
- Enabled uploading documents to specific collections.
- Improved docstrings, increased unit test coverage, and renamed several helper functions.

### [0.0.7] - 2025-05-01
- Added static routers for serving document, thumbnail, and userpic files.
- Introduced `*_meta` classes and a `MetaMixin` to support flexible metadata handling.

### [0.0.6] - 2025-04-27
- Added support for uploading and managing user profile pictures through the API.
- Implemented input validators for username, password, user summary, and TOTP codes.
- Introduced an image helper utility for resizing, validating, and transforming image files.

### [0.0.5] - 2025-04-20
- Implemented role-based authentication with `reader`, `writer`, `editor`, and `admin` roles.
- Added `LRU` cache to optimize static file access with bounded memory usage.
- Introduced `html` directory to serve frontend static assets.
- Added API routers for managing `token`, `user`, `secret`, and `lock` entities.
- Implemented support for secure token issuance and invalidation workflows.

### [0.0.4] - 2025-04-06
- Introduced `timed` decorator to measure and log execution time of async functions.
- Enabled automatic `secret.key` generation during Docker image builds.
- Added `FileManager` module to centralize and simplify file and directory operations.
- Implemented `hook` module for internal event handling via trigger-like mechanisms.

### [0.0.3] - 2025-03-30
- Added `CacheManager` for managing SQLAlchemy entities using Redis.
- Added `EntityManager` to handle ORM operations backed by PostgreSQL.
- Implemented a unified `Repository` layer combining cache and database logic.
- Added `sort helper` to generate sortable numeric indexes for encrypted values.
- Introduced persistent `secret.key` generation during application startup.

### [0.0.2] - 2025-03-22
- Integrated Prometheus exporters for `node`, `PostgreSQL`, and `Redis` monitoring.
- Exposed ports `9100`, `9187`, and `9121` for Prometheus metric scraping.
- Added `Sphinx`-based documentation accessible at the `/autodoc` endpoint.
- Enabled automatic generation of project documentation on application startup.

### [0.0.1] - 2025-03-09
- Created initial `FastAPI` application with a structured project layout.
- Added `launch.json` and `settings.json` for Visual Studio Code integration.
- Introduced `Makefile`, `Dockerfile`, and `entrypoint.sh` for streamlined development and deployment.
- Added core modules: `config`, `context`, `postgres`, `redis`, and `log`.
- Pinned Python package versions for reproducible builds.
