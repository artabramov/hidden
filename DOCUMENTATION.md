# Hidden documentation

* app
  * [app](#module-app.app)
  * [auth](#module-app.auth)
  * [config](#module-app.config)
  * [constants](#module-app.constants)
  * [error](#module-app.error)
  * [hook](#module-app.hook)
  * [log](#module-app.log)
  * [lru](#module-app.lru)
  * [redis](#module-app.redis)
  * [repository](#module-app.repository)
  * [rwlock](#module-app.rwlock)
  * [sqlite](#module-app.sqlite)
  * [version](#module-app.version)
* addons
  * [addons.example_addon](#module-app.addons.example_addon)
* helpers
  * [image_helper](#module-app.helpers.image_helper)
  * [jwt_helper](#module-app.helpers.jwt_helper)
  * [mfa_helper](#module-app.helpers.mfa_helper)
  * [thumbnail_mixin](#module-app.helpers.thumbnail_mixin)
* managers
  * [cache_manager](#module-app.managers.cache_manager)
  * [encryption_manager](#module-app.managers.encryption_manager)
  * [entity_manager](#module-app.managers.entity_manager)
  * [file_manager](#module-app.managers.file_manager)
* models
  * [file](#module-app.models.file)
  * [file_meta](#module-app.models.file_meta)
  * [file_revision](#module-app.models.file_revision)
  * [file_tag](#module-app.models.file_tag)
  * [file_thumbnail](#module-app.models.file_thumbnail)
  * [folder](#module-app.models.folder)
  * [folder_meta](#module-app.models.folder_meta)
  * [user](#module-app.models.user)
  * [user_meta](#module-app.models.user_meta)
  * [user_thumbnail](#module-app.models.user_thumbnail)
* routers
  * [file_delete](#module-app.routers.file_delete)
  * [file_download](#module-app.routers.file_download)
  * [file_list](#module-app.routers.file_list)
  * [file_select](#module-app.routers.file_select)
  * [file_update](#module-app.routers.file_update)
  * [file_upload](#module-app.routers.file_upload)
  * [folder_delete](#module-app.routers.folder_delete)
  * [folder_insert](#module-app.routers.folder_insert)
  * [folder_list](#module-app.routers.folder_list)
  * [folder_select](#module-app.routers.folder_select)
  * [folder_update](#module-app.routers.folder_update)
  * [tag_delete](#module-app.routers.tag_delete)
  * [tag_insert](#module-app.routers.tag_insert)
  * [telemetry_retrieve](#module-app.routers.telemetry_retrieve)
  * [thumbnail_retrieve](#module-app.routers.thumbnail_retrieve)
  * [token_invalidate](#module-app.routers.token_invalidate)
  * [token_retrieve](#module-app.routers.token_retrieve)
  * [user_delete](#module-app.routers.user_delete)
  * [user_list](#module-app.routers.user_list)
  * [user_login](#module-app.routers.user_login)
  * [user_password](#module-app.routers.user_password)
  * [user_register](#module-app.routers.user_register)
  * [user_role](#module-app.routers.user_role)
  * [user_select](#module-app.routers.user_select)
  * [user_update](#module-app.routers.user_update)
  * [userpic_delete](#module-app.routers.userpic_delete)
  * [userpic_retrieve](#module-app.routers.userpic_retrieve)
  * [userpic_upload](#module-app.routers.userpic_upload)
* schemas
  * [file_delete](#module-app.schemas.file_delete)
  * [file_list](#module-app.schemas.file_list)
  * [file_select](#module-app.schemas.file_select)
  * [file_update](#module-app.schemas.file_update)
  * [file_upload](#module-app.schemas.file_upload)
  * [folder_delete](#module-app.schemas.folder_delete)
  * [folder_insert](#module-app.schemas.folder_insert)
  * [folder_list](#module-app.schemas.folder_list)
  * [folder_select](#module-app.schemas.folder_select)
  * [folder_update](#module-app.schemas.folder_update)
  * [revision_select](#module-app.schemas.revision_select)
  * [tag_delete](#module-app.schemas.tag_delete)
  * [tag_insert](#module-app.schemas.tag_insert)
  * [telemetry_retrieve](#module-app.schemas.telemetry_retrieve)
  * [token_invalidate](#module-app.schemas.token_invalidate)
  * [token_retrieve](#module-app.schemas.token_retrieve)
  * [user_delete](#module-app.schemas.user_delete)
  * [user_list](#module-app.schemas.user_list)
  * [user_login](#module-app.schemas.user_login)
  * [user_password](#module-app.schemas.user_password)
  * [user_register](#module-app.schemas.user_register)
  * [user_role](#module-app.schemas.user_role)
  * [user_select](#module-app.schemas.user_select)
  * [user_update](#module-app.schemas.user_update)
  * [userpic_delete](#module-app.schemas.userpic_delete)
  * [userpic_upload](#module-app.schemas.userpic_upload)
* validators
  * [file_validators](#module-app.validators.file_validators)
  * [folder_validators](#module-app.validators.folder_validators)
  * [tag_validators](#module-app.validators.tag_validators)
  * [user_validators](#module-app.validators.user_validators)
<a id="module-app"></a>

<a id="module-app.app"></a>
## app.app module

Hidden — main application module.

This module assembles the FastAPI application, connects core services,
mounts all routers, and defines global behavior. On startup, it loads
configuration, opens database and cache connections, and places shared
components into the application state. If lockdown mode is enabled, it
is forcibly disabled. On shutdown, all resources are released cleanly.

For every request, assign a UUID, measure and log duration, check the
lockdown state, and validate the gocryptfs key. Request logging is
enabled at DEBUG level.

Errors are handled centrally to produce consistent JSON. Returns 422 for
validation; 498/499 for gocryptfs-key issues; 423 for lockdown mode; 409
for file conflicts; 401/403 for auth errors. All other exceptions become
500. Every non-validation issue is logged with elapsed time and a stack
trace, and the response includes the request UUID (X-Request-ID). Error
logging is enabled at ERROR level.

<a id="app.app.add_cors_headers"></a>
### app.app.add_cors_headers(response: JSONResponse) → JSONResponse

Add headers to the response to allow cross-origin requests from any
source. This ensures that the response can be accessed by clients
from different domains, supports all HTTP methods and headers.

<a id="app.models.folder.Folder.path"></a>
<a id="app.models.file_revision.FileRevision.path"></a>
<a id="app.models.file.File.path"></a>
<a id="app.helpers.thumbnail_mixin.ThumbnailMixin.path"></a>
<a id="app.app.catch_all"></a>
### *async* app.app.catch_all(full_path: str, request: Request)

Serves static files. Returns the main HTML file if no specific
path is provided, or serves the requested file if it exists.

<a id="app.error.E"></a>
<a id="app.app.exception_handler"></a>
### *async* app.app.exception_handler(request: Request, e: Exception)

Handles exceptions and returns consistent JSON errors; logs elapsed
time (with stack trace for server errors) and appends X-Request-ID.

<a id="app.app.lifespan"></a>
### app.app.lifespan(app: FastAPI)

Initializes core services and a shared file manager on startup. On
shutdown, disposes database resources and closes cache connections.

<a id="app.hook.Hook.call"></a>
<a id="app.app.middleware_handler"></a>
### *async* app.app.middleware_handler(request: Request, call_next)

Binds a request-scoped logger, logs request timing, checks lockdown
state, reads the gocryptfs key, appends X-Request-ID to the response.

<a id="module-app.auth"></a>
<a id="app.auth.auth"></a>
## app.auth module

Provides authentication and permission checks based on JWT tokens,
mapping user roles to functions that validate their access rights
and raising detailed errors on invalid or expired tokens.

<a id="module-app.models"></a>
<a id="app.schemas.user_select.UserSelectResponse.role"></a>
<a id="app.schemas.user_role.UserRoleRequest.role"></a>
<a id="app.schemas.revision_select.RevisionSelectResponse.user"></a>
<a id="app.schemas.folder_select.FolderSelectResponse.user"></a>
<a id="app.schemas.file_select.FileSelectResponse.user"></a>
<a id="app.routers.user_role.user_role"></a>
<a id="app.models.user.UserRole"></a>
<a id="app.models.user.User.role"></a>
<a id="app.models.user.User"></a>
### app.auth.auth(user_role: [UserRole](#app.models.user.UserRole)) → Callable

Returns a FastAPI dependency enforcing permissions for the specified
role by mapping application roles to permission-check functions that
gate access to protected routes.

<a id="module-app.config"></a>
## app.config module

Defines the application configuration as a dataclass and loads values
from an .env file using the python-dotenv library, converting them
to the appropriate types; uses lru_cache to memoize the resulting
configuration object for efficient reuse.

<a id="app.lru.LRU"></a>
<a id="app.config.Config.UVICORN_WORKERS"></a>
<a id="app.config.Config.UVICORN_PORT"></a>
<a id="app.config.Config.UVICORN_HOST"></a>
<a id="app.config.Config.THUMBNAILS_WIDTH"></a>
<a id="app.config.Config.THUMBNAILS_QUALITY"></a>
<a id="app.config.Config.THUMBNAILS_HEIGHT"></a>
<a id="app.config.Config.THUMBNAILS_DIR"></a>
<a id="app.config.Config.TEMPORARY_DIR"></a>
<a id="app.config.Config.SQLITE_SQL_ECHO"></a>
<a id="app.config.Config.SQLITE_POOL_SIZE"></a>
<a id="app.config.Config.SQLITE_POOL_OVERFLOW"></a>
<a id="app.config.Config.SQLITE_PATH"></a>
<a id="app.config.Config.REVISIONS_DIR"></a>
<a id="app.config.Config.REDIS_PORT"></a>
<a id="app.config.Config.REDIS_HOST"></a>
<a id="app.config.Config.REDIS_EXPIRE"></a>
<a id="app.config.Config.REDIS_ENABLED"></a>
<a id="app.config.Config.REDIS_DECODE_RESPONSES"></a>
<a id="app.config.Config.LRU_TOTAL_SIZE_BYTES"></a>
<a id="app.config.Config.LRU_ITEM_SIZE_LIMIT_BYTES"></a>
<a id="app.config.Config.LOG_NAME"></a>
<a id="app.config.Config.LOG_LEVEL"></a>
<a id="app.config.Config.LOG_FORMAT"></a>
<a id="app.config.Config.LOG_FILES_LIMIT"></a>
<a id="app.config.Config.LOG_FILESIZE"></a>
<a id="app.config.Config.LOG_FILENAME"></a>
<a id="app.config.Config.LOCK_FILE_PATH"></a>
<a id="app.config.Config.JWT_SECRET"></a>
<a id="app.config.Config.JWT_ALGORITHMS"></a>
<a id="app.config.Config.JTI_LENGTH"></a>
<a id="app.config.Config.HTML_PATH"></a>
<a id="app.config.Config.HTML_FILE"></a>
<a id="app.config.Config.GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS"></a>
<a id="app.config.Config.GOCRYPTFS_PASSPHRASE_PATH"></a>
<a id="app.config.Config.GOCRYPTFS_PASSPHRASE_LENGTH"></a>
<a id="app.config.Config.GOCRYPTFS_DATA_MOUNTPOINT"></a>
<a id="app.config.Config.GOCRYPTFS_DATA_CIPHER_DIR"></a>
<a id="app.config.Config.FILE_SHRED_CYCLES"></a>
<a id="app.config.Config.FILE_DEFAULT_MIMETYPE"></a>
<a id="app.config.Config.FILE_CHUNK_SIZE"></a>
<a id="app.config.Config.FILES_DIR"></a>
<a id="app.config.Config.CRYPTO_NONCE_LENGTH"></a>
<a id="app.config.Config.CRYPTO_KEY_LENGTH"></a>
<a id="app.config.Config.CRYPTO_HKDF_SALT_B64"></a>
<a id="app.config.Config.CRYPTO_HKDF_INFO"></a>
<a id="app.config.Config.CRYPTO_DERIVE_WITH_HKDF"></a>
<a id="app.config.Config.CRYPTO_DEFAULT_ENCODING"></a>
<a id="app.config.Config.CRYPTO_AAD_DEFAULT"></a>
<a id="app.config.Config.AUTH_TOTP_ATTEMPTS"></a>
<a id="app.config.Config.AUTH_SUSPENDED_TIME"></a>
<a id="app.config.Config.AUTH_PASSWORD_ATTEMPTS"></a>
<a id="app.config.Config.ADDONS_PATH"></a>
<a id="app.config.Config.ADDONS_LIST"></a>
<a id="app.config.Config"></a>
### *class* app.config.Config(GOCRYPTFS_PASSPHRASE_PATH: str, GOCRYPTFS_PASSPHRASE_LENGTH: int, GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS: int, GOCRYPTFS_DATA_MOUNTPOINT: str, GOCRYPTFS_DATA_CIPHER_DIR: str, CRYPTO_KEY_LENGTH: int, CRYPTO_NONCE_LENGTH: int, CRYPTO_HKDF_INFO: bytes, CRYPTO_HKDF_SALT_B64: str, CRYPTO_DERIVE_WITH_HKDF: bool, CRYPTO_DEFAULT_ENCODING: str, CRYPTO_AAD_DEFAULT: bytes, LOCK_FILE_PATH: str, LOG_LEVEL: str, LOG_NAME: str, LOG_FORMAT: str, LOG_FILENAME: str, LOG_FILESIZE: int, LOG_FILES_LIMIT: int, UVICORN_HOST: str, UVICORN_PORT: int, UVICORN_WORKERS: int, SQLITE_PATH: str, SQLITE_POOL_SIZE: int, SQLITE_POOL_OVERFLOW: int, SQLITE_SQL_ECHO: bool, REDIS_ENABLED: bool, REDIS_HOST: str, REDIS_PORT: int, REDIS_DECODE_RESPONSES: bool, REDIS_EXPIRE: int, LRU_TOTAL_SIZE_BYTES: int, LRU_ITEM_SIZE_LIMIT_BYTES: int, FILE_CHUNK_SIZE: int, FILE_SHRED_CYCLES: int, FILE_DEFAULT_MIMETYPE: str, JTI_LENGTH: int, JWT_ALGORITHMS: list, JWT_SECRET: str, ADDONS_PATH: str, ADDONS_LIST: list, AUTH_PASSWORD_ATTEMPTS: int, AUTH_TOTP_ATTEMPTS: int, AUTH_SUSPENDED_TIME: int, FILES_DIR: str, REVISIONS_DIR: str, TEMPORARY_DIR: str, THUMBNAILS_DIR: str, THUMBNAILS_WIDTH: int, THUMBNAILS_HEIGHT: int, THUMBNAILS_QUALITY: int, HTML_PATH: str, HTML_FILE: str)

Bases: `object`

Strongly typed configuration where field names must match keys
in the .env file; values are trimmed and converted according to
their annotated types.

#### ADDONS_LIST *: list*

#### ADDONS_PATH *: str*

#### AUTH_PASSWORD_ATTEMPTS *: int*

#### AUTH_SUSPENDED_TIME *: int*

#### AUTH_TOTP_ATTEMPTS *: int*

#### CRYPTO_AAD_DEFAULT *: bytes*

#### CRYPTO_DEFAULT_ENCODING *: str*

#### CRYPTO_DERIVE_WITH_HKDF *: bool*

#### CRYPTO_HKDF_INFO *: bytes*

#### CRYPTO_HKDF_SALT_B64 *: str*

#### CRYPTO_KEY_LENGTH *: int*

#### CRYPTO_NONCE_LENGTH *: int*

#### FILES_DIR *: str*

#### FILE_CHUNK_SIZE *: int*

#### FILE_DEFAULT_MIMETYPE *: str*

#### FILE_SHRED_CYCLES *: int*

#### GOCRYPTFS_DATA_CIPHER_DIR *: str*

#### GOCRYPTFS_DATA_MOUNTPOINT *: str*

#### GOCRYPTFS_PASSPHRASE_LENGTH *: int*

#### GOCRYPTFS_PASSPHRASE_PATH *: str*

#### GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS *: int*

#### HTML_FILE *: str*

#### HTML_PATH *: str*

#### JTI_LENGTH *: int*

#### JWT_ALGORITHMS *: list*

#### JWT_SECRET *: str*

#### LOCK_FILE_PATH *: str*

#### LOG_FILENAME *: str*

#### LOG_FILESIZE *: int*

#### LOG_FILES_LIMIT *: int*

#### LOG_FORMAT *: str*

#### LOG_LEVEL *: str*

#### LOG_NAME *: str*

#### LRU_ITEM_SIZE_LIMIT_BYTES *: int*

#### LRU_TOTAL_SIZE_BYTES *: int*

#### REDIS_DECODE_RESPONSES *: bool*

#### REDIS_ENABLED *: bool*

#### REDIS_EXPIRE *: int*

#### REDIS_HOST *: str*

#### REDIS_PORT *: int*

#### REVISIONS_DIR *: str*

#### SQLITE_PATH *: str*

#### SQLITE_POOL_OVERFLOW *: int*

#### SQLITE_POOL_SIZE *: int*

#### SQLITE_SQL_ECHO *: bool*

#### TEMPORARY_DIR *: str*

#### THUMBNAILS_DIR *: str*

#### THUMBNAILS_HEIGHT *: int*

#### THUMBNAILS_QUALITY *: int*

#### THUMBNAILS_WIDTH *: int*

#### UVICORN_HOST *: str*

#### UVICORN_PORT *: int*

#### UVICORN_WORKERS *: int*

<a id="app.managers.cache_manager.CacheManager.get"></a>
<a id="app.config.get_config"></a>
### app.config.get_config() → [Config](#app.config.Config)

Loads configuration settings from an .env file and returns them as
a Config dataclass instance. The function uses type annotations to
convert the environment variable values to their appropriate types,
such as bool, int, list, str or bytes.

<a id="module-app.constants"></a>
## app.constants module

<a id="module-app.error"></a>
## app.error module

Centralized error definitions and HTTPException wrapper ensuring
consistent error codes and unified response format across the API.

### *exception* app.error.E(loc: list, error_input: str, error_type: str, status_code: int)

Bases: `HTTPException`

Unified HTTPException wrapper that produces error details in the
same shape as Pydantic validation errors.


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

<a id="module-app.hook"></a>
## app.hook module

Provides an application hook system: loads add-on modules listed in the
config, discovers async handlers named after known hooks, and registers
them for post-event execution.

<a id="app.hook.Hook"></a>
### *class* app.hook.Hook(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Bases: `object`

Executes registered hook handlers from app state, passing the
request session, Redis cache, the current user, and any extra
arguments.

#### *async* call(hook: str, \*args, \*\*kwargs)

Runs all handlers registered for the given hook in order,
passing session, cache, current user, and provided args/kwargs.

<a id="app.hook.init_hooks"></a>
### app.hook.init_hooks(app: FastAPI) → None

Builds the hook registry by importing add-on modules from the
configured path and registering async functions whose names match
constants in enabled hooks.

<a id="module-app.log"></a>
## app.log module

Initializes application logging with a concurrent-safe rotating file
handler. Applies formatter and level from the app, attaches the handler
only once, disables propagation to prevent duplicate output, stores the
logger on app state, and returns the ready-to-use instance.

<a id="app.log.init_logger"></a>
### app.log.init_logger(app: FastAPI) → Logger

Creates a logger from config, attaches a rotating handler,
sets level, stores it in app state, and returns it.

<a id="module-app.lru"></a>
## app.lru module

Byte-oriented LRU cache keyed by strings. Enforces a global capacity
with an optional per-item cap, promotes entries on access, and evicts
the least-recently used until within budget. Supports insert/update,
fetch with recency bump, removal, and full clear, and exposes live
size and item count properties.

<a id="app.lru.LRU.size"></a>
### *class* app.lru.LRU(cache_size_bytes: int, item_size_bytes: int | None = None)

Bases: `object`

LRU cache that stores bytes under string keys.
Limited both by total size in bytes and optional per-item size.

<a id="app.lru.LRU.clear"></a>
#### clear() → None

Clear cache completely.

<a id="app.lru.LRU.count"></a>
#### *property* count *: int*

Number of cached entries.

<a id="app.repository.Repository.delete"></a>
<a id="app.managers.file_manager.FileManager.delete"></a>
<a id="app.managers.entity_manager.EntityManager.delete"></a>
<a id="app.managers.cache_manager.CacheManager.delete"></a>
<a id="app.lru.LRU.delete"></a>
#### delete(path: str) → None

Remove a key if present.

<a id="app.lru.LRU.load"></a>
#### load(path: str) → bytes | None

Return cached value or None if not found.

<a id="app.schemas.tag_insert.TagInsertRequest.value"></a>
<a id="app.models.file_tag.FileTag.value"></a>
<a id="app.lru.LRU.save"></a>
#### save(path: str, value: bytes) → None

Insert or update a key, enforcing size limits.

#### *property* size *: int*

Total size of all cached entries in bytes.

<a id="module-app.redis"></a>
## app.redis module

Provides an asynchronous Redis client managed via FastAPI lifespan:
the client is created from runtime settings, stored in app.state for
reuse, exposed through a request-scoped dependency, and optionally
initialized on startup.

<a id="app.redis.RedisClient"></a>
### *class* app.redis.RedisClient(, host: str, port: int, decode_responses: bool = True)

Bases: `object`

Holds a shared asyncio Redis client built from configuration and
intended to be instantiated during application startup and reused
across requests via app.state.

<a id="app.redis.RedisClient.close"></a>
#### *async* close() → None

Close the underlying connection pool on application shutdown.

<a id="app.redis.get_cache"></a>
### *async* app.redis.get_cache(request: Request) → AsyncGenerator[Redis, None]

Yield the shared Redis client from app.state without closing it per
request so the connection pool can be reused efficiently across the
application.

<a id="app.redis.init_cache"></a>
### *async* app.redis.init_cache(client: [RedisClient](#app.redis.RedisClient)) → None

Optionally initialize the cache by checking connectivity and
performing startup tasks like a database flush if desired.

<a id="module-app.repository"></a>
## app.repository module

Defines a repository class that manages CRUD operations and caching for
SQLAlchemy models using an asynchronous session for database operations
and Redis for cache storage. Provides methods for existence checks,
insertion, selection, updating, deletion, counting, summation, and
transaction management with commit and rollback.

<a id="app.sqlite.Base"></a>
<a id="app.repository.Repository"></a>
### *class* app.repository.Repository(session: AsyncSession, cache: Redis, entity_class: Type[DeclarativeBase], config: [Config](#app.config.Config))

Bases: `object`

Provides a unified interface for performing CRUD operations on
SQLAlchemy models with integrated Redis caching.

<a id="app.repository.Repository.commit"></a>
<a id="app.managers.entity_manager.EntityManager.commit"></a>
#### *async* commit()

Commits the current transaction for pending changes in the
database.

<a id="app.repository.Repository.count_all"></a>
<a id="app.managers.entity_manager.EntityManager.count_all"></a>
#### *async* count_all(\*\*kwargs) → int

Counts the number of SQLAlchemy models that match the given
criteria.

#### *async* delete(entity: DeclarativeBase, commit: bool = True)

Deletes an entity from the database and removes its entry from
the cache if caching is enabled.

<a id="app.repository.Repository.delete_all"></a>
<a id="app.managers.entity_manager.EntityManager.delete_all"></a>
<a id="app.managers.cache_manager.CacheManager.delete_all"></a>
#### *async* delete_all(commit: bool = False, \*\*kwargs)

Deletes all SQLAlchemy models from the database  and cache that
match the given criteria.

<a id="app.repository.Repository.delete_all_from_cache"></a>
#### *async* delete_all_from_cache()

Deletes all entities of the managed SQLAlchemy model matching
the criteria from the database and clears them from the cache.

<a id="app.repository.Repository.delete_from_cache"></a>
#### *async* delete_from_cache(entity: DeclarativeBase)

Deletes an entity of the managed SQLAlchemy model from the cache
without affecting the database.

<a id="app.repository.Repository.exists"></a>
<a id="app.managers.entity_manager.EntityManager.exists"></a>
#### *async* exists(\*\*kwargs) → bool

Checks if a SQLAlchemy model matching the given criteria exists
in the database.

<a id="app.repository.Repository.insert"></a>
<a id="app.managers.entity_manager.EntityManager.insert"></a>
#### *async* insert(entity: DeclarativeBase, commit: bool = True)

Inserts a new entity of the managed SQLAlchemy model into the
database.

<a id="app.repository.Repository.rollback"></a>
<a id="app.managers.entity_manager.EntityManager.rollback"></a>
#### *async* rollback()

Rolls back the current transaction, discarding pending changes
in case of errors or inconsistencies.

<a id="app.repository.Repository.select"></a>
<a id="app.managers.entity_manager.EntityManager.select"></a>
#### *async* select(\*\*kwargs) → DeclarativeBase | None

Retrieves a SQLAlchemy model based on the provided criteria
or its ID.

<a id="app.repository.Repository.select_all"></a>
<a id="app.managers.entity_manager.EntityManager.select_all"></a>
#### *async* select_all(\*\*kwargs) → List[DeclarativeBase]

Retrieves all SQLAlchemy models from the database that match
the given criteria.

<a id="app.schemas.folder_update.FolderUpdateRequest.name"></a>
<a id="app.schemas.folder_select.FolderSelectResponse.name"></a>
<a id="app.schemas.folder_insert.FolderInsertRequest.name"></a>
<a id="app.repository.Repository.sum_all"></a>
<a id="app.models.folder.Folder.name"></a>
<a id="app.managers.entity_manager.EntityManager.sum_all"></a>
#### *async* sum_all(column_name: str, \*\*kwargs) → int

Calculates the sum of a specific column for all SQLAlchemy
models matching the criteria.

<a id="app.repository.Repository.update"></a>
<a id="app.managers.entity_manager.EntityManager.update"></a>
#### *async* update(entity: DeclarativeBase, commit: bool = True)

Updates an existing SQLAlchemy model in the database and
deletes from cache.

<a id="module-app.rwlock"></a>
## app.rwlock module

Async reader-writer synchronization primitive with writer preference for
asyncio-based code. Allows concurrent shared access for multiple readers
while ensuring writers acquire exclusive access and preventing new
readers from entering when a writer is active or queued. Designed to be
cancellation-safe, non-reentrant, and process-local, exposing context
managers for explicit read and write critical sections.

<a id="app.rwlock.RWLock"></a>
### *class* app.rwlock.RWLock

Bases: `object`

Asyncio-friendly readers-writer lock with writer preference:
multiple readers may proceed concurrently, writers acquire
exclusive access, and new readers are blocked while any writer
is active or waiting. Non-reentrant and in-process only;
cancellation-safe.

<a id="app.rwlock.RWLock.read"></a>
<a id="app.managers.file_manager.FileManager.read"></a>
#### read()

Acquire a shared read lock: waits while a writer is active or
queued, then yields; releases on exit and wakes waiters when
the last reader leaves.

<a id="app.rwlock.RWLock.write"></a>
<a id="app.managers.file_manager.FileManager.write"></a>
#### write()

Acquire an exclusive write lock: announces writer intent to
block new readers, waits for current readers to drain, then
yields; releases on exit and wakes pending readers/writers.

<a id="module-app.sqlite"></a>
## app.sqlite module

Sets up async SQLite engine and sessions for SQLAlchemy. The engine
and session factory are created from a Config instance and should be
constructed in FastAPI lifespan and stored in app.state.

### *class* app.sqlite.Base(\*\*kwargs: Any)

Bases: `DeclarativeBase`

<a id="app.sqlite.Base.metadata"></a>
#### metadata *: ClassVar[MetaData]* *= MetaData()*

Refers to the `_schema.MetaData` collection that will be used
for new `_schema.Table` objects.

#### SEE ALSO
orm_declarative_metadata

<a id="app.sqlite.Base.registry"></a>
#### registry *: ClassVar[\_RegistryType]* *= <sqlalchemy.orm.decl_api.registry object>*

Refers to the `_orm.registry` in use where new
`_orm.Mapper` objects will be associated.

<a id="app.sqlite.SessionManager"></a>
### *class* app.sqlite.SessionManager(, sqlite_path: str, sql_echo: bool = False)

Bases: `object`

Creates and manages the SQLite async engine and session factory
derived from runtime settings, intended to be instantiated during
application startup and reused via app.state for handling database
access.

<a id="app.sqlite.SessionManager.connection_string"></a>
#### *property* connection_string *: str*

Return the SQLAlchemy async URL for aiosqlite that points
at the resolved database file path.

<a id="app.sqlite.SessionManager.db_path"></a>
#### *property* db_path *: str*

Return the absolute filesystem path to the database file with
user home expansion and normalization applied.

<a id="app.sqlite.get_session"></a>
<a id="app.sqlite.SessionManager.get_session"></a>
#### get_session() → AsyncSession

Return a task-scoped AsyncSession so that concurrent coroutines
receive isolated sessions bound to their current asyncio task.

### *async* app.sqlite.get_session(request: Request) → AsyncGenerator[AsyncSession, None]

Yield an AsyncSession obtained from the SessionManager stored in
app.state and wrap it in a simple unit-of-work pattern that commits
on success, rolls back on error, and always closes the session.

<a id="app.sqlite.init_database"></a>
### *async* app.sqlite.init_database(session_manager: [SessionManager](#app.sqlite.SessionManager)) → None

Create the database schema for all mapped models by running
create_all against the async engine at application startup.

<a id="module-app.version"></a>
## app.version module

## Module contents
<a id="api/app.addons.md"></a>
<a id="module-app.addons"></a>
# app.addons package

<a id="module-app.addons.example_addon"></a>
## app.addons.example_addon module

Example addon for handling hook functions triggered by corresponding
events within the app. Each function is associated with a specific event
and is designed to be executed when that event occurs. Functions may
include additional logic such as event logging, updating the database,
managing the cache, performing file or network operations, interacting
with third-party apps, and other actions.

<a id="app.schemas.tag_insert.TagInsertResponse.file_id"></a>
<a id="app.schemas.tag_delete.TagDeleteResponse.file_id"></a>
<a id="app.schemas.revision_select.RevisionSelectResponse.file_id"></a>
<a id="app.schemas.file_upload.FileUploadResponse.file_id"></a>
<a id="app.schemas.file_update.FileUpdateResponse.file_id"></a>
<a id="app.schemas.file_delete.FileDeleteResponse.file_id"></a>
<a id="app.routers.file_delete.file_delete"></a>
<a id="app.models.file_thumbnail.FileThumbnail.file_id"></a>
<a id="app.models.file_tag.FileTag.file_id"></a>
<a id="app.models.file_revision.FileRevision.file_id"></a>
<a id="app.models.file_meta.FileMeta.file_id"></a>
<a id="app.addons.example_addon.after_file_delete"></a>
### *async* app.addons.example_addon.after_file_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file_id: int)

Executes after a file is deleted.

<a id="app.schemas.revision_select.RevisionSelectResponse.revision_number"></a>
<a id="app.routers.file_download.file_download"></a>
<a id="app.models.file_revision.FileRevision.revision_number"></a>
<a id="app.models.file.File"></a>
<a id="app.addons.example_addon.after_file_download"></a>
### *async* app.addons.example_addon.after_file_download(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File), revision_number: int)

Executes after a file is downloaded.

<a id="app.schemas.file_list.FileListResponse.files_count"></a>
<a id="app.schemas.file_list.FileListResponse.files"></a>
<a id="app.routers.file_list.file_list"></a>
<a id="app.addons.example_addon.after_file_list"></a>
### *async* app.addons.example_addon.after_file_list(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), files: List[[File](#app.models.file.File)], files_count: int)

Executes after a file list is retrieved.

<a id="app.routers.file_select.file_select"></a>
<a id="app.addons.example_addon.after_file_select"></a>
### *async* app.addons.example_addon.after_file_select(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File))

Executes after a file is retrieved.

<a id="app.routers.file_update.file_update"></a>
<a id="app.addons.example_addon.after_file_update"></a>
### *async* app.addons.example_addon.after_file_update(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File))

Executes after a file is updated.

<a id="app.routers.file_upload.file_upload"></a>
<a id="app.managers.file_manager.FileManager.upload"></a>
<a id="app.addons.example_addon.after_file_upload"></a>
### *async* app.addons.example_addon.after_file_upload(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File))

Executes after a file is uploaded.

<a id="app.schemas.folder_update.FolderUpdateResponse.folder_id"></a>
<a id="app.schemas.folder_insert.FolderInsertResponse.folder_id"></a>
<a id="app.schemas.folder_delete.FolderDeleteResponse.folder_id"></a>
<a id="app.schemas.file_update.FileUpdateRequest.folder_id"></a>
<a id="app.schemas.file_select.FileSelectResponse.folder"></a>
<a id="app.routers.folder_delete.folder_delete"></a>
<a id="app.models.folder_meta.FolderMeta.folder_id"></a>
<a id="app.models.file.File.folder_id"></a>
<a id="app.addons.example_addon.after_folder_delete"></a>
### *async* app.addons.example_addon.after_folder_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), folder_id: int)

Executes after a folder is deleted.

<a id="app.routers.folder_insert.folder_insert"></a>
<a id="app.models.folder.Folder"></a>
<a id="app.addons.example_addon.after_folder_insert"></a>
### *async* app.addons.example_addon.after_folder_insert(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), folder: [Folder](#app.models.folder.Folder))

Executes after a folder is created.

<a id="app.schemas.folder_list.FolderListResponse.folders_count"></a>
<a id="app.schemas.folder_list.FolderListResponse.folders"></a>
<a id="app.routers.folder_list.folder_list"></a>
<a id="app.addons.example_addon.after_folder_list"></a>
### *async* app.addons.example_addon.after_folder_list(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), folders: List[[Folder](#app.models.folder.Folder)], folders_count: int)

Executes after a folder list is retrieved.

<a id="app.routers.folder_select.folder_select"></a>
<a id="app.addons.example_addon.after_folder_select"></a>
### *async* app.addons.example_addon.after_folder_select(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), folder: [Folder](#app.models.folder.Folder))

Executes after a folder is retrieved.

<a id="app.routers.folder_update.folder_update"></a>
<a id="app.addons.example_addon.after_folder_update"></a>
### *async* app.addons.example_addon.after_folder_update(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), folder: [Folder](#app.models.folder.Folder))

Executes after a folder is updated.

<a id="app.routers.tag_delete.tag_delete"></a>
<a id="app.addons.example_addon.after_tag_delete"></a>
### *async* app.addons.example_addon.after_tag_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File), tag_value: str)

Executes after a tag is deleted.

<a id="app.routers.tag_insert.tag_insert"></a>
<a id="app.addons.example_addon.after_tag_insert"></a>
### *async* app.addons.example_addon.after_tag_insert(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File), tag_value: str)

Executes after a file tag is added.

<a id="app.routers.telemetry_retrieve.telemetry_retrieve"></a>
<a id="app.addons.example_addon.after_telemetry_retrieve"></a>
### *async* app.addons.example_addon.after_telemetry_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), telemetry: dict)

Executes after telemetry is retrieved.

<a id="app.routers.thumbnail_retrieve.thumbnail_retrieve"></a>
<a id="app.addons.example_addon.after_thumbnail_retrieve"></a>
### *async* app.addons.example_addon.after_thumbnail_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), file: [File](#app.models.file.File))

Executes after a file thumbnail is retrieved.

<a id="app.routers.token_invalidate.token_invalidate"></a>
<a id="app.addons.example_addon.after_token_invalidate"></a>
### *async* app.addons.example_addon.after_token_invalidate(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a token is invalidated (logout).

<a id="app.routers.token_retrieve.token_retrieve"></a>
<a id="app.addons.example_addon.after_token_retrieve"></a>
### *async* app.addons.example_addon.after_token_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a token is retrieved (issued).

<a id="app.routers.user_delete.user_delete"></a>
<a id="app.addons.example_addon.after_user_delete"></a>
### *async* app.addons.example_addon.after_user_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), user: [User](#app.models.user.User))

Executes after a user is deleted.

<a id="app.schemas.user_list.UserListResponse.users_count"></a>
<a id="app.schemas.user_list.UserListResponse.users"></a>
<a id="app.routers.user_list.user_list"></a>
<a id="app.addons.example_addon.after_user_list"></a>
### *async* app.addons.example_addon.after_user_list(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), users: List[[User](#app.models.user.User)], users_count: int)

Executes after a list of users is retrieved.

<a id="app.routers.user_login.user_login"></a>
<a id="app.addons.example_addon.after_user_login"></a>
### *async* app.addons.example_addon.after_user_login(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a user logs in.

<a id="app.schemas.user_register.UserRegisterRequest.password"></a>
<a id="app.schemas.user_login.UserLoginRequest.password"></a>
<a id="app.routers.user_password.user_password"></a>
<a id="app.addons.example_addon.after_user_password"></a>
### *async* app.addons.example_addon.after_user_password(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a user password is changed.

<a id="app.routers.user_register.user_register"></a>
<a id="app.addons.example_addon.after_user_register"></a>
### *async* app.addons.example_addon.after_user_register(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a user is registered.

<a id="app.addons.example_addon.after_user_role"></a>
### *async* app.addons.example_addon.after_user_role(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), user: [User](#app.models.user.User))

Executes after a user role or active status is changed.

<a id="app.routers.user_select.user_select"></a>
<a id="app.addons.example_addon.after_user_select"></a>
### *async* app.addons.example_addon.after_user_select(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), user: [User](#app.models.user.User))

Executes after a user is retrieved.

<a id="app.routers.user_update.user_update"></a>
<a id="app.addons.example_addon.after_user_update"></a>
### *async* app.addons.example_addon.after_user_update(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a user is updated.

<a id="app.routers.userpic_delete.userpic_delete"></a>
<a id="app.addons.example_addon.after_userpic_delete"></a>
### *async* app.addons.example_addon.after_userpic_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a userpic is deleted.

<a id="app.routers.userpic_retrieve.userpic_retrieve"></a>
<a id="app.addons.example_addon.after_userpic_retrieve"></a>
### *async* app.addons.example_addon.after_userpic_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User), user: [User](#app.models.user.User))

Executes after a userpic is retrieved.

<a id="app.routers.userpic_upload.userpic_upload"></a>
<a id="app.addons.example_addon.after_userpic_upload"></a>
### *async* app.addons.example_addon.after_userpic_upload(request: Request, session: AsyncSession, cache: Redis, current_user: [User](#app.models.user.User))

Executes after a userpic is uploaded.

## Module contents
<a id="api/app.helpers.md"></a>
<a id="module-app.helpers"></a>
# app.helpers package

<a id="module-app.helpers.image_helper"></a>
## app.helpers.image_helper module

Utilities for deterministic image processing. Provides an asynchronous
resize routine that runs in a worker thread, normalizes orientation from
embedded metadata, converts to an appropriate color mode, center-crops
to match the requested aspect ratio, resamples with a high-quality
filter, and overwrites the original file using an optimized progressive
encoding. It also centralizes the set of accepted input formats and the
preferred media type for downstream validation and content negotiation.

<a id="app.helpers.image_helper.image_resize"></a>
### *async* app.helpers.image_helper.image_resize(path: str, width: int, height: int, quality: int)

Asynchronously runs the sync resizer in a worker thread: applies
EXIF orientation, center-crops to the target aspect ratio, resizes
with Lanczos, and overwrites the file as a progressive JPEG.

<a id="module-app.helpers.jwt_helper"></a>
## app.helpers.jwt_helper module

Utilities for working with JSON Web Tokens: generates stable,
collision-resistant token identifiers, assembles signed claim sets
for authenticated users (including issued-at and optional expiry),
produces compact encoded tokens, and verifies and parses incoming
tokens with signature and standard claim validation.

<a id="app.schemas.token_retrieve.TokenRetrieveRequest.exp"></a>
<a id="app.helpers.jwt_helper.create_payload"></a>
### app.helpers.jwt_helper.create_payload(user: [User](#app.models.user.User), jti: str, exp: int = None)

Builds a JWT claims payload for the given user including user_id,
role, username, jti, and iat (Unix seconds); if exp is provided it
is used as an absolute expiration timestamp, otherwise the payload
is created without an exp claim.

<a id="app.helpers.jwt_helper.decode_jwt"></a>
### app.helpers.jwt_helper.decode_jwt(jwt_token: str, jwt_secret: str, jwt_algorithms: list) → dict

Decodes a JWT using the given secret and allowed algorithms,
validating the signature and standard claims (such as exp and iat)
and returning the claims dictionary, raising PyJWT exceptions on
invalid or expired tokens.

<a id="app.helpers.jwt_helper.encode_jwt"></a>
### app.helpers.jwt_helper.encode_jwt(payload: dict, jwt_secret: str, jwt_algorithm: str) → str

Encodes and signs the given claims payload into a compact JWT using
the supplied secret and algorithm via PyJWT.

<a id="app.helpers.jwt_helper.generate_jti"></a>
### app.helpers.jwt_helper.generate_jti(key_length: int) → str

Generates a cryptographically random alphanumeric JTI of the given
length for uniquely identifying and potentially revoking tokens.

<a id="module-app.helpers.mfa_helper"></a>
## app.helpers.mfa_helper module

Utilities for time-based one-time passwords used in multi-factor auth.
Provides a secure generator for random Base32 secrets and a helper to
compute the current OTP from a supplied secret, following standard TOTP
conventions so the codes interoperate with common authenticator apps.
Includes minimal input validation and avoids retaining state or
sensitive material beyond the returned values.

<a id="app.schemas.user_register.UserRegisterResponse.mfa_secret"></a>
<a id="app.schemas.token_retrieve.TokenRetrieveRequest.totp"></a>
<a id="app.helpers.mfa_helper.calculate_totp"></a>
### app.helpers.mfa_helper.calculate_totp(mfa_secret: str)

Computes the current time-based one-time password derived from
the provided Base32 secret, compatible with standard TOTP apps.

<a id="app.helpers.mfa_helper.generate_mfa_secret"></a>
### app.helpers.mfa_helper.generate_mfa_secret() → str

Generates and returns a random base32-encoded secret suitable
for use with time-based one-time password (TOTP) MFA systems.

<a id="module-app.helpers.thumbnail_mixin"></a>
## app.helpers.thumbnail_mixin module

Lightweight mixin for deriving absolute filesystem locations of
thumbnail artifacts from a UUID and an application configuration.
It provides a class utility to compute the path for an arbitrary
identifier and an instance-level convenience that delegates to the
same logic. The helpers are deterministic, side-effect free, and
keep storage layout concerns decoupled from the model.

<a id="app.helpers.thumbnail_mixin.ThumbnailMixin"></a>
### *class* app.helpers.thumbnail_mixin.ThumbnailMixin

Bases: `object`

Build absolute paths to thumbnail files.

#### path(config: Any) → str

Return absolute path to the thumbnail file by its UUID.

<a id="app.schemas.revision_select.RevisionSelectResponse.uuid"></a>
<a id="app.models.user_thumbnail.UserThumbnail.uuid"></a>
<a id="app.models.file_thumbnail.FileThumbnail.uuid"></a>
<a id="app.models.file_revision.FileRevision.uuid"></a>
<a id="app.models.file_revision.FileRevision.path_for_uuid"></a>
<a id="app.helpers.thumbnail_mixin.ThumbnailMixin.path_for_uuid"></a>
#### *classmethod* path_for_uuid(config: Any, uuid: str) → str

Return absolute path for a given UUID using config.

## Module contents
<a id="api/app.managers.md"></a>
<a id="module-app.managers"></a>
# app.managers package

<a id="module-app.managers.cache_manager"></a>
## app.managers.cache_manager module

Redis-backed cache manager for SQLAlchemy ORM entities. Provides
TTL-based caching of ORM instances, lookup by model and primary key,
bulk invalidation per model, and full-database flush, using SQLAlchemy’s
binary serialization format.

<a id="app.managers.cache_manager.CacheManager"></a>
### *class* app.managers.cache_manager.CacheManager(cache: Redis, expire: int)

Bases: `object`

Manages caching operations for SQLAlchemy models using Redis. This
class provides methods for setting, retrieving and deleting cached
SQLAlchemy model instances. It uses Redis for storage and supports
asynchronous operations to handle caching efficiently.

#### *async* delete(entity: DeclarativeBase) → None

Removes an SQLAlchemy model instance from the Redis cache by
deleting the cache entry associated with the given model.

#### *async* delete_all(cls: Type[DeclarativeBase]) → None

Removes all cached instances of a given SQLAlchemy model class
by deleting all cache entries related to the specified class.

<a id="app.managers.cache_manager.CacheManager.erase"></a>
#### *async* erase() → None

Clears all cached entries from Redis cache.

#### *async* get(cls: Type[DeclarativeBase], entity_id: int | str) → DeclarativeBase | None

Retrieves an SQLAlchemy model instance from the Redis cache by
fetching the serialized model from Redis and deserializing it.

<a id="app.managers.cache_manager.CacheManager.set"></a>
#### *async* set(entity: DeclarativeBase) → None

Caches an SQLAlchemy model instance by serializing it and
storing it in Redis cache with an expiration time.

<a id="module-app.managers.encryption_manager"></a>
## app.managers.encryption_manager module

Manager that centralizes symmetric encryption and message authentication.
It takes a secret at construction, derives an AEAD key with HKDF (or
uses the raw secret), configures AES-GCM with associated data, and
exposes helpers to encrypt/decrypt byte strings while emitting a
deterministic nonce-prefixed payload. String helpers wrap the binary
result in Base64, with integer and boolean conveniences layered on top.
A separate HMAC-SHA-512 routine is provided for non-reversible lookup
keys. The API avoids global state, is safe to call from asynchronous
paths, and keeps cryptographic details encapsulated behind a small,
consistent surface.

<a id="app.managers.encryption_manager.EncryptionManager"></a>
### *class* app.managers.encryption_manager.EncryptionManager(config: [Config](#app.config.Config), gocryptfs_key: str | bytes)

Bases: `object`

Coordinates symmetric encryption primitives behind a simple API.
Accepts configuration and a gocryptfs at construction.

<a id="app.managers.encryption_manager.EncryptionManager.decrypt_bool"></a>
#### decrypt_bool(token: str = None) → bool | None

Decrypts a base64 token and maps the integer back to a boolean.
Treats nonzero values as True and zero as False.

<a id="app.managers.encryption_manager.EncryptionManager.decrypt_bytes"></a>
#### decrypt_bytes(payload: bytes = None) → bytes | None

Decrypts bytes produced by this encryptor and verifies
authenticity.

<a id="app.managers.encryption_manager.EncryptionManager.decrypt_int"></a>
#### decrypt_int(token: str = None) → int | None

Decrypts a base64 token and parses the original integer value.
Raises on invalid numeric form as part of fail-fast behavior.

<a id="app.managers.encryption_manager.EncryptionManager.decrypt_str"></a>
#### decrypt_str(token: str = None) → str | None

Decrypts a base64 text produced by the string encryptor. Returns
the original text decoded with the configured charset.

<a id="app.managers.encryption_manager.EncryptionManager.encrypt_bool"></a>
#### encrypt_bool(value: bool = None) → str | None

Encrypts a boolean by mapping to an integer and using string
encryption. Returns a base64 token consistent with other scalar
helpers.

<a id="app.managers.encryption_manager.EncryptionManager.encrypt_bytes"></a>
#### encrypt_bytes(data: bytes = None) → bytes | None

Encrypts bytes and returns nonce||ciphertext (tag included).

<a id="app.managers.encryption_manager.EncryptionManager.encrypt_int"></a>
#### encrypt_int(value: int = None) → str | None

Encrypts an integer by converting to text and using string
encryption. Returns a base64 token suitable for storage or
transport.

<a id="app.managers.encryption_manager.EncryptionManager.encrypt_str"></a>
#### encrypt_str(value: str = None) → str | None

Encrypts text by encoding with the configured charset and
base64-wrapping the result. Returns a textual envelope of
the binary ciphertext.

<a id="app.managers.encryption_manager.EncryptionManager.get_hash"></a>
#### get_hash(value: str) → str

Computes an HMAC-SHA-512 over the given value using
a MAC-dedicated key. Returns a lowercase hexadecimal digest.

<a id="module-app.managers.entity_manager"></a>
## app.managers.entity_manager module

Asynchronous data-access manager that wraps an ORM session with a
small, consistent interface for common patterns: existence checks,
single-record fetches, list retrieval with keyword-style filters,
ordering and pagination, textual statements, batched deletions, and
simple aggregates such as counts and sums. Queries are constructed from
field/operator pairs, support membership and pattern matching, and can
emit subqueries for use in higher-level filters. The API keeps
transaction control explicit with flush/commit/rollback helpers and
avoids blocking by leveraging the underlying async engine.

<a id="app.managers.entity_manager.EntityManager"></a>
### *class* app.managers.entity_manager.EntityManager(session: AsyncSession)

Bases: `object`

Coordinates database operations for ORM entities over an async
session. Exposes CRUD, query helpers, aggregation, and transaction
control.

#### *async* commit()

Commits all changes made during the current transaction, making
them permanent in the database.

#### *async* count_all(cls: Type[DeclarativeBase], \*\*kwargs) → int

Counts entities matching the given criteria using an aggregate
query. Returns zero when no rows qualify.

<a id="app.managers.entity_manager.EntityManager.flush"></a>
#### *async* delete(obj: DeclarativeBase, flush: bool = True, commit: bool = False)

Marks an entity for removal from persistent storage. Optionally
flushes pending changes and commits the transaction.

#### *async* delete_all(cls: Type[DeclarativeBase], flush: bool = True, commit: bool = False, \*\*kwargs)

Removes entities matching filters in bounded batches. Iterates
until no further matches remain, minimizing pressure.

#### *async* exists(cls: Type[DeclarativeBase], \*\*kwargs) → bool

Checks if an entity of the SQLAlchemy model class exists
in the database based on the provided filters.

#### *async* flush()

Synchronizes pending changes in the session with the database.
Does not finalize the transaction or release locks.

#### *async* insert(obj: DeclarativeBase, flush: bool = True, commit: bool = True)

Adds a new entity to the current unit of work. Optionally
flushes pending changes and commits the transaction.

#### *async* rollback()

Reverts all changes made during the current transaction, undoing
any modifications to maintain consistency.

#### *async* select(cls: Type[DeclarativeBase], obj_id: int) → DeclarativeBase | None

Fetches a single entity by its primary identifier. Returns
the matching record or None when absent.

#### *async* select_all(cls: Type[DeclarativeBase], \*\*kwargs) → List[DeclarativeBase]

Returns all entities matching filters with optional ordering
and pagination. Intended for result lists without eager loading
or joins.

<a id="app.managers.entity_manager.EntityManager.select_by"></a>
#### *async* select_by(cls: Type[DeclarativeBase], \*\*kwargs) → DeclarativeBase | None

Fetches a single entity using filter criteria. Returns
the first match or None when nothing qualifies.

<a id="app.managers.entity_manager.EntityManager.select_rows"></a>
#### *async* select_rows(sql: str) → list

Executes a textual statement and returns raw result rows.

<a id="app.managers.entity_manager.EntityManager.subquery"></a>
#### *async* subquery(cls: Type[DeclarativeBase], foreign_key: str, \*\*kwargs) → select

Constructs a subquery for the given SQLAlchemy model class,
selecting the values of the specified foreign key column and
applying the provided filters. It builds a subquery object that
can be used to filter other queries based on the foreign key.

#### *async* sum_all(cls: Type[DeclarativeBase], column_name: str, \*\*kwargs) → int

Computes a sum over a numeric column for entities matching
filters. Returns zero when no rows qualify or the aggregate
is null.

#### *async* update(obj: DeclarativeBase, flush: bool = True, commit: bool = False)

Merges an entity’s state into the current unit of work.
Optionally flushes pending changes and commits the transaction.

<a id="module-app.managers.file_manager"></a>
## app.managers.file_manager module

Asynchronous file utilities for atomic writes, chunked I/O, and
multiple-pass overwrite deletion via a system tool. Favors fail-fast
behavior with minimal policy, leaving durability and higher-level
error handling to callers.

<a id="app.managers.file_manager.FileManager"></a>
### *class* app.managers.file_manager.FileManager(config: [Config](#app.config.Config))

Bases: `object`

Provides asynchronous file operations with atomic writes and
chunked I/O. Favors fail-fast behavior and avoids durability
guarantees beyond OS buffering.

<a id="app.schemas.revision_select.RevisionSelectResponse.checksum"></a>
<a id="app.schemas.file_select.FileSelectResponse.checksum"></a>
<a id="app.models.user_thumbnail.UserThumbnail.checksum"></a>
<a id="app.models.file_thumbnail.FileThumbnail.checksum"></a>
<a id="app.models.file_revision.FileRevision.checksum"></a>
<a id="app.models.file.File.checksum"></a>
<a id="app.managers.file_manager.FileManager.checksum"></a>
#### *async* checksum(path: str) → str

Computes and returns the SHA-256 hex digest of a file
asynchronously by streaming it in chunks.

<a id="app.managers.file_manager.FileManager.copy"></a>
#### *async* copy(src_path: str, dst_path: str) → None

Copies a file by streaming bytes and atomically replacing the
destination. Creates parent directories as needed and avoids
exposing partial results.

#### *async* delete(path: str) → None

Runs a system tool that overwrites a file in multiple passes and
unlinks it. Waits for completion and performs the operation only
if a regular file is present.

<a id="app.schemas.revision_select.RevisionSelectResponse.filesize"></a>
<a id="app.schemas.file_select.FileSelectResponse.filesize"></a>
<a id="app.models.user_thumbnail.UserThumbnail.filesize"></a>
<a id="app.models.file_thumbnail.FileThumbnail.filesize"></a>
<a id="app.models.file_revision.FileRevision.filesize"></a>
<a id="app.models.file.File.filesize"></a>
<a id="app.managers.file_manager.FileManager.filesize"></a>
#### *async* filesize(path: str) → int

Returns the size of a file in bytes via an async stat call.
Lets OS errors propagate (e.g., missing path).

<a id="app.managers.file_manager.FileManager.isdir"></a>
#### *async* isdir(path: str) → bool

Checks whether a path refers to an existing directory. Runs
asynchronously and returns False for files, non-existing paths,
and symlinks that don’t point to a directory.

<a id="app.managers.file_manager.FileManager.isfile"></a>
#### *async* isfile(path: str) → bool

Checks whether a path refers to an existing regular file.
Runs asynchronously and ignores non-file filesystem entries.

<a id="app.schemas.file_select.FileSelectResponse.mimetype"></a>
<a id="app.models.file.File.mimetype"></a>
<a id="app.managers.file_manager.FileManager.mimetype"></a>
#### *async* mimetype(path: str) → str | None

Detect MIME type by file content (libmagic), then by signature
(filetype), and finally by filename extension as a fallback.

<a id="app.managers.file_manager.FileManager.mkdir"></a>
#### *async* mkdir(path: str, is_file: bool = False) → None

Ensure required directories exist. For file paths, create parent
directories; for directory paths, create the directory itself.
Intermediate directories are created as needed; existing ones
are left untouched.

#### *async* read(path: str) → bytes

Reads the entire contents of a file into memory. Suitable for
small to medium inputs; consider streaming for large data.

<a id="app.managers.file_manager.FileManager.rename"></a>
#### *async* rename(src_path: str, dst_path: str) → None

Atomically moves or renames a file, overwriting any existing
target. Creates the destination’s parent directory when missing
and completes in one step.

<a id="app.managers.file_manager.FileManager.rmdir"></a>
#### *async* rmdir(path: str) → None

Remove a directory if it exists and is empty.

#### *async* upload(file: object, path: str) → None

Streams data from an asynchronous reader and writes it
atomically. Reads fixed-size chunks until exhaustion and
commits the result in one step.

#### *async* write(path: str, data: bytes) → None

Writes bytes sequence atomically using the same replace pattern.
Persists to a temporary file first and exposes the result only
when complete.

## Module contents
<a id="api/app.models.md"></a>
# app.models package

<a id="module-app.models.file"></a>
## app.models.file module

SQLAlchemy model for files.

<a id="app.schemas.userpic_upload.UserpicUploadResponse.user_id"></a>
<a id="app.schemas.userpic_delete.UserpicDeleteResponse.user_id"></a>
<a id="app.schemas.user_update.UserUpdateResponse.user_id"></a>
<a id="app.schemas.user_update.UserUpdateRequest.summary"></a>
<a id="app.schemas.user_select.UserSelectResponse.summary"></a>
<a id="app.schemas.user_role.UserRoleResponse.user_id"></a>
<a id="app.schemas.user_register.UserRegisterResponse.user_id"></a>
<a id="app.schemas.user_register.UserRegisterRequest.summary"></a>
<a id="app.schemas.user_password.UserPasswordResponse.user_id"></a>
<a id="app.schemas.user_login.UserLoginResponse.user_id"></a>
<a id="app.schemas.user_delete.UserDeleteResponse.user_id"></a>
<a id="app.schemas.token_retrieve.TokenRetrieveResponse.user_id"></a>
<a id="app.schemas.token_invalidate.TokenInvalidateResponse.user_id"></a>
<a id="app.schemas.tag_insert.TagInsertResponse.latest_revision_number"></a>
<a id="app.schemas.tag_delete.TagDeleteResponse.latest_revision_number"></a>
<a id="app.schemas.folder_update.FolderUpdateRequest.summary"></a>
<a id="app.schemas.folder_select.FolderSelectResponse.summary"></a>
<a id="app.schemas.folder_insert.FolderInsertRequest.summary"></a>
<a id="app.schemas.file_upload.FileUploadResponse.latest_revision_number"></a>
<a id="app.schemas.file_update.FileUpdateResponse.latest_revision_number"></a>
<a id="app.schemas.file_update.FileUpdateRequest.summary"></a>
<a id="app.schemas.file_update.FileUpdateRequest.filename"></a>
<a id="app.schemas.file_select.FileSelectResponse.summary"></a>
<a id="app.schemas.file_select.FileSelectResponse.latest_revision_number"></a>
<a id="app.schemas.file_select.FileSelectResponse.flagged"></a>
<a id="app.schemas.file_select.FileSelectResponse.filename"></a>
<a id="app.schemas.file_delete.FileDeleteResponse.latest_revision_number"></a>
<a id="app.models.user_thumbnail.UserThumbnail.user_id"></a>
<a id="app.models.user_meta.UserMeta.user_id"></a>
<a id="app.models.user.User.summary"></a>
<a id="app.models.folder.Folder.user_id"></a>
<a id="app.models.folder.Folder.summary"></a>
<a id="app.models.file_revision.FileRevision.user_id"></a>
<a id="app.models.file.File.user_id"></a>
<a id="app.models.file.File.summary"></a>
<a id="app.models.file.File.latest_revision_number"></a>
<a id="app.models.file.File.flagged"></a>
<a id="app.models.file.File.filename"></a>
### *class* app.models.file.File(user_id, folder_id, filename, filesize, checksum, mimetype=None, flagged=False, summary=None, latest_revision_number=0)

Bases: [`Base`](#app.sqlite.Base)

#### checksum

<a id="app.schemas.user_select.UserSelectResponse.created_date"></a>
<a id="app.schemas.revision_select.RevisionSelectResponse.created_date"></a>
<a id="app.schemas.folder_select.FolderSelectResponse.created_date"></a>
<a id="app.schemas.file_select.FileSelectResponse.created_date"></a>
<a id="app.models.user_thumbnail.UserThumbnail.created_date"></a>
<a id="app.models.user_meta.UserMeta.created_date"></a>
<a id="app.models.user.User.created_date"></a>
<a id="app.models.folder_meta.FolderMeta.created_date"></a>
<a id="app.models.folder.Folder.created_date"></a>
<a id="app.models.file_thumbnail.FileThumbnail.created_date"></a>
<a id="app.models.file_tag.FileTag.created_date"></a>
<a id="app.models.file_revision.FileRevision.created_date"></a>
<a id="app.models.file_meta.FileMeta.created_date"></a>
<a id="app.models.file.File.created_date"></a>
#### created_date

<a id="app.models.file.File.file_folder"></a>
#### file_folder

<a id="app.models.file.File.file_meta"></a>
#### file_meta

<a id="app.schemas.file_select.FileSelectResponse.file_revisions"></a>
<a id="app.models.file.File.file_revisions"></a>
#### file_revisions

<a id="app.schemas.file_select.FileSelectResponse.file_tags"></a>
<a id="app.models.file.File.file_tags"></a>
#### file_tags

<a id="app.models.file.File.file_thumbnail"></a>
#### file_thumbnail

<a id="app.models.file.File.file_user"></a>
#### file_user

#### filename

#### filesize

#### flagged

#### folder_id

<a id="app.models.file.File.has_revisions"></a>
#### *property* has_revisions *: bool*

<a id="app.schemas.user_select.UserSelectResponse.has_thumbnail"></a>
<a id="app.models.user.User.has_thumbnail"></a>
<a id="app.models.file.File.has_thumbnail"></a>
#### *property* has_thumbnail *: bool*

#### id

#### latest_revision_number

#### mimetype

#### path(config: Any) → str

Return absolute path to the file file by config.

<a id="app.models.file.File.path_for_filename"></a>
#### *classmethod* path_for_filename(config: Any, folder_name: str, filename: str) → str

Return absolute path to the file file by parameters.

#### summary

<a id="app.models.user.User.to_dict"></a>
<a id="app.models.folder.Folder.to_dict"></a>
<a id="app.models.file_revision.FileRevision.to_dict"></a>
<a id="app.models.file.File.to_dict"></a>
#### *async* to_dict() → dict

Returns a dictionary representation of the file.

<a id="app.schemas.folder_select.FolderSelectResponse.updated_date"></a>
<a id="app.schemas.file_select.FileSelectResponse.updated_date"></a>
<a id="app.models.user_thumbnail.UserThumbnail.updated_date"></a>
<a id="app.models.user_meta.UserMeta.updated_date"></a>
<a id="app.models.user.User.updated_date"></a>
<a id="app.models.folder_meta.FolderMeta.updated_date"></a>
<a id="app.models.folder.Folder.updated_date"></a>
<a id="app.models.file_thumbnail.FileThumbnail.updated_date"></a>
<a id="app.models.file_meta.FileMeta.updated_date"></a>
<a id="app.models.file.File.updated_date"></a>
#### updated_date

#### user_id

<a id="module-app.models.file_meta"></a>
## app.models.file_meta module

SQLAlchemy model for file metadata.

<a id="app.models.file_meta.FileMeta"></a>
### *class* app.models.file_meta.FileMeta(\*\*kwargs)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for file metadata. Stores a key-value pair linked
to a file; keys are unique within each file.

#### created_date

#### file_id

#### id

<a id="app.models.file_meta.FileMeta.meta_file"></a>
#### meta_file

<a id="app.models.user_meta.UserMeta.meta_key"></a>
<a id="app.models.folder_meta.FolderMeta.meta_key"></a>
<a id="app.models.file_meta.FileMeta.meta_key"></a>
#### meta_key

<a id="app.models.user_meta.UserMeta.meta_value"></a>
<a id="app.models.folder_meta.FolderMeta.meta_value"></a>
<a id="app.models.file_meta.FileMeta.meta_value"></a>
#### meta_value

#### updated_date

<a id="module-app.models.file_revision"></a>
## app.models.file_revision module

SQLAlchemy model for file revisions.

<a id="app.models.file_revision.FileRevision"></a>
### *class* app.models.file_revision.FileRevision(user_id, file_id, revision_number, uuid, filesize, checksum)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for file revisions. Immutable snapshots of a file.

#### checksum

#### created_date

#### file_id

#### filesize

#### id

#### path(config: Any) → str

Return absolute path to the thumbnail file by its UUID.

#### *classmethod* path_for_uuid(config: Any, uuid: str) → str

Return absolute path for a given UUID using config.

<a id="app.models.file_revision.FileRevision.revision_file"></a>
#### revision_file

#### revision_number

<a id="app.models.file_revision.FileRevision.revision_user"></a>
#### revision_user

#### *async* to_dict() → dict

Returns a dictionary representation of the revision.

#### user_id

#### uuid

<a id="module-app.models.file_tag"></a>
## app.models.file_tag module

SQLAlchemy model for file tags.

<a id="app.models.file_tag.FileTag"></a>
### *class* app.models.file_tag.FileTag(file_id, value)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for file tags. Stores a tag value linked
to a file; values are unique within each file.

#### created_date

#### file_id

#### id

<a id="app.models.file_tag.FileTag.tag_file"></a>
#### tag_file

#### value

<a id="module-app.models.file_thumbnail"></a>
## app.models.file_thumbnail module

SQLAlchemy model for file thumbnails.

<a id="app.models.file_thumbnail.FileThumbnail"></a>
### *class* app.models.file_thumbnail.FileThumbnail(file_id, uuid, filesize, checksum)

Bases: [`Base`](#app.sqlite.Base), [`ThumbnailMixin`](#app.helpers.thumbnail_mixin.ThumbnailMixin)

SQLAlchemy model for file thumbnails. One-to-one thumbnail
linked to a file; stores UUID (thumbnail file name), file
size, and checksum.

#### checksum

#### created_date

#### file_id

#### filesize

#### id

<a id="app.models.file_thumbnail.FileThumbnail.thumbnail_file"></a>
#### thumbnail_file

#### updated_date

#### uuid

<a id="module-app.models.folder"></a>
## app.models.folder module

SQLAlchemy model for folders.

<a id="app.schemas.folder_update.FolderUpdateRequest.readonly"></a>
<a id="app.schemas.folder_select.FolderSelectResponse.readonly"></a>
<a id="app.schemas.folder_insert.FolderInsertRequest.readonly"></a>
<a id="app.models.folder.Folder.readonly"></a>
### *class* app.models.folder.Folder(user_id, readonly, name, summary=None)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for folders. Stores a unique name, read-only
flag, creation/update timestamps, and optional summary.

#### created_date

<a id="app.models.folder.Folder.folder_files"></a>
#### folder_files

<a id="app.models.folder.Folder.folder_meta"></a>
#### folder_meta

<a id="app.models.folder.Folder.folder_user"></a>
#### folder_user

#### id

#### name

#### path(config: Any) → str

Return absolute path to the folder by config.

<a id="app.models.folder.Folder.path_for_dir"></a>
#### *classmethod* path_for_dir(config: Any, folder_name: str) → str

Return absolute path to the folder by parameters.

#### readonly

#### summary

#### *async* to_dict() → dict

Returns a dictionary representation of the folder.

#### updated_date

#### user_id

<a id="module-app.models.folder_meta"></a>
## app.models.folder_meta module

SQLAlchemy model for folder metadata.

<a id="app.models.folder_meta.FolderMeta"></a>
### *class* app.models.folder_meta.FolderMeta(\*\*kwargs)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for folder metadata. Stores a key-value pair
linked to a folder; keys are unique within each folder.

#### created_date

#### folder_id

#### id

<a id="app.models.folder_meta.FolderMeta.meta_folder"></a>
#### meta_folder

#### meta_key

#### meta_value

#### updated_date

<a id="module-app.models.user"></a>
## app.models.user module

SQLAlchemy model for users.

<a id="app.schemas.user_update.UserUpdateRequest.last_name"></a>
<a id="app.schemas.user_update.UserUpdateRequest.first_name"></a>
<a id="app.schemas.user_select.UserSelectResponse.username"></a>
<a id="app.schemas.user_select.UserSelectResponse.last_name"></a>
<a id="app.schemas.user_select.UserSelectResponse.first_name"></a>
<a id="app.schemas.user_select.UserSelectResponse.active"></a>
<a id="app.schemas.user_role.UserRoleRequest.active"></a>
<a id="app.schemas.user_register.UserRegisterRequest.username"></a>
<a id="app.schemas.user_register.UserRegisterRequest.last_name"></a>
<a id="app.schemas.user_register.UserRegisterRequest.first_name"></a>
<a id="app.schemas.user_login.UserLoginRequest.username"></a>
<a id="app.schemas.token_retrieve.TokenRetrieveRequest.username"></a>
<a id="app.models.user.User.username"></a>
<a id="app.models.user.User.password_hash"></a>
<a id="app.models.user.User.mfa_secret_encrypted"></a>
<a id="app.models.user.User.last_name"></a>
<a id="app.models.user.User.jti_encrypted"></a>
<a id="app.models.user.User.first_name"></a>
<a id="app.models.user.User.active"></a>
### *class* app.models.user.User(username, password_hash, first_name, last_name, role, active, mfa_secret_encrypted, jti_encrypted, summary=None)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for users. Stores authentication credentials,
access role, status flags, audit timestamps, MFA fields, and
optional profile information.

#### active

<a id="app.models.user.UserRole.admin"></a>
<a id="app.models.user.User.can_admin"></a>
#### *property* can_admin *: bool*

<a id="app.models.user.User.can_edit"></a>
#### *property* can_edit *: bool*

<a id="app.models.user.User.can_read"></a>
#### *property* can_read *: bool*

<a id="app.models.user.User.can_write"></a>
#### *property* can_write *: bool*

#### created_date

#### first_name

<a id="app.models.user.User.full_name"></a>
#### full_name

#### *property* has_thumbnail *: bool*

#### id

#### jti_encrypted

<a id="app.schemas.user_select.UserSelectResponse.last_login_date"></a>
<a id="app.models.user.User.last_login_date"></a>
#### last_login_date

#### last_name

<a id="app.models.user.User.mfa_attempts"></a>
#### mfa_attempts

#### mfa_secret_encrypted

<a id="app.schemas.user_login.UserLoginResponse.password_accepted"></a>
<a id="app.models.user.User.password_accepted"></a>
#### password_accepted

<a id="app.models.user.User.password_attempts"></a>
#### password_attempts

#### password_hash

#### role

#### summary

<a id="app.models.user.User.suspended_until_date"></a>
#### suspended_until_date

#### *async* to_dict() → dict

Returns a dictionary representation of the user.

#### updated_date

<a id="app.models.user.User.user_files"></a>
#### user_files

<a id="app.models.user.User.user_folders"></a>
#### user_folders

<a id="app.models.user.User.user_meta"></a>
#### user_meta

<a id="app.models.user.User.user_revisions"></a>
#### user_revisions

<a id="app.models.user.User.user_thumbnail"></a>
#### user_thumbnail

#### username

### *class* app.models.user.UserRole

Bases: `object`

Defines the available user roles in the application.
Each role determines a predefined set of permissions.

#### admin *= 'admin'*

<a id="app.models.user.UserRole.editor"></a>
#### editor *= 'editor'*

<a id="app.models.user.UserRole.reader"></a>
#### reader *= 'reader'*

<a id="app.models.user.UserRole.writer"></a>
#### writer *= 'writer'*

<a id="module-app.models.user_meta"></a>
## app.models.user_meta module

SQLAlchemy model for user metadata.

<a id="app.models.user_meta.UserMeta"></a>
### *class* app.models.user_meta.UserMeta(\*\*kwargs)

Bases: [`Base`](#app.sqlite.Base)

SQLAlchemy model for user metadata. Stores a key-value pair
linked to a user; keys are unique within each folder.

#### created_date

#### id

#### meta_key

<a id="app.models.user_meta.UserMeta.meta_user"></a>
#### meta_user

#### meta_value

#### updated_date

#### user_id

<a id="module-app.models.user_thumbnail"></a>
## app.models.user_thumbnail module

SQLAlchemy model for user thumbnails.

<a id="app.models.user_thumbnail.UserThumbnail"></a>
### *class* app.models.user_thumbnail.UserThumbnail(user_id, uuid, filesize, checksum)

Bases: [`Base`](#app.sqlite.Base), [`ThumbnailMixin`](#app.helpers.thumbnail_mixin.ThumbnailMixin)

SQLAlchemy model for user thumbnails. One-to-one thumbnail
linked to a user; stores its UUID, size, and checksum.

#### checksum

#### created_date

#### filesize

#### id

<a id="app.models.user_thumbnail.UserThumbnail.thumbnail_user"></a>
#### thumbnail_user

#### updated_date

#### user_id

#### uuid

## Module contents
<a id="api/app.routers.md"></a>
<a id="module-app.routers"></a>
# app.routers package

<a id="module-app.routers.file_delete"></a>
## app.routers.file_delete module

FastAPI router for file deleting.

<a id="module-app.schemas"></a>
<a id="app.schemas.file_delete.FileDeleteResponse"></a>
### *async* app.routers.file_delete.file_delete(request: Request, folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_admin)) → [FileDeleteResponse](#app.schemas.file_delete.FileDeleteResponse)

Delete a file and all associated artifacts (thumbnail, revisions,
head file).

**Authentication:**
- Requires a valid bearer token with admin role.

**Path parameters:**
- folder_id (integer ≥ 1): parent folder identifier.
- file_id (integer ≥ 1): file identifier.

**Response:**
- FileDeleteResponse with file ID and latest revision
number.

**Response codes:**
- 200 — file deleted successfully.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder or file not found.
- 409 — conflict: thumbnail, revision or head file is missing.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Deletes thumbnail, all revisions, and the head file from the
filesystem; purges LRU cache entries.

**Hooks:**
- HOOK_AFTER_FILE_DELETE — executed after successful deletion.

<a id="module-app.routers.file_download"></a>
## app.routers.file_download module

FastAPI router for file downloading.

### *async* app.routers.file_download.file_download(request: Request, folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), revision_number: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → Response

Download a file file (current head or a specific revision) within
a given folder. Returns the raw file bytes with the file’s
MIME type, and the original filename.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Path parameters:**
- folder_id (integer ≥ 1): parent folder identifier.
- file_id (integer ≥ 1): file identifier.
- revision_number (integer ≥ 0): 0 for the current file head;
> 0 for a specific revision.

**Response codes:**
- 200 — file returned.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder, file, or revision not found.
- 409 — file not found on filesystem or checksum mismatch.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_FILE_DOWNLOAD — executed after a successful read.

<a id="module-app.routers.file_list"></a>
## app.routers.file_list module

FastAPI router for file listing.

<a id="app.schemas.file_list.FileListResponse"></a>
<a id="app.schemas.file_list.FileListRequest"></a>
### *async* app.routers.file_list.file_list(request: Request, schema=Depends(FileListRequest), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [FileListResponse](#app.schemas.file_list.FileListResponse)

Retrieve files matching the provided filters and return them
with the total number of matches.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Query parameters:**
- FileListRequest — optional filters (folder_id, creation time,
creator, flagged status, filename/mimetype, file size), pagination
(offset and limit), and ordering (order_by and order).

**Response:**
- FileListResponse — page of files and total match count.

**Response codes:**
- 200 — list returned.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_FILE_LIST: executed after successful retrieval.

<a id="module-app.routers.file_select"></a>
## app.routers.file_select module

FastAPI router for file retrieving.

<a id="app.schemas.file_select.FileSelectResponse"></a>
### *async* app.routers.file_select.file_select(request: Request, folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [FileSelectResponse](#app.schemas.file_select.FileSelectResponse)

Retrieve a single file by ID within a given folder and return its
details, including creator, parent folder, timestamps, flagged
status, filename, size, MIME type, checksum, summary, and latest
revision.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Response schema:**
- FileSelectResponse — includes file ID; creator; parent folder;
creation and last-update timestamps (Unix seconds, UTC); flagged
status; filename; file size; MIME type (optional); content checksum;
optional summary; and the latest revision number.

**Path parameters:**
- folder_id (integer ≥ 1): parent folder identifier.
- file_id (integer ≥ 1): file identifier.

**Response codes:**
- 200 — file found; details returned.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder or file not found.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_FILE_SELECT: executed after a successful
retrieval.

<a id="module-app.routers.file_update"></a>
## app.routers.file_update module

FastAPI router for file changing.

<a id="app.schemas.file_update.FileUpdateResponse"></a>
<a id="app.schemas.file_update.FileUpdateRequest"></a>
### *async* app.routers.file_update.file_update(request: Request, schema: [FileUpdateRequest](#app.schemas.file_update.FileUpdateRequest), folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_edit)) → [FileUpdateResponse](#app.schemas.file_update.FileUpdateResponse)

Updates a file by renaming its head file within the current folder,
moving the head file to a different folder (keeping its name),
and/or changing the file summary. Disk changes are performed with
an atomic rename; the file row is staged (no-commit), the file is
renamed or moved on disk, and then the transaction is committed to
keep database and filesystem in sync.

Concurrency is controlled with per-path locks. For rename/move, two
locks are acquired in a deterministic order to prevent deadlocks.
All database and filesystem checks are executed inside this critical
section. These locks are in-process.

Files are stored under their folder directory. The database enforces
uniqueness of (folder_id, filename) for files.

**Authentication:**
- Requires a valid bearer token with editor role or higher.

**Validation schemas:**
- FileUpdateRequest — optional fields: filename, summary,
folder_id.
- FileUpdateResponse — returns file_id and
latest_revision_number.

**Path parameters:**
- folder_id (integer ≥ 1) — current folder identifier.
- file_id (integer ≥ 1) — file identifier.

**Request body:**
- application/json with any of: filename, summary,
folder_id.

**Response codes:**
- 200 — update successful.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder or file not found.
- 409 — conflict: name already exists in DB/FS or DB/FS mismatch
(file present but file missing, or vice versa).
- 422 — invalid file name.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_FILE_UPDATE — executed after a successful update.

<a id="module-app.routers.file_upload"></a>
## app.routers.file_upload module

FastAPI router for file uploading.

<a id="app.schemas.file_upload.FileUploadResponse"></a>
### *async* app.routers.file_upload.file_upload(request: Request, folder_id: int = Path(PydanticUndefined), data: UploadFile = File(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_write)) → [FileUploadResponse](#app.schemas.file_upload.FileUploadResponse)

Uploads a file into the target folder. If no file with that name
exists, a new one is created; if it does, the current head file
is snapshotted as a new immutable revision and the upload becomes
the new head. File metadata (size, MIME type, checksum) is computed
from the uploaded content and persisted. Disk writes are performed
via a temporary file followed by an atomic rename to avoid partial
states.

This operation is serialized per (folder_id, filename) using an
in-process asyncio lock, so concurrent uploads of the same name in a
single process are executed one by one. In the update path, if the
database commit fails after the head file was already replaced on
disk, the previous head is restored from the just-created revision
to keep the filesystem and database consistent. Thumbnails are
regenerated for image types inside the same critical section after
a successful commit; any outdated thumbnail is removed first.

**Authentication:**
- Requires a valid bearer token with writer role or higher.

**Validation schemas:**
- FileUploadResponse — contains the newly created (or updated)
file ID and the latest revision number.

**Path parameters:**
- folder_id (integer ≥ 1) — target folder identifier.

**Request body:**
- file — the file to upload (multipart/form-data).

**Response codes:**
- 201 — file successfully uploaded; file created or replaced
(revision recorded when replaced); thumbnail generated or skipped.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role to perform the operation, invalid JTI,
user is inactive or suspended.
- 404 — folder not found.
- 409 — conflict on DB/FS mismatch for the file (file present but
file missing, or vice versa; MIME type changed for an existing file).
- 422 — invalid file name.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_FILE_UPLOAD: executed after a successful upload.

<a id="module-app.routers.folder_delete"></a>
## app.routers.folder_delete module

FastAPI router for folder deleting.

<a id="app.schemas.folder_delete.FolderDeleteResponse"></a>
### *async* app.routers.folder_delete.folder_delete(request: Request, folder_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_admin)) → [FolderDeleteResponse](#app.schemas.folder_delete.FolderDeleteResponse)

Delete a folder and all its files (including thumbnails, revisions,
and head files).

Disk cleanup is best-effort: missing thumbnails/revisions/head
files are ignored. A WRITE lock on the folder is taken to block
concurrent file operations during deletion.

**Authentication:**
- Requires a valid bearer token with admin role.

**Path parameters:**
- folder_id (integer ≥ 1): folder identifier.

**Response:**
- FolderDeleteResponse — returns the deleted folder ID.

**Response codes:**
- 200 — folder deleted.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder not found.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Removes thumbnails, revisions, and head files from the filesystem
(best-effort); purges LRU cache entries.

**Hooks:**
- HOOK_AFTER_FOLDER_DELETE — executed after successful
deletion.

<a id="module-app.routers.folder_insert"></a>
## app.routers.folder_insert module

FastAPI router for creating folders.

<a id="app.schemas.folder_insert.FolderInsertResponse"></a>
<a id="app.schemas.folder_insert.FolderInsertRequest"></a>
### *async* app.routers.folder_insert.folder_insert(request: Request, schema: [FolderInsertRequest](#app.schemas.folder_insert.FolderInsertRequest), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_write)) → [FolderInsertResponse](#app.schemas.folder_insert.FolderInsertResponse)

Create a new folder and a matching directory on the filesystem, then
return the ID. The folder name must be unique; if a name is already
taken, the request is rejected.

**Authentication:**
- Requires a valid bearer token with writer role or higher.

**Validation schemas:**
- FolderInsertRequest — request body with read-only flag,
name, and optional summary.
- FolderInsertResponse — contains the newly created folder ID.

**Request body:**
- readonly (boolean): read-only flag for the folder.
- name (string, 1-256; ≤255 UTF-8 bytes): folder name;
trimmed; / and NUL are not allowed.
- summary (string, 0-4096): optional description; trimmed; empty
becomes NULL.

**Response codes:**
- 201 — folder successfully created.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 422 — name already exists or fails validation.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Creates a directory at files/<name>.

**Hooks:**
- HOOK_AFTER_FOLDER_INSERT: executed after folder and directory
are successfully created.

<a id="module-app.routers.folder_list"></a>
## app.routers.folder_list module

FastAPI router for folder listing.

<a id="app.schemas.folder_list.FolderListResponse"></a>
<a id="app.schemas.folder_list.FolderListRequest"></a>
### *async* app.routers.folder_list.folder_list(request: Request, schema=Depends(FolderListRequest), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [FolderListResponse](#app.schemas.folder_list.FolderListResponse)

Retrieve folders matching the provided filters and return them with
the total number of matches.

**Authentication**
- Requires a valid bearer token with reader role or higher.

**Query parameters**
- FolderListRequest — optional filters (creation time, creator,
readonly flag, name), pagination (offset/limit), and ordering
(order_by/order).

**Response**
- FolderListResponse — page of folders and total match
count.

**Response codes**
- 200 — folder list returned.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks**
- HOOK_AFTER_FOLDER_LIST — executed after successful retrieval.

<a id="module-app.routers.folder_select"></a>
## app.routers.folder_select module

FastAPI router for retrieving folder details by ID.

<a id="app.schemas.folder_select.FolderSelectResponse"></a>
### *async* app.routers.folder_select.folder_select(request: Request, folder_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)

Retrieve a single folder by ID and return its details, including
creator info, creation and updateion timestamps, read-only flag,
name, and optional summary.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Response schema:**
- FolderSelectResponse — includes folder ID; creator;
creation and last-update timestamps (Unix seconds, UTC); read-only
flag; normalized name; and optional summary.

**Path parameters:**
- folder_id (integer): identifier of the folder to retrieve.

**Response codes:**
- 200 — folder found; details returned.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder not found.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_FOLDER_SELECT: executed after a successful
retrieval.

<a id="module-app.routers.folder_update"></a>
## app.routers.folder_update module

FastAPI router for updating folder details.

<a id="app.schemas.folder_update.FolderUpdateResponse"></a>
<a id="app.schemas.folder_update.FolderUpdateRequest"></a>
### *async* app.routers.folder_update.folder_update(request: Request, schema: [FolderUpdateRequest](#app.schemas.folder_update.FolderUpdateRequest), folder_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_edit)) → [FolderUpdateResponse](#app.schemas.folder_update.FolderUpdateResponse)

Updates a folder’s properties and, if the name changes, renames
the underlying directory on disk. The operation updates: name,
readonly status, and summary. Changes are performed under an
exclusive folder lock to keep the database and filesystem in
sync. folder names are unique across the application; both the
database and the filesystem are validated before applying changes.

**Authentication:**
- Requires a valid bearer token with editor role or higher.

**Validation schemas:**
- FolderUpdateRequest — optional fields: name, readonly,

> summary.
- FolderUpdateResponse — returns folder_id.

**Path parameters:**
- folder_id (integer ≥ 1) — folder identifier.

**Request body:**
- application/json with any of: name, readonly, summary.

**Response codes:**
- 200 — update successful.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or

> suspended.
- 404 — folder not found.
- 422 — validation error (e.g., name already exists).
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Locks & consistency:**
- Exclusive per-folder lock during the update.
- On rename, directory existence is checked before moving; any
failure triggers a best-effort rollback of the directory move.

**Hooks:**
- HOOK_AFTER_FOLDER_UPDATE — executed after a successful
update.

<a id="module-app.routers.tag_delete"></a>
## app.routers.tag_delete module

FastAPI router for deleting file tags.

<a id="app.schemas.tag_delete.TagDeleteResponse"></a>
### *async* app.routers.tag_delete.tag_delete(request: Request, folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), tag_value: str = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_edit)) → [TagDeleteResponse](#app.schemas.tag_delete.TagDeleteResponse)

Delete a tag from a file and return the file ID with its
latest revision number. The operation is idempotent: if the tag is
absent, the endpoint still returns 200 and leaves the file
unchanged.

**Authentication:**
- Requires a valid bearer token with editor role.

**Path parameters:**
- folder_id (integer ≥ 1): folder identifier.
- file_id (integer ≥ 1): file identifier within the folder.
- tag_value (string, 1-40): tag value to remove; normalized and
validated.

**Response:**
- TagDeleteResponse — returns the file_id and the
latest_revision_number.

**Response codes:**
- 200 — tag removed (or not present; idempotent success).
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder or file not found.
- 422 — invalid tag_value (fails normalization/constraints).
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_TAG_DELETE — executed after successful update.

<a id="module-app.routers.tag_insert"></a>
## app.routers.tag_insert module

FastAPI router for adding file tags.

<a id="app.schemas.tag_insert.TagInsertResponse"></a>
<a id="app.schemas.tag_insert.TagInsertRequest"></a>
### *async* app.routers.tag_insert.tag_insert(request: Request, schema: [TagInsertRequest](#app.schemas.tag_insert.TagInsertRequest), folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_edit)) → [TagInsertResponse](#app.schemas.tag_insert.TagInsertResponse)

Add a new tag to a file and return the file ID with its latest
revision number. If the tag already exists for this file, the
operation is idempotent and no duplicate is created.

**Authentication:**
- Requires a valid bearer token with editor role or higher.

**Validation schemas:**
- TagInsertRequest — request body with a single value field.
The value is normalized/validated by value_validate (NFKC, trim,
lower-case).
- TagInsertResponse — contains the file_id and the
latest_revision_number.

**Path parameters:**
- folder_id (int, ≥1): target folder ID.
- file_id  (int, ≥1): target file ID within the folder.

**Request body:**
- value (string, 1-40): tag value; whitespace-trimmed; normalized.

**Response codes:**
- 201 — tag successfully created (or already present; idempotent).
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — folder or file not found.
- 422 — validation error (path/body).
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Persists a new FileTag and links it to the target file (only if
not already present).

**Hooks:**
- HOOK_AFTER_TAG_INSERT: executed after the tag is ensured on the
file (newly created or already present).

<a id="module-app.routers.telemetry_retrieve"></a>
## app.routers.telemetry_retrieve module

FastAPI router for retrieving telemetry.

### *async* app.routers.telemetry_retrieve.telemetry_retrieve(request: Request, session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_admin))

Retrieves telemetry. Aggregates system metrics and configuration
details.

**Auth:**
- The token must be included in the request header and contain auth
data for an active user with the admin role.

**Returns:**
- TelemetryRetrieveResponse: Telemetry details on success.

**Raises:**
- 200 OK: If telemetry is successfully retrieved.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_TELEMETRY_RETRIEVE: Executes after telemetry is
successfully retrieved.

<a id="module-app.routers.thumbnail_retrieve"></a>
## app.routers.thumbnail_retrieve module

FastAPI router for thumbnail retrieving.

### *async* app.routers.thumbnail_retrieve.thumbnail_retrieve(request: Request, folder_id: int = Path(PydanticUndefined), file_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read))

Retrieve a file’s thumbnail and return raw image bytes. The
image is fetched from the LRU cache first; on miss, it is read from
the filesystem, verified against the stored checksum, and cached.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Path parameters:**
- folder_id (integer ≥ 1): parent folder identifier.
- file_id (integer ≥ 1): file identifier.

**Response:**
- Raw binary image.

**Response codes:**
- 200 — thumbnail returned.
- 304 — not modified (ETag matched).
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or

> suspended.
- 404 — folder or file not found, or no thumbnail set.
- 409 — file not found on filesystem or checksum mismatch.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Reads from the LRU cache or filesystem and saves the bytes into
the LRU cache on cache miss.

**Hooks:**
- HOOK_AFTER_THUMBNAIL_RETRIEVE: executed after successful
thumbnail retrieval.

<a id="module-app.routers.token_invalidate"></a>
## app.routers.token_invalidate module

FastAPI router for invalidating JWT tokens (logout).

<a id="app.schemas.token_invalidate.TokenInvalidateResponse"></a>
### *async* app.routers.token_invalidate.token_invalidate(request: Request, session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [TokenInvalidateResponse](#app.schemas.token_invalidate.TokenInvalidateResponse)

Invalidates the current JWT (logout) by rotating the stored JTI for
the authenticated user. On success, persists the new JTI, triggers
the post-invalidate hook, and returns the user ID. The user will
need to authenticate again to obtain a new valid token.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- TokenInvalidateResponse — confirms logout by returning the user
ID.

**Request body / parameters:**
- None.

**Response codes:**
- 200 — token invalidated; logout successful.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_TOKEN_INVALIDATE: executes after successful token
invalidation.

<a id="module-app.routers.token_retrieve"></a>
## app.routers.token_retrieve module

FastAPI router for issuing JWT tokens (authentication step 2).

<a id="app.schemas.token_retrieve.TokenRetrieveResponse"></a>
<a id="app.schemas.token_retrieve.TokenRetrieveRequest"></a>
### *async* app.routers.token_retrieve.token_retrieve(request: Request, schema: [TokenRetrieveRequest](#app.schemas.token_retrieve.TokenRetrieveRequest), session=Depends(get_session), cache=Depends(get_cache)) → [TokenRetrieveResponse](#app.schemas.token_retrieve.TokenRetrieveResponse)

Completes MFA authentication and issues a JWT access token. Verifies
the username and the provided time-based one-time password (TOTP).
On success, resets the attempt counter, clears the password
acceptance flag, triggers the post-token hook, and returns the user
ID with a signed JWT. On failure, increments attempts and may force
the user to restart authentication from the login step.

**Authentication:**
- Requires successful password authentication (previous login step).

**Validation schemas:**
- TokenRetrieveRequest — request body with username, TOTP, and
optional token expiration.
- TokenRetrieveResponse — contains user ID and JWT token.

**Request body**:
- username (string) — login identifier; automatically trimmed
and lowercased; only Latin letters, digits, and underscore allowed.
- totp (string) — one-time password generated from the MFA secret.
- exp (integer) — custom expiration time in seconds for
the issued JWT.

**Response codes:**
- 200 — TOTP validated; token successfully issued.
- 422 — invalid username, inactive user, user not logged in, or
invalid TOTP.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_TOKEN_RETRIEVE: executes after successful token
retrieval.

<a id="module-app.routers.user_delete"></a>
## app.routers.user_delete module

FastAPI router for deleting user accounts.

<a id="app.schemas.user_delete.UserDeleteResponse"></a>
### *async* app.routers.user_delete.user_delete(request: Request, user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_admin)) → [UserDeleteResponse](#app.schemas.user_delete.UserDeleteResponse)

Deletes a user account by ID. The current user cannot delete their
own account. The user to delete should not have any relationships
with other app objects.

**Authentication:**
- Requires a valid bearer token with the admin role.

**Validation schemas:**
- UserDeleteResponse — confirmation response with the deleted
user’s ID.

**Path parameters:**
- user_id (integer) — unique identifier of the user to delete.

**Response codes:**
- 200 — user successfully deleted.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — user not found.
- 422 — attempted to delete own account or deletion failed.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_DELETE: executes after successful deletion.

<a id="module-app.routers.user_list"></a>
## app.routers.user_list module

FastAPI router for user listing.

<a id="app.schemas.user_list.UserListResponse"></a>
<a id="app.schemas.user_list.UserListRequest"></a>
### *async* app.routers.user_list.user_list(request: Request, schema=Depends(UserListRequest), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [UserListResponse](#app.schemas.user_list.UserListResponse)

Retrieves a paginated list of users with optional filters and ordering.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- UserListRequest — pagination, ordering, and optional filters.
- UserListResponse — list of users and total count.

**Query parameters:**
- Mapped from UserListRequest fields (offset, limit, order_by,
order, and optional filter fields).

**Response codes:**
- 200 — list successfully retrieved.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_LIST: executes after the list is retrieved.

<a id="module-app.routers.user_login"></a>
## app.routers.user_login module

FastAPI router for user login (authentication step 1).

<a id="app.schemas.user_login.UserLoginResponse"></a>
<a id="app.schemas.user_login.UserLoginRequest"></a>
### *async* app.routers.user_login.user_login(request: Request, schema: [UserLoginRequest](#app.schemas.user_login.UserLoginRequest), session=Depends(get_session), cache=Depends(get_cache)) → [UserLoginResponse](#app.schemas.user_login.UserLoginResponse)

Authenticates a user. Verifies credentials and denies access for
suspended or inactive accounts. On success, clears suspension,
resets the attempt counter, triggers the post-login hook, and
returns the user ID with a password acceptance flag; on failure,
increments attempts and may apply a temporary suspension.

**Authentication:**
- No prior authentication required.

**Validation schemas:**
- UserLoginRequest — request body with username and password.
- UserLoginResponse — contains user ID and password acceptance
flag.

**Request body**:
- username (string) — login identifier; automatically trimmed
and lowercased; only Latin letters, digits, and underscore allowed.
- password (string) — login credential.

**Response codes:**
- 200 — user successfully authenticated (password accepted).
- 422 — invalid credentials; user suspended; user inactive.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_LOGIN: executes after successful authentication.

<a id="module-app.routers.user_password"></a>
## app.routers.user_password module

FastAPI router for changing user password.

<a id="app.schemas.user_password.UserPasswordResponse"></a>
<a id="app.schemas.user_password.UserPasswordRequest"></a>
### *async* app.routers.user_password.user_password(request: Request, schema: [UserPasswordRequest](#app.schemas.user_password.UserPasswordRequest), user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [UserPasswordResponse](#app.schemas.user_password.UserPasswordResponse)

Changes the password for the authenticated user. The path user ID
must match the current user, and the new password must differ from
the current password.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- UserPasswordRequest — current and new passwords (new password
must satisfy complexity rules).
- UserPasswordResponse — confirmation with user ID.

**Path parameters:**
- user_id (integer) — ID of the user whose password is updated
(must equal the authenticated user’s ID).

**Response codes:**
- 200 — password successfully changed.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 422 — path user ID mismatch, current password invalid, or new

> password equals the current one.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_PASSWORD: executes after password change.

<a id="module-app.routers.user_register"></a>
## app.routers.user_register module

FastAPI router for user registration.

<a id="app.schemas.user_register.UserRegisterResponse"></a>
<a id="app.schemas.user_register.UserRegisterRequest"></a>
### *async* app.routers.user_register.user_register(request: Request, schema: [UserRegisterRequest](#app.schemas.user_register.UserRegisterRequest), session=Depends(get_session), cache=Depends(get_cache)) → [UserRegisterResponse](#app.schemas.user_register.UserRegisterResponse)

Registers a new user. Checks if the username is unique, and creates
a new user with the provided details and credentials. If this is the
first registered user, they are active and get the admin role;
otherwise created as inactive reader and should be activated by
an admin. On success triggers the post-register hook, and returns
the user ID and one-time MFA secret.

**Authentication:**
- No prior authentication required.

**Validation schemas:**
- UserRegisterRequest — request body with username, password,
first name, last name, and optional summary.
- UserRegisterResponse — contains newly registered user ID and
one-time MFA secret.

**Request body**:
- username (string, 2-40) — login identifier; automatically
trimmed and lowercased; only Latin letters, digits, and underscore
allowed.
- password (string, ≥6) — login credential; must meet complexity
rules — uppercase, lowercase, digit, special character; no
whitespace.
- first_name (string, 1-40) — given first name for the user
profile; accepts any characters.
- last_name (string, 1-40) — given name for the user profile;
accepts any characters.
- summary (string, ≤4096, optional) — profile description; accepts
any characters.

**Response codes:**
- 201 — user successfully created.
- 422 — validation failed or username already exists.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_REGISTER: Executes after the user is
successfully created.

<a id="module-app.routers.user_role"></a>
## app.routers.user_role module

FastAPI router for managing user roles and active status.

<a id="app.schemas.user_role.UserRoleResponse"></a>
<a id="app.schemas.user_role.UserRoleRequest"></a>
### *async* app.routers.user_role.user_role(request: Request, schema: [UserRoleRequest](#app.schemas.user_role.UserRoleRequest), user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_admin)) → [UserRoleResponse](#app.schemas.user_role.UserRoleResponse)

Changes the role and active status of a specific user account.
The current user cannot update their own role or activity status.

**Authentication:**
- Requires a valid bearer token with the admin role.

**Validation schemas:**
- UserRoleRequest — request body containing the new role and
active status values.
- UserRoleResponse — confirmation response with the affected
user’s ID.

**Path parameters:**
- user_id (integer) — unique identifier of the user whose role or
status should be updated.

**Response codes:**
- 200 — user role or active status successfully updated.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — user not found.
- 422 — attempted to change own role or active status.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_ROLE: executes after the user role or active

> status has been updated.

<a id="module-app.routers.user_select"></a>
## app.routers.user_select module

FastAPI router for retrieving user details.

<a id="app.schemas.user_select.UserSelectResponse"></a>
### *async* app.routers.user_select.user_select(request: Request, user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)

Retrieves a single user by ID and returns their details.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- UserSelectResponse — user details: ID, account creation and
last-login times, role, active status, username, first and last
name, optional summary.

**Path parameters:**
- user_id (integer) — unique user identifier.

**Response codes:**
- 200 — user found; details returned.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — user not found.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_SELECT: executes after successful retrieval.

<a id="module-app.routers.user_update"></a>
## app.routers.user_update module

FastAPI router for updating user profile.

<a id="app.schemas.user_update.UserUpdateResponse"></a>
<a id="app.schemas.user_update.UserUpdateRequest"></a>
### *async* app.routers.user_update.user_update(request: Request, schema: [UserUpdateRequest](#app.schemas.user_update.UserUpdateRequest), user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [UserUpdateResponse](#app.schemas.user_update.UserUpdateResponse)

Updates the authenticated user’s profile details (first and last
names and optional summary). The path user ID must match the current
user.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- UserUpdateRequest — first name, last name, optional summary.
- UserUpdateResponse — confirmation with user ID.

**Path parameters:**
- user_id (integer) — ID of the user whose profile is updated
(must equal the authenticated user’s ID).

**Response codes:**
- 200 — profile successfully updated.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 422 — path user ID mismatch.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USER_UPDATE: executes after profile update.

<a id="module-app.routers.userpic_delete"></a>
## app.routers.userpic_delete module

FastAPI router for deleting user image.

<a id="app.schemas.userpic_delete.UserpicDeleteResponse"></a>
### *async* app.routers.userpic_delete.userpic_delete(request: Request, user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [UserpicDeleteResponse](#app.schemas.userpic_delete.UserpicDeleteResponse)

Delete the current user’s userpic and return the user ID. Only the
owner can delete their own userpic.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- UserpicDeleteResponse — contains the user ID.

**Path parameters:**
- user_id (integer): target user ID; must equal the authenticated
user’s ID.

**Response codes:**
- 200 — userpic successfully deleted.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — userpic not found for the user.
- 422 — user ID does not match the authenticated user.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Evicts the thumbnail from the in-memory LRU cache.
- Deletes the file at thumbnails/<filename>.

**Hooks:**
- HOOK_AFTER_USERPIC_DELETE: executed after successful userpic
deletion.

<a id="module-app.routers.userpic_retrieve"></a>
## app.routers.userpic_retrieve module

FastAPI router for userpic retrieving.

### *async* app.routers.userpic_retrieve.userpic_retrieve(request: Request, user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read))

Retrieve a user’s current userpic and return raw image bytes. The
image bytes are fetched from the LRU cache first, and if absent,
read from the filesystem and cached.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Path parameters:**
- user_id (integer ≥ 1): target user identifier.

**Response:**
- Raw binary image.

**Response codes:**
- 200 — userpic returned.
- 304 — not modified (ETag matched).
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 404 — user not found, or no userpic set.
- 409 — file not found on filesystem or checksum mismatch.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Side effects:**
- Reads the image from the LRU cache or filesystem and saves it

> into the LRU cache on cache miss.

**Hooks:**
- HOOK_AFTER_USERPIC_RETRIEVE: executed after successful userpic
retrieval.

<a id="module-app.routers.userpic_upload"></a>
## app.routers.userpic_upload module

FastAPI router for uploading userpics.

<a id="app.schemas.userpic_upload.UserpicUploadResponse"></a>
### *async* app.routers.userpic_upload.userpic_upload(request: Request, data: UploadFile = File(PydanticUndefined), user_id: int = Path(PydanticUndefined), session=Depends(get_session), cache=Depends(get_cache), current_user: [User](#app.models.user.User) = Depends(_can_read)) → [UserpicUploadResponse](#app.schemas.userpic_upload.UserpicUploadResponse)

Uploads a userpic for the authenticated user. The path user ID must
match the current user. The file must be a standard raster image
(JPEG, PNG, GIF, BMP, TIFF, ICO, PBM/PGM/PPM) and will be resized
and re-encoded to JPEG; on success, any previous thumbnail is
deleted and the new image is saved at the configured dimensions
and quality.

**Authentication:**
- Requires a valid bearer token with reader role or higher.

**Validation schemas:**
- UserpicUploadResponse — confirmation with the user ID.

**Path parameters:**
- user_id (integer) — identifier of the user uploading the image.

**Request body:**
- file (multipart/form-data) — image to upload; content type must
be in the configured image MIME allowlist.

**Response codes:**
- 200 — userpic successfully uploaded and stored.
- 401 — missing, invalid, or expired token.
- 403 — insufficient role, invalid JTI, user is inactive or
suspended.
- 422 — path user ID does not match current user or file mimetype
is invalid.
- 423 — application is temporarily locked.
- 498 — gocryptfs key is missing.
- 499 — gocryptfs key is invalid.

**Hooks:**
- HOOK_AFTER_USERPIC_UPLOAD: executes after the image is processed
and saved.

## Module contents
<a id="api/app.schemas.md"></a>
# app.schemas package

<a id="module-app.schemas.file_delete"></a>
## app.schemas.file_delete module

Pydantic schemas for file deletion.

### *class* app.schemas.file_delete.FileDeleteResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for file deletion. Contains the deleted file ID
and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

<a id="app.schemas.userpic_upload.UserpicUploadResponse.model_config"></a>
<a id="app.schemas.userpic_delete.UserpicDeleteResponse.model_config"></a>
<a id="app.schemas.user_update.UserUpdateResponse.model_config"></a>
<a id="app.schemas.user_update.UserUpdateRequest.model_config"></a>
<a id="app.schemas.user_select.UserSelectResponse.model_config"></a>
<a id="app.schemas.user_role.UserRoleResponse.model_config"></a>
<a id="app.schemas.user_role.UserRoleRequest.model_config"></a>
<a id="app.schemas.user_register.UserRegisterResponse.model_config"></a>
<a id="app.schemas.user_register.UserRegisterRequest.model_config"></a>
<a id="app.schemas.user_password.UserPasswordResponse.model_config"></a>
<a id="app.schemas.user_password.UserPasswordRequest.model_config"></a>
<a id="app.schemas.user_login.UserLoginResponse.model_config"></a>
<a id="app.schemas.user_login.UserLoginRequest.model_config"></a>
<a id="app.schemas.user_list.UserListResponse.model_config"></a>
<a id="app.schemas.user_list.UserListRequest.model_config"></a>
<a id="app.schemas.user_delete.UserDeleteResponse.model_config"></a>
<a id="app.schemas.token_retrieve.TokenRetrieveResponse.model_config"></a>
<a id="app.schemas.token_retrieve.TokenRetrieveRequest.model_config"></a>
<a id="app.schemas.token_invalidate.TokenInvalidateResponse.model_config"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.model_config"></a>
<a id="app.schemas.tag_insert.TagInsertResponse.model_config"></a>
<a id="app.schemas.tag_insert.TagInsertRequest.model_config"></a>
<a id="app.schemas.tag_delete.TagDeleteResponse.model_config"></a>
<a id="app.schemas.revision_select.RevisionSelectResponse.model_config"></a>
<a id="app.schemas.folder_update.FolderUpdateResponse.model_config"></a>
<a id="app.schemas.folder_update.FolderUpdateRequest.model_config"></a>
<a id="app.schemas.folder_select.FolderSelectResponse.model_config"></a>
<a id="app.schemas.folder_list.FolderListResponse.model_config"></a>
<a id="app.schemas.folder_list.FolderListRequest.model_config"></a>
<a id="app.schemas.folder_insert.FolderInsertResponse.model_config"></a>
<a id="app.schemas.folder_insert.FolderInsertRequest.model_config"></a>
<a id="app.schemas.folder_delete.FolderDeleteResponse.model_config"></a>
<a id="app.schemas.file_upload.FileUploadResponse.model_config"></a>
<a id="app.schemas.file_update.FileUpdateResponse.model_config"></a>
<a id="app.schemas.file_update.FileUpdateRequest.model_config"></a>
<a id="app.schemas.file_select.FileSelectResponse.model_config"></a>
<a id="app.schemas.file_list.FileListResponse.model_config"></a>
<a id="app.schemas.file_list.FileListRequest.model_config"></a>
<a id="app.schemas.file_delete.FileDeleteResponse.model_config"></a>
#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.file_list"></a>
## app.schemas.file_list module

Pydantic schemas for listing files.

<a id="app.schemas.user_list.UserListRequest.order_by"></a>
<a id="app.schemas.user_list.UserListRequest.order"></a>
<a id="app.schemas.user_list.UserListRequest.offset"></a>
<a id="app.schemas.user_list.UserListRequest.limit"></a>
<a id="app.schemas.folder_list.FolderListRequest.order_by"></a>
<a id="app.schemas.folder_list.FolderListRequest.order"></a>
<a id="app.schemas.folder_list.FolderListRequest.offset"></a>
<a id="app.schemas.folder_list.FolderListRequest.limit"></a>
<a id="app.schemas.file_list.FileListRequest.order_by"></a>
<a id="app.schemas.file_list.FileListRequest.order"></a>
<a id="app.schemas.file_list.FileListRequest.offset"></a>
<a id="app.schemas.file_list.FileListRequest.limit"></a>
### *class* app.schemas.file_list.FileListRequest(, created_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, created_date_\_le: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_le: Annotated[int | None, Ge(ge=0)] = None, user_id_\_eq: Annotated[int | None, Ge(ge=1)] = None, folder_id_\_eq: Annotated[int | None, Ge(ge=1)] = None, flagged_\_eq: bool | None = None, filename_\_ilike: str | None = None, filesize_\_ge: Annotated[int | None, Ge(ge=0)] = None, filesize_\_le: Annotated[int | None, Ge(ge=0)] = None, mimetype_\_ilike: str | None = None, tag_value_\_eq: str | None = None, offset: Annotated[int, Ge(ge=0)] = 0, limit: Annotated[int, Ge(ge=1), Le(le=500)] = 50, order_by: Literal['id', 'created_date', 'updated_date', 'user_id', 'folder_id', 'flagged', 'filename', 'filesize', 'mimetype'] = 'id', order: Literal['asc', 'desc', 'rand'] = 'desc')

Bases: `BaseModel`

Request schema for listing files. Allows filtering by creator,
folder, filename/mimetype (case-insensitive), flagged status,
creation and update time ranges, filesize range, MIME type, tag
value. Supports pagination via offset/limit. Results can be ordered
by id, created/updated date, creator, folder, flagged, filename,
filesize, or mimetype, in ascending, descending, or random order.
Extra fields are forbidden.

#### created_date_\_ge *: int | None*

#### created_date_\_le *: int | None*

#### filename_\_ilike *: str | None*

#### filesize_\_ge *: int | None*

#### filesize_\_le *: int | None*

#### flagged_\_eq *: bool | None*

#### folder_id_\_eq *: int | None*

#### limit *: int*

#### mimetype_\_ilike *: str | None*

#### model_config *: ClassVar[ConfigDict]* *= {'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### offset *: int*

#### order *: Literal['asc', 'desc', 'rand']*

#### order_by *: Literal['id', 'created_date', 'updated_date', 'user_id', 'folder_id', 'flagged', 'filename', 'filesize', 'mimetype']*

#### tag_value_\_eq *: str | None*

#### updated_date_\_ge *: int | None*

#### updated_date_\_le *: int | None*

#### user_id_\_eq *: int | None*

### *class* app.schemas.file_list.FileListResponse(, files: List[[FileSelectResponse](#app.schemas.file_select.FileSelectResponse)], files_count: int)

Bases: `BaseModel`

Response schema for listing files. Contains the selected page
of files and the total number of matches before pagination.

#### files *: List[[FileSelectResponse](#app.schemas.file_select.FileSelectResponse)]*

#### files_count *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.file_select"></a>
## app.schemas.file_select module

Pydantic schemas for file detail retrieval.

<a id="app.schemas.revision_select.RevisionSelectResponse"></a>
### *class* app.schemas.file_select.FileSelectResponse(, id: int, user: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse), folder: [FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse), created_date: int, updated_date: int, flagged: bool, filename: str, filesize: int, mimetype: str | None = None, checksum: str, summary: str | None = None, latest_revision_number: int, file_revisions: List[[RevisionSelectResponse](#app.schemas.revision_select.RevisionSelectResponse)], file_tags: list = None)

Bases: `BaseModel`

Response schema for file details. Includes identifiers, creator,
parent folder, creation/update timestamps, flagged status, filename,
filesize, mimetype, checksum, optional summary, latest revision
number, and a list of file revisions.

#### checksum *: str*

#### created_date *: int*

#### file_revisions *: List[[RevisionSelectResponse](#app.schemas.revision_select.RevisionSelectResponse)]*

#### file_tags *: list*

#### filename *: str*

#### filesize *: int*

#### flagged *: bool*

#### folder *: [FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)*

#### id *: int*

#### latest_revision_number *: int*

#### mimetype *: str | None*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### summary *: str | None*

#### updated_date *: int*

#### user *: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)*

<a id="module-app.schemas.file_update"></a>
## app.schemas.file_update module

Pydantic schemas for file update.

### *class* app.schemas.file_update.FileUpdateRequest(, folder_id: Annotated[int, Ge(ge=1)], filename: Annotated[str, MinLen(min_length=1), MaxLen(max_length=255)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for updating a file. Includes the required filename
and folder ID, plus an optional summary. Whitespace is stripped from
strings; extra fields are forbidden.

#### filename *: str*

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### summary *: str | None*

### *class* app.schemas.file_update.FileUpdateResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for file update. Contains the updated
file ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.file_upload"></a>
## app.schemas.file_upload module

Pydantic schemas for file upload.

### *class* app.schemas.file_upload.FileUploadResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for file upload. Contains the created file
ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.folder_delete"></a>
## app.schemas.folder_delete module

Pydantic schemas for folder deletion.

### *class* app.schemas.folder_delete.FolderDeleteResponse(, folder_id: int)

Bases: `BaseModel`

Response schema for folder deletion. Contains the deleted
folder ID.

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.folder_insert"></a>
## app.schemas.folder_insert module

Pydantic schemas for folder insertion.

### *class* app.schemas.folder_insert.FolderInsertRequest(, readonly: bool, name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=255)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for folder insertion. Includes the read-only
flag, folder name, and an optional summary. Whitespace is
stripped from strings; extra fields are forbidden.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name *: str*

#### readonly *: bool*

#### summary *: str | None*

### *class* app.schemas.folder_insert.FolderInsertResponse(, folder_id: int)

Bases: `BaseModel`

Response schema for folder insertion. Contains the created
folder ID.

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.folder_list"></a>
## app.schemas.folder_list module

Pydantic schemas for listing folders.

### *class* app.schemas.folder_list.FolderListRequest(, user_id_\_eq: Annotated[int | None, Ge(ge=1)] = None, created_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, created_date_\_le: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_le: Annotated[int | None, Ge(ge=0)] = None, readonly_\_eq: bool | None = None, name_\_ilike: str | None = None, offset: Annotated[int, Ge(ge=0)] = 0, limit: Annotated[int, Ge(ge=1), Le(le=500)] = 50, order_by: Literal['id', 'created_date', 'updated_date', 'user_id', 'readonly', 'name'] = 'id', order: Literal['asc', 'desc', 'rand'] = 'desc')

Bases: `BaseModel`

Request schema for listing folders. Allows filtering by creator,
name (case-insensitive), read-only status, and creation/update time
ranges. Supports pagination via offset/limit. Results can be ordered
by id, created/updated date, creator, read-only flag, name, or
filesize, in ascending, descending, or random order. Extra fields
are forbidden.

#### created_date_\_ge *: int | None*

#### created_date_\_le *: int | None*

#### limit *: int*

#### model_config *: ClassVar[ConfigDict]* *= {'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name_\_ilike *: str | None*

#### offset *: int*

#### order *: Literal['asc', 'desc', 'rand']*

#### order_by *: Literal['id', 'created_date', 'updated_date', 'user_id', 'readonly', 'name']*

#### readonly_\_eq *: bool | None*

#### updated_date_\_ge *: int | None*

#### updated_date_\_le *: int | None*

#### user_id_\_eq *: int | None*

### *class* app.schemas.folder_list.FolderListResponse(, folders: List[[FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)], folders_count: int)

Bases: `BaseModel`

Response schema for listing folders. Contains the selected page
of folders and the total number of matches before pagination.

#### folders *: List[[FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)]*

#### folders_count *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.folder_select"></a>
## app.schemas.folder_select module

Pydantic schemas for folder detail retrieval.

### *class* app.schemas.folder_select.FolderSelectResponse(, id: int, created_date: int, updated_date: int, readonly: bool, name: str, summary: str | None = None, user: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse))

Bases: `BaseModel`

Response schema for folder detail retrieval. Includes the
folder ID; creation and last-update timestamps (Unix seconds,
UTC); read-only flag; folder name; optional summary; and
creator details.

#### created_date *: int*

#### id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name *: str*

#### readonly *: bool*

#### summary *: str | None*

#### updated_date *: int*

#### user *: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)*

<a id="module-app.schemas.folder_update"></a>
## app.schemas.folder_update module

Pydantic schemas for folder update.

### *class* app.schemas.folder_update.FolderUpdateRequest(, readonly: bool, name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=255)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for updating a folder. Includes the read-only
flag, folder name, and an optional summary. Whitespace is
stripped from strings; extra fields are forbidden.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name *: str*

#### readonly *: bool*

#### summary *: str | None*

### *class* app.schemas.folder_update.FolderUpdateResponse(, folder_id: int)

Bases: `BaseModel`

Response schema for folder update. Contains the updated folder ID.

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.revision_select"></a>
## app.schemas.revision_select module

Pydantic schemas for revision detail retrieval.

### *class* app.schemas.revision_select.RevisionSelectResponse(, id: int, user: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse), file_id: int, created_date: int, revision_number: int, uuid: str, filesize: int, checksum: str)

Bases: `BaseModel`

Response schema for revision retrieval. Includes the revision ID;
creator data; parent file ID; creation timestamp (Unix seconds,
UTC); revision number; UUID (revision file name); its file size;
and content checksum.

#### checksum *: str*

#### created_date *: int*

#### file_id *: int*

#### filesize *: int*

#### id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### revision_number *: int*

#### user *: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)*

#### uuid *: str*

<a id="module-app.schemas.tag_delete"></a>
## app.schemas.tag_delete module

Pydantic schemas for tag deletion.

### *class* app.schemas.tag_delete.TagDeleteResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for tag delete. Contains the related
file ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.tag_insert"></a>
## app.schemas.tag_insert module

Pydantic schemas for file tag insertion.

### *class* app.schemas.tag_insert.TagInsertRequest(, value: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)])

Bases: `BaseModel`

Request schema for creating a new file tag. The tag value
is validated and cleaned before being processed.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="app.schemas.tag_insert.TagInsertRequest.validate_value"></a>
#### *classmethod* validate_value(value: str) → str

Validate and normalize tag value.

#### value *: str*

### *class* app.schemas.tag_insert.TagInsertResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for tag insert. Contains the related
file ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

<a id="module-app.schemas.telemetry_retrieve"></a>
## app.schemas.telemetry_retrieve module

Pydantic schemas for telemetry retrieve.

<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.unix_timestamp"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.timezone_offset"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.timezone_name"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.sqlite_version"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.sqlite_size"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.redis_version"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.redis_memory"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.python_version"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.python_implementation"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.python_compiler"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.platform_processor"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.platform_architecture"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.platform_alias"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.os_version"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.os_release"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.os_name"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.memory_used"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.memory_total"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.memory_free"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.disk_used"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.disk_total"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.disk_free"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.cpu_usage_percent"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.cpu_frequency"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.cpu_core_count"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.app_version"></a>
<a id="app.schemas.telemetry_retrieve.TelemetryRetrieveResponse"></a>
### *class* app.schemas.telemetry_retrieve.TelemetryRetrieveResponse(, app_version: str, unix_timestamp: int, timezone_name: str, timezone_offset: int, sqlite_version: str, sqlite_size: int, redis_version: str, redis_memory: int, platform_alias: str, platform_architecture: str, platform_processor: str, python_compiler: str, python_implementation: str, python_version: str, os_name: str, os_release: str, os_version: str, disk_total: int, disk_used: int, disk_free: int, memory_total: int, memory_used: int, memory_free: int, cpu_core_count: int, cpu_frequency: int, cpu_usage_percent: float)

Bases: `BaseModel`

Response schema for retrieving telemetry data. Contains information
operating system, database, cache, platform, Python environment,
and resource usage metrics.

#### app_version *: str*

#### cpu_core_count *: int*

#### cpu_frequency *: int*

#### cpu_usage_percent *: float*

#### disk_free *: int*

#### disk_total *: int*

#### disk_used *: int*

#### memory_free *: int*

#### memory_total *: int*

#### memory_used *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### os_name *: str*

#### os_release *: str*

#### os_version *: str*

#### platform_alias *: str*

#### platform_architecture *: str*

#### platform_processor *: str*

#### python_compiler *: str*

#### python_implementation *: str*

#### python_version *: str*

#### redis_memory *: int*

#### redis_version *: str*

#### sqlite_size *: int*

#### sqlite_version *: str*

#### timezone_name *: str*

#### timezone_offset *: int*

#### unix_timestamp *: int*

<a id="module-app.schemas.token_invalidate"></a>
## app.schemas.token_invalidate module

Pydantic schemas for token invalidation.

### *class* app.schemas.token_invalidate.TokenInvalidateResponse(, user_id: int)

Bases: `BaseModel`

Response schema for token invalidation. Confirms that the token
was invalidated for the specified user by returning the user’s
unique identifier.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.token_retrieve"></a>
## app.schemas.token_retrieve module

Pydantic schemas for token retrieval.

### *class* app.schemas.token_retrieve.TokenRetrieveRequest(, username: str, totp: Annotated[str, MinLen(min_length=6), MaxLen(max_length=6)], exp: Annotated[int | None, Ge(ge=1)] = None)

Bases: `BaseModel`

Request schema for token retrieval. Includes the username,
a time-based one-time password (TOTP), and an optional token
lifetime exp — absolute expiration timestamp in Unix seconds;
if omitted, the token is issued without an exp claim (non-expiring).
Extra fields are forbidden.

#### exp *: int | None*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### totp *: str*

#### username *: str*

<a id="app.schemas.token_retrieve.TokenRetrieveResponse.user_token"></a>
### *class* app.schemas.token_retrieve.TokenRetrieveResponse(, user_id: int, user_token: str)

Bases: `BaseModel`

Response schema for token retrieval. Returns the user ID and
a signed JWT access token for authenticated requests.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

#### user_token *: str*

<a id="module-app.schemas.user_delete"></a>
## app.schemas.user_delete module

Pydantic schemas for user deletion.

### *class* app.schemas.user_delete.UserDeleteResponse(, user_id: int)

Bases: `BaseModel`

Response schema for user deletion. Contains the deleted user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.user_list"></a>
## app.schemas.user_list module

Pydantic schemas for listing users.

### *class* app.schemas.user_list.UserListRequest(, created_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, created_date_\_le: Annotated[int | None, Ge(ge=0)] = None, last_login_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, last_login_date_\_le: Annotated[int | None, Ge(ge=0)] = None, active_\_eq: bool | None = None, role_\_eq: Literal['reader', 'writer', 'editor', 'admin'] | None = None, username_\_ilike: str | None = None, first_name_\_ilike: str | None = None, last_name_\_ilike: str | None = None, full_name_\_ilike: str | None = None, offset: Annotated[int, Ge(ge=0)] = 0, limit: Annotated[int, Ge(ge=1), Le(le=500)] = 50, order_by: Literal['id', 'created_date', 'last_login_date', 'role', 'active', 'username', 'first_name', 'last_name', 'full_name'] = 'id', order: Literal['asc', 'desc', 'rand'] = 'desc')

Bases: `BaseModel`

Request schema for listing users. Allows filtering by activity
status and role; by username (case-insensitive); by name fields:
first_name, last_name, full_name (case-insensitive); and by
creation/last-login time ranges. Supports pagination via
offset/limit. Results can be ordered by id, created_date,
last_login_date, role, active, username, first_name, last_name,
or full_name in ascending, descending, or random order.

#### active_\_eq *: bool | None*

#### created_date_\_ge *: int | None*

#### created_date_\_le *: int | None*

#### first_name_\_ilike *: str | None*

#### full_name_\_ilike *: str | None*

#### last_login_date_\_ge *: int | None*

#### last_login_date_\_le *: int | None*

#### last_name_\_ilike *: str | None*

#### limit *: int*

#### model_config *: ClassVar[ConfigDict]* *= {'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### offset *: int*

#### order *: Literal['asc', 'desc', 'rand']*

#### order_by *: Literal['id', 'created_date', 'last_login_date', 'role', 'active', 'username', 'first_name', 'last_name', 'full_name']*

#### role_\_eq *: Literal['reader', 'writer', 'editor', 'admin'] | None*

#### username_\_ilike *: str | None*

### *class* app.schemas.user_list.UserListResponse(, users: List[[UserSelectResponse](#app.schemas.user_select.UserSelectResponse)], users_count: int)

Bases: `BaseModel`

Response schema for listing users. Contains the selected page
of users and the total number of matches before pagination.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### users *: List[[UserSelectResponse](#app.schemas.user_select.UserSelectResponse)]*

#### users_count *: int*

<a id="module-app.schemas.user_login"></a>
## app.schemas.user_login module

Pydantic schemas for user login.

### *class* app.schemas.user_login.UserLoginRequest(, username: str, password: SecretStr)

Bases: `BaseModel`

Request schema for user login. Carries the username and password
used to authenticate the account; the username is trimmed and
lowercased (Latin letters, digits, underscore). Extra fields
are forbidden.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### password *: SecretStr*

#### username *: str*

### *class* app.schemas.user_login.UserLoginResponse(, user_id: int, password_accepted: bool)

Bases: `BaseModel`

Response schema for user login. Returns the user ID and a flag
indicating that the password step was accepted and the flow may
proceed to MFA.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### password_accepted *: bool*

#### user_id *: int*

<a id="module-app.schemas.user_password"></a>
## app.schemas.user_password module

Pydantic schemas for password change.

<a id="app.schemas.user_password.UserPasswordRequest.updated_password"></a>
<a id="app.schemas.user_password.UserPasswordRequest.current_password"></a>
### *class* app.schemas.user_password.UserPasswordRequest(, current_password: Annotated[str, MinLen(min_length=6)], updated_password: Annotated[str, MinLen(min_length=6)])

Bases: `BaseModel`

Request schema for changing a user’s password. Requires the current
password and a new password. Whitespace is stripped from strings;
extra fields are forbidden.

#### current_password *: str*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### updated_password *: str*

### *class* app.schemas.user_password.UserPasswordResponse(, user_id: int)

Bases: `BaseModel`

Response schema for password change. Contains the user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.user_register"></a>
## app.schemas.user_register module

Pydantic schemas for user registration.

### *class* app.schemas.user_register.UserRegisterRequest(, username: Annotated[str, MinLen(min_length=2), MaxLen(max_length=40)], password: Annotated[SecretStr, MinLen(min_length=6)], first_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], last_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for user registration request with validation
of username, password, names, and optional profile summary.
Extra fields are forbidden.

#### first_name *: str*

#### last_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### password *: SecretStr*

#### summary *: str | None*

#### username *: str*

### *class* app.schemas.user_register.UserRegisterResponse(, user_id: int, mfa_secret: str)

Bases: `BaseModel`

Response schema for user registration response including assigned
user ID and MFA secret string.

#### mfa_secret *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.user_role"></a>
## app.schemas.user_role module

Pydantic schemas for user role update.

### *class* app.schemas.user_role.UserRoleRequest(, role: Literal['reader', 'writer', 'editor', 'admin'], active: bool)

Bases: `BaseModel`

Request schema for updating a user’s role and active status.
Includes the new role (reader|writer|editor|admin) and an activity
status. Whitespace is stripped from strings. Extra fields are
forbidden.

#### active *: bool*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### role *: Literal['reader', 'writer', 'editor', 'admin']*

<a id="app.schemas.user_role.UserRoleRequest.validate_role"></a>
#### *classmethod* validate_role(value: str) → str

### *class* app.schemas.user_role.UserRoleResponse(, user_id: int)

Bases: `BaseModel`

Response schema for user role update. Contains the user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.user_select"></a>
## app.schemas.user_select module

Pydantic schemas for user detail retrieval.

### *class* app.schemas.user_select.UserSelectResponse(, id: int, created_date: int, last_login_date: int, role: Literal['reader', 'writer', 'editor', 'admin'], active: bool, username: str, first_name: str, last_name: str, summary: str | None = None, has_thumbnail: bool)

Bases: `BaseModel`

Response schema for user details. Includes identifiers, creation
and last-login timestamps, role, active status, username, first/last
name, optional summary, and thumbnail presence flag.

#### active *: bool*

#### created_date *: int*

#### first_name *: str*

#### has_thumbnail *: bool*

#### id *: int*

#### last_login_date *: int*

#### last_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### role *: Literal['reader', 'writer', 'editor', 'admin']*

#### summary *: str | None*

#### username *: str*

<a id="module-app.schemas.user_update"></a>
## app.schemas.user_update module

Pydantic schemas for user update.

### *class* app.schemas.user_update.UserUpdateRequest(, first_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], last_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for updating a user profile. Requires first and last
name; summary is optional. Whitespace is stripped from strings;
extra fields are forbidden.

#### first_name *: str*

#### last_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### summary *: str | None*

### *class* app.schemas.user_update.UserUpdateResponse(, user_id: int)

Bases: `BaseModel`

Response schema for user update. Contains the updated user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.userpic_delete"></a>
## app.schemas.userpic_delete module

Pydantic schemas for userpic deletion.

### *class* app.schemas.userpic_delete.UserpicDeleteResponse(, user_id: int)

Bases: `BaseModel`

Response schema for userpic deletion. Contains the user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

<a id="module-app.schemas.userpic_upload"></a>
## app.schemas.userpic_upload module

Pydantic schemas for uploading a user’s image.

### *class* app.schemas.userpic_upload.UserpicUploadResponse(, user_id: int)

Bases: `BaseModel`

Response schema confirming a successful user image upload by
returning the unique identifier of the affected user account.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## Module contents
<a id="api/app.validators.md"></a>
<a id="module-app.validators"></a>
# app.validators package

<a id="module-app.validators.file_validators"></a>
## app.validators.file_validators module

Cross-platform validators for names and summaries used in a file storage
context. The name checker normalizes Unicode, trims whitespace, rejects
special path components, filters out control and portability-breaking
characters, forbids trailing dots and platform-reserved basenames, and
enforces a 255-byte UTF-8 limit to match common filesystem constraints.
The summary helper applies a minimal normalization pass that strips
surrounding whitespace and converts empty strings to null, ensuring
consistent optional metadata handling.

<a id="app.validators.file_validators.name_validate"></a>
### app.validators.file_validators.name_validate(name: str) → str

Validates name used as a single component by trimming surrounding
whitespace and ensuring the result is not empty, rejecting the
special components ‘.’ and ‘..’, forbidding characters that are
problematic across platforms as well as any ASCII control characters
including NUL, disallowing a trailing dot and Windows-reserved names
regardless of extension, and enforcing a maximum of 255 bytes when
encoded in UTF-8. The value is Unicode-normalized to NFC prior to
the byte-length check, and the normalized name is returned.

<a id="app.validators.user_validators.summary_validate"></a>
<a id="app.validators.folder_validators.summary_validate"></a>
<a id="app.validators.file_validators.summary_validate"></a>
### app.validators.file_validators.summary_validate(summary: str | None) → str | None

Validates file summary by trimming whitespace and converting
blank strings to None. Returns the normalized file summary.

<a id="module-app.validators.folder_validators"></a>
## app.validators.folder_validators module

Validators for folder metadata. Provides a simple normalization pass for
textual summaries that trims surrounding whitespace and converts blank
input to a null value.

### app.validators.folder_validators.summary_validate(summary: str | None) → str | None

Validates summary by trimming whitespace and converting blank
strings to None. Returns the normalized summary.

<a id="module-app.validators.tag_validators"></a>
## app.validators.tag_validators module

Validator for free-form tag values that enforces a canonical,
search-friendly representation. Input is Unicode-normalized,
whitespace is trimmed, and case is folded to achieve consistent
comparisons across locales. Blank or purely whitespace input is
rejected to prevent meaningless records.

<a id="app.validators.tag_validators.value_validate"></a>
### app.validators.tag_validators.value_validate(value: str) → str

Normalize to NFKC, trim, and lower-case; reject empty.

<a id="module-app.validators.user_validators"></a>
## app.validators.user_validators module

Validators for user input in authentication and profiles: lowercases
and restricts usernames to letters, digits, and underscores; enforces
passwords with mixed case, digits, and punctuation while forbidding
spaces; trims and lowercases roles without asserting membership; accepts
digit-only TOTP codes; and normalizes summaries by stripping whitespace
and collapsing blanks to null.

<a id="app.validators.user_validators.password_validate"></a>
### app.validators.user_validators.password_validate(password: str) → str

Validates password by disallowing spaces and requiring lowercase,
uppercase, digit, and special character.

<a id="app.validators.user_validators.role_validate"></a>
### app.validators.user_validators.role_validate(role: str) → str

Normalizes a role string without validating membership. Strips
leading/trailing whitespace and lowercases the value.

### app.validators.user_validators.summary_validate(summary: str | None) → str | None

Validates summary by trimming whitespace and converting blank
strings to None.

<a id="app.validators.user_validators.totp_validate"></a>
### app.validators.user_validators.totp_validate(totp: str)

The one-time password must contain only digits.

<a id="app.validators.user_validators.username_validate"></a>
### app.validators.user_validators.username_validate(username: str) → str

Validates username by lowercasing and ensuring only lowercase
letters, digits, or underscore are allowed.
