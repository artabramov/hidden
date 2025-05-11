# Changelog

### [0.0.10] - 2025-05-11
- Added `uptime` helper and included app uptime in telemetry data.
- Added `serial` number generation and included it in telemetry data.
- Added `secret key` creation date to secret key retrieval router.
- Added special handling for `403`, `423`, `404` errors with `CORS` headers.

### [0.0.9] - 2025-05-09
- Added `CORS` support for the `JavaScript` frontend with a different `origin`.
- Added `psutil` package for process and system monitoring.
- Added `telemetry` endpoint that returns basic system information.

### [0.0.8] - 2025-05-04
- Added `video helper` to generate thumbnails from uploaded video files.
- Added support for uploading documents to a specified `collection`.
- Added updates to `docstrings`, unit tests, and renamed several functions.

### [0.0.7] - 2025-05-01
- Added static routers for serving `document`, `thumbnail`, and `userpic`.
- Added `*_meta` classes and a `meta mixin` for handling extra metadata.

### [0.0.6] - 2025-04-27
- Added support for uploading `userpics` to user profiles via the API.
- Added `validators` for `username`, `password`, `user summary`, and `totp`.
- Added `image helper` to resize, validate, and transform image files.

### [0.0.5] - 2025-04-20
- Added role-based `auth` with `reader`, `writer`, `editor`, and `admin` roles.
- Added `LRU` cache for efficient loading of static files with limits.
- Added `html` directory to serve static content for the frontend.
- Added routers and schemas for `token`, `user`, `secret`, and `lock`.
- Added `token retrieval` and `token invalidation` functionality.

### [0.0.4] - 2025-04-06
- Added `timed` decorator to log async function execution durations.
- Added `secret key` generation during image build via `Dockerfile`.
- Added `file manager` to simplify file and directory operations.
- Added `hook` module and defined triggers for internal event handling.

### [0.0.3] - 2025-03-30
- Added `cache manager` to manage SQLAlchemy entities in Redis cache.
- Added `entity manager` for managing Postgres-based SQLAlchemy records.
- Added `repository` combining entity and cache management logic.
- Added `sort helper` for generating sortable numeric string indices.
- Added `secret.key` and generator that runs at application startup.

### [0.0.2] - 2025-03-22
- Added metric exporters for `node`, `postgres`, and `redis` services.
- Added ports `9100`, `9187`, and `9121` for Prometheus metrics scraping.
- Added `Sphinx` documentation accessible at the `/autodoc` endpoint.
- Added automatic documentation generation on application startup.

### [0.0.1] - 2025-03-09
- Created basic `FastAPI` application and directories for static files.
- Added `launch.json` and `settings.json` for Visual Studio Code.
- Added `Makefile`, `Dockerfile`, `entrypoint.sh`, and pinned versions.
- Added `config` module to read values from the `.env` file.
- Added `context` module to provide values passed within the application.
- Added `encrypt_helper` module for encryption and hashing.
- Added `redis` and `postgres` modules to connect to database and cache.
- Added `log` module to handle log messages.
