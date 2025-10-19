# app.helpers package

## app.helpers.image_helper module

Utilities for deterministic image processing. Provides an asynchronous
resize routine that runs in a worker thread, normalizes orientation from
embedded metadata, converts to an appropriate color mode, center-crops
to match the requested aspect ratio, resamples with a high-quality
filter, and overwrites the original file using an optimized progressive
encoding. It also centralizes the set of accepted input formats and the
preferred media type for downstream validation and content negotiation.

### *async* app.helpers.image_helper.image_resize(path: str, width: int, height: int, quality: int)

Asynchronously runs the sync resizer in a worker thread: applies
EXIF orientation, center-crops to the target aspect ratio, resizes
with Lanczos, and overwrites the file as a progressive JPEG.

## app.helpers.jwt_helper module

Utilities for working with JSON Web Tokens: generates stable,
collision-resistant token identifiers, assembles signed claim sets
for authenticated users (including issued-at and optional expiry),
produces compact encoded tokens, and verifies and parses incoming
tokens with signature and standard claim validation.

### app.helpers.jwt_helper.create_payload(user: [User](app.models.md#app.models.user.User), jti: str, exp: int = None)

Builds a JWT claims payload for the given user including user_id,
role, username, jti, and iat (Unix seconds); if exp is provided it
is used as an absolute expiration timestamp, otherwise the payload
is created without an exp claim.

### app.helpers.jwt_helper.decode_jwt(jwt_token: str, jwt_secret: str, jwt_algorithms: list) → dict

Decodes a JWT using the given secret and allowed algorithms,
validating the signature and standard claims (such as exp and iat)
and returning the claims dictionary, raising PyJWT exceptions on
invalid or expired tokens.

### app.helpers.jwt_helper.encode_jwt(payload: dict, jwt_secret: str, jwt_algorithm: str) → str

Encodes and signs the given claims payload into a compact JWT using
the supplied secret and algorithm via PyJWT.

### app.helpers.jwt_helper.generate_jti(key_length: int) → str

Generates a cryptographically random alphanumeric JTI of the given
length for uniquely identifying and potentially revoking tokens.

## app.helpers.mfa_helper module

Utilities for time-based one-time passwords used in multi-factor auth.
Provides a secure generator for random Base32 secrets and a helper to
compute the current OTP from a supplied secret, following standard TOTP
conventions so the codes interoperate with common authenticator apps.
Includes minimal input validation and avoids retaining state or
sensitive material beyond the returned values.

### app.helpers.mfa_helper.calculate_totp(mfa_secret: str)

Computes the current time-based one-time password derived from
the provided Base32 secret, compatible with standard TOTP apps.

### app.helpers.mfa_helper.generate_mfa_secret() → str

Generates and returns a random base32-encoded secret suitable
for use with time-based one-time password (TOTP) MFA systems.

## app.helpers.thumbnail_mixin module

Lightweight mixin for deriving absolute filesystem locations of
thumbnail artifacts from a UUID and an application configuration.
It provides a class utility to compute the path for an arbitrary
identifier and an instance-level convenience that delegates to the
same logic. The helpers are deterministic, side-effect free, and
keep storage layout concerns decoupled from the model.

### *class* app.helpers.thumbnail_mixin.ThumbnailMixin

Bases: `object`

Build absolute paths to thumbnail files.

#### path(config: Any) → str

Return absolute path to the thumbnail file by its UUID.

#### *classmethod* path_for_uuid(config: Any, uuid: str) → str

Return absolute path for a given UUID using config.

## Module contents
