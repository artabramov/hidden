- [Architecture overview](#architecture-overview)
- [app.app](#appapp)
- [app.error](#apperror)
- [app.auth](#appauth)

## Architecture overview

By default the application runs in a Docker container and can be deployed anywhere Docker (or a compatible OCI runtime) is available. All data operations go exclusively through the public REST API. Three volumes are exposed:

1. `hidden-secrets` — stores the master secret key (gocryptfs passphrase). It is generated randomly during installation and is required for every operation.
2. `hidden-data` — the encrypted payload (gocryptfs cipher directory). Can be used for data migration, backups, or emergency recovery outside the application (the secret key is required in all cases).
3. `hidden-logs` — application logs (typically used only for development).

The application is divided into several layers, each responsible for a specific aspect of the system: 

1. `Routing` — the single entry point to data via the Public API. Includes FastAPI routers, Pydantic validation schemas, and authentication/authorization.
2. `Business Logic` — business rules and high-level logic organized per router, with hooks exposed for add-ons.
3. `Extensible Core` — configuration, repository layer, file locking, and logging; manages add-on loading and enforces the presence of the master secret key.
4. `Data Access Layer` — four managers for low-level operations: database, cache, filesystem, and encrypted storage.
5. `Storage Layer` — the gocryptfs cipher directory for physical storage of files, revisions, and thumbnails; Redis and an LRU cache speed up database and filesystem operations.

```
       External                           Docker Container
┌────────────────────┐       ┌───────────────────────────────────────┐
│     Public API     │───────│                Routing                │
└────────────────────┘       └───────────────────────────────────────┘
                                                 │
                             ┌───────────────────────────────────────┐
                             │             Business Logic            │
                             └───────────────────────────────────────┘
                                                 │
                             ┌────────────────────────┬──────────────┐
                             │          Core          │    Addons    │
                             └────────────────────────┴──────────────┘
        Volumes                                  │
┌────────────────────┐       ┌───────────────────────────────────────┐
│     Secret Key     │- - - -│              Data Access              │
└────────────────────┘       └───────────────────────────────────────┘
                                          │                   │
┌────────────────────┐       ┌───────────────────────┐ ┌─────────────┐
│   Encrypted Data   │- - - -│   Protected Storage   │ │    Cache    │
└────────────────────┘       └───────────────────────┘ └─────────────┘
```


## app.app

Main application assembly for Hidden: builds the FastAPI app, wires core services, mounts routers, sets CORS/OpenAPI, and defines global lifecycle, middleware, and exception handling. Each request receives a UUID, precise timing/logging, lockdown and gocryptfs-key checks, and consistent JSON errors.

**Responsibilities**

- Load configuration and initialize core services (DB, Redis, hooks, logger, file manager, LRU).
- Mount all public routers (auth, users, folders, files, tags, thumbnails, telemetry).
- Expose OpenAPI under `/api/v1` with persisted auth and request-duration display.
- Enforce global middleware: request IDs, timing, DEBUG request logs, lockdown/key checks, `X-Request-ID`.
- Centralize exception handling with stable JSON shape and correct status codes.
- Serve a static HTML frontend and files from the configured directory.
- Provide in-process locking primitives (folder/file) and clear locks/LRU when needed.

**Initialization & Lifespan**

- On startup (`lifespan`):
  - `app.state.config` — loaded via `get_config()`.
  - `SessionManager` + `init_database()`; `RedisClient` + `init_cache()`.
  - `init_hooks(app)`, `init_logger(app)`.
  - `FileManager(config)` as `app.state.file_manager`.
  - `LRU` cache for thumbnails/userpics (`app.state.lru`).
  - Force-disable lockdown: delete lock file if it exists.
  - Per-process locks: `folder_locks: Dict[key, RWLock]`, `file_locks: Dict[key, asyncio.Lock]`.
- On shutdown: dispose async engine, close Redis.

**Routers mounted**

- Auth & tokens: `user_login`, `token_retrieve`, `token_invalidate`.
- Users: `user_register`, `user_role`, `user_password`, `user_select`, `user_update`, `user_delete`, `user_list`, `userpic_upload/delete/retrieve`.
- Folders: `folder_insert/select/update/delete/list`.
- Files: `file_upload/download/select/update/delete/list`, `thumbnail_retrieve`.
- Tags: `tag_insert`, `tag_delete`.
- Telemetry: `telemetry_retrieve`.

**OpenAPI & CORS**

- Root path: `/api/v1`, title: “Hidden — REST over gocryptfs”.
- Swagger UI options: persisted auth, request duration, “Try it out”.
- CORS middleware: `*` origins/methods/headers, credentials allowed.

**Static hosting**

- Catch-all route serves the main HTML (`HTML_PATH`/`HTML_FILE`) or a requested file if present; returns `404` otherwise.

**Middleware behavior**

- Generate/reuse `X-Request-ID` (UUID) per request; store start time; attach `LoggerAdapter` with the request UUID.
- DEBUG log on receive/send with elapsed time.
- Lockdown check: if global lock file exists → clear LRU, return `423 Locked`.
- gocryptfs-key check:
  - Missing passphrase file → clear LRU, return **498** (`gocryptfs_key_missing`).
  - Invalid/length mismatch → clear LRU, return **499** (`gocryptfs_key_invalid`).
- On success: append `X-Request-ID` header to the response.

**Exception handling**

- `RequestValidationError` / `pydantic.ValidationError` → **422** with `.errors()` payload; DEBUG log.
- Crypto errors (`InvalidTag`, `InvalidSignature`, `InvalidKey`, `UnsupportedAlgorithm`, `AlreadyFinalized`, `NotYetFinalized`, `AlreadyUpdated`, `InternalError`) → clear LRU, **499** `gocryptfs_key_invalid`.
- Raised `HTTPException` → passthrough status/detail.
- Any other exception → **500** `server_error`.
- Non-validation failures logged at ERROR with stack trace; always return JSON and set `X-Request-ID`.

**Locking & deadlocks**

- Folder/file locks are per-process (not shared across workers).
- Acquire in order: **folder → files**. When locking multiple files, **sort keys** to avoid AB-BA deadlocks.

**Special status codes**

- **423** — application lockdown.
- **498** — gocryptfs key missing.
- **499** — gocryptfs key invalid.


## app.error

Centralized error definitions and a thin HTTPException wrapper that guarantees a uniform response shape across the API. The module standardizes error codes, locations, and messages so clients can handle failures consistently—mirroring Pydantic’s validation-error format. It defines a concise taxonomy (authentication, authorization, value/file errors, lock/server/key states) and exposes a single helper E to raise structured exceptions.

**Responsibilities**

- Define canonical error constants and locations used throughout the API.
- Provide custom HTTP status codes for gocryptfs key states (`498`, `499`).
- Offer a unified exception helper (`E`) that emits details in Pydantic-like form:
`[{ "loc": [...], "input": "...", "type": "..." }]`.
- Ensure consistent error handling across routers, managers, and helpers.

**Key components**

```python
class E(HTTPException)
```

**Locations**

| Constant     | Value  |
|--------------|--------|
| `LOC_HEADER` | header |
| `LOC_COOKIE` | cookie |
| `LOC_PATH`   | path   |
| `LOC_QUERY`  | query  |
| `LOC_BODY`   | body   |

**Error taxonomy**

| Constant                    | Code String             | HTTP Status |
|-----------------------------|-------------------------|-------------|
| `ERR_TOKEN_MISSING`         | `token_missing`         | 401         |
| `ERR_TOKEN_INVALID`         | `token_invalid`         | 401         |
| `ERR_TOKEN_EXPIRED`         | `token_expired`         | 401         |
| `ERR_USER_NOT_FOUND`        | `user_not_found`        | 403 / 422   |
| `ERR_USER_SUSPENDED`        | `user_suspended`        | 403 / 422   |
| `ERR_USER_INACTIVE`         | `user_inactive`         | 403 / 422   |
| `ERR_USER_REJECTED`         | `user_rejected`         | 403 / 422   |
| `ERR_ROLE_FORBIDDEN`        | `role_forbidden`        | 403 / 422   |
| `ERR_USER_NOT_LOGGED_IN`    | `user_not_logged_in`    | 403 / 422   |
| `ERR_VALUE_NOT_FOUND`       | `value_not_found`       | 404 / 422   |
| `ERR_VALUE_EXISTS`          | `value_exists`          | 404 / 422   |
| `ERR_VALUE_EMPTY`           | `value_empty`           | 404 / 422   |
| `ERR_VALUE_INVALID`         | `value_invalid`         | 404 / 422   |
| `ERR_VALUE_READONLY`        | `value_readonly`        | 404 / 422   |
| `ERR_FILE_NOT_FOUND`        | `file_not_found`        | 404 / 422   |
| `ERR_FILE_EXISTS`           | `file_exists`           | 404 / 422   |
| `ERR_FILE_MIMETYPE_INVALID` | `file_mimetype_invalid` | 404 / 422   |
| `ERR_FILE_HASH_EXISTS`      | `file_hash_exists`      | 404 / 422   |
| `ERR_FILE_HASH_MISMATCH`    | `file_hash_mismatch`    | 404 / 422   |
| `ERR_FILE_WRITE_ERROR`      | `file_write_error`      | 404 / 422   |
| `ERR_FILE_CONFLICT`         | `file_conflict`         | 404 / 422   |
| `ERR_LOCKED`                | `locked`                | 423         |
| `ERR_GOCRYPTFS_KEY_MISSING` | `gocryptfs_key_missing` | 498         |
| `ERR_GOCRYPTFS_KEY_INVALID` | `gocryptfs_key_invalid` | 499         |
| `ERR_SERVER_ERROR`          | `server_error`          | 500         |


## app.auth

The auth module is the security gatekeeper of the Hidden backend. It unifies JWT validation, role-based permissions, and user-state verification into a clear dependency system for FastAPI routers. By encapsulating all authentication logic in this module, the rest of the application remains clean, secure, and easily testable.

It provides authentication and permission control for the application’s REST API using JWT tokens. It ensures that only valid, active users with sufficient privileges can access protected routes. Each user role (reader, writer, editor, admin) maps to a specific FastAPI dependency that enforces the corresponding access rules.

**Responsibilities:**

- Validate and decode JWT bearer tokens supplied in the Authorization header.
- Verify token integrity, expiration, and signature using the configured secret and algorithm.
- Fetch user records from the database and Redis cache through the repository layer.
- Enforce role-based permissions (read, write, edit, admin).
- Perform additional checks (user existence and active status, suspension, JTI consistency).
- Raise detailed API errors with precise locations (`LOC_HEADER`, `Authorization`) and error codes (`ERR_TOKEN_MISSING`, `ERR_TOKEN_EXPIRED`, etc.).

**Key components:**

```python
auth(user_role: UserRole) -> Callable
```

Returns a FastAPI dependency enforcing permissions for the specified user role. Maps application roles to their corresponding role checkers (`_can_read`, `_can_write`, `_can_edit`, `_can_admin`).

**Example:**

```python
@router.get("/files", dependencies=[Depends(auth(UserRole.reader))])
async def list_files(...):
    ...
```

**Role checkers:**

- Extracts and validates the bearer token.
- Calls the internal _auth() function for full verification.
- Confirms that the user has the corresponding permission (can_read, can_write, can_edit, can_admin).
- Returns the authenticated User object or raises an HTTP exception.

**Example:**

```python
user = await _can_admin(request)
```

_auth(request, user_token, session, cache) -> User

**Authentication steps:**

1. Decode JWT via `decode_jwt()` using app configuration.
(raises `ERR_TOKEN_EXPIRED` if the signature has expired, `ERR_TOKEN_INVALID` for malformed or tampered tokens).
2. Validate payload — ensure user_id (int) and jti (str) fields are present.
3. Load user from storage via Repository.
4. Check state — active, not suspended, and matching decrypted JTI.
5. Return the fully validated User model instance.

**Error Handling**

All failures are wrapped with structured exceptions using helper E(), returning precise HTTP status codes and internal error constants:

| Condition                  | Error              | Status |
|----------------------------|--------------------|--------|
| Missing or malformed token | ERR_TOKEN_MISSING  | 401    |
| Invalid or corrupted token | ERR_TOKEN_INVALID  | 401    |
| Expired token              | ERR_TOKEN_EXPIRED  | 401    |
| User not found             | ERR_USER_NOT_FOUND | 403    |
| Inactive account           | ERR_USER_INACTIVE  | 403    |
| Suspended account          | ERR_USER_SUSPENDED | 403    |
| JTI mismatch               | ERR_USER_REJECTED  | 403    |

