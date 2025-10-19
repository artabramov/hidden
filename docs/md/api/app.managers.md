# app.managers package

## app.managers.cache_manager module

Redis-backed cache manager for SQLAlchemy ORM entities. Provides
TTL-based caching of ORM instances, lookup by model and primary key,
bulk invalidation per model, and full-database flush, using SQLAlchemy’s
binary serialization format.

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

#### *async* erase() → None

Clears all cached entries from Redis cache.

#### *async* get(cls: Type[DeclarativeBase], entity_id: int | str) → DeclarativeBase | None

Retrieves an SQLAlchemy model instance from the Redis cache by
fetching the serialized model from Redis and deserializing it.

#### *async* set(entity: DeclarativeBase) → None

Caches an SQLAlchemy model instance by serializing it and
storing it in Redis cache with an expiration time.

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

### *class* app.managers.encryption_manager.EncryptionManager(config: [Config](app.md#app.config.Config), gocryptfs_key: str | bytes)

Bases: `object`

Coordinates symmetric encryption primitives behind a simple API.
Accepts configuration and a gocryptfs at construction.

#### decrypt_bool(token: str = None) → bool | None

Decrypts a base64 token and maps the integer back to a boolean.
Treats nonzero values as True and zero as False.

#### decrypt_bytes(payload: bytes = None) → bytes | None

Decrypts bytes produced by this encryptor and verifies
authenticity.

#### decrypt_int(token: str = None) → int | None

Decrypts a base64 token and parses the original integer value.
Raises on invalid numeric form as part of fail-fast behavior.

#### decrypt_str(token: str = None) → str | None

Decrypts a base64 text produced by the string encryptor. Returns
the original text decoded with the configured charset.

#### encrypt_bool(value: bool = None) → str | None

Encrypts a boolean by mapping to an integer and using string
encryption. Returns a base64 token consistent with other scalar
helpers.

#### encrypt_bytes(data: bytes = None) → bytes | None

Encrypts bytes and returns nonce||ciphertext (tag included).

#### encrypt_int(value: int = None) → str | None

Encrypts an integer by converting to text and using string
encryption. Returns a base64 token suitable for storage or
transport.

#### encrypt_str(value: str = None) → str | None

Encrypts text by encoding with the configured charset and
base64-wrapping the result. Returns a textual envelope of
the binary ciphertext.

#### get_hash(value: str) → str

Computes an HMAC-SHA-512 over the given value using
a MAC-dedicated key. Returns a lowercase hexadecimal digest.

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

#### *async* select_by(cls: Type[DeclarativeBase], \*\*kwargs) → DeclarativeBase | None

Fetches a single entity using filter criteria. Returns
the first match or None when nothing qualifies.

#### *async* select_rows(sql: str) → list

Executes a textual statement and returns raw result rows.

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

## app.managers.file_manager module

Asynchronous file utilities for atomic writes, chunked I/O, and
multiple-pass overwrite deletion via a system tool. Favors fail-fast
behavior with minimal policy, leaving durability and higher-level
error handling to callers.

### *class* app.managers.file_manager.FileManager(config: [Config](app.md#app.config.Config))

Bases: `object`

Provides asynchronous file operations with atomic writes and
chunked I/O. Favors fail-fast behavior and avoids durability
guarantees beyond OS buffering.

#### *async* checksum(path: str) → str

Computes and returns the SHA-256 hex digest of a file
asynchronously by streaming it in chunks.

#### *async* copy(src_path: str, dst_path: str) → None

Copies a file by streaming bytes and atomically replacing the
destination. Creates parent directories as needed and avoids
exposing partial results.

#### *async* delete(path: str) → None

Runs a system tool that overwrites a file in multiple passes and
unlinks it. Waits for completion and performs the operation only
if a regular file is present.

#### *async* filesize(path: str) → int

Returns the size of a file in bytes via an async stat call.
Lets OS errors propagate (e.g., missing path).

#### *async* isdir(path: str) → bool

Checks whether a path refers to an existing directory. Runs
asynchronously and returns False for files, non-existing paths,
and symlinks that don’t point to a directory.

#### *async* isfile(path: str) → bool

Checks whether a path refers to an existing regular file.
Runs asynchronously and ignores non-file filesystem entries.

#### *async* mimetype(path: str) → str | None

Detect MIME type by file content (libmagic), then by signature
(filetype), and finally by filename extension as a fallback.

#### *async* mkdir(path: str, is_file: bool = False) → None

Ensure required directories exist. For file paths, create parent
directories; for directory paths, create the directory itself.
Intermediate directories are created as needed; existing ones
are left untouched.

#### *async* read(path: str) → bytes

Reads the entire contents of a file into memory. Suitable for
small to medium inputs; consider streaming for large data.

#### *async* rename(src_path: str, dst_path: str) → None

Atomically moves or renames a file, overwriting any existing
target. Creates the destination’s parent directory when missing
and completes in one step.

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
