# app/constants.py
# SPDX-License-Identifier: SSPL-1.0

# NOTE (ADR-01): Naming and code style conventions.
# 1. File names use `<resource>_<action>` to group related logic by
#    domain resource and improve locality in listings.
# 2. Function names use `<action>_<resource>` to preserve natural
#    reading order and improve readability.
# 3. Code style follows PEP 8 with line length limits: 79 characters
#    for code and 72 characters for comments, enforced with flake8.
# 4. Path-related constants follow strict suffix conventions (these
#    suffixes are not interchangeable and must be used consistently):
#    *_PATH     - absolute file path
#    *_DIR      - absolute directory path
#    *_DIRNAME  - relative directory name
#    *_FILENAME - relative filename

# Watchdog heartbeat file and drain timeout before unmount.
# Used for liveness checks and emergency unmount coordination.
WATCHDOG_HEARTBEAT_PATH = "/tmp/hidden-watchdog.touch"
WATCHDOG_GRACEFUL_UNMOUNT_SECONDS = 5

# Lockdown mode control flag.
# Presence of this file blocks the app and returns HTTP 503.
LOCKDOWN_MODE_ENABLED_FLAG_PATH = "/tmp/hidden-lockdown-mode.lock"

# Master password used to encrypt the gocryptfs passphrase.
# Defines minimum required length for this encryption password.
MASTER_PASSWORD_MIN_LENGTH = 16

# Minimum interval between master-password attempts in one process.
# Brute-force resistance still relies primarily on entropy and crypto cost.
MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS = 2

# Fernet key file for internal encryption.
# Stores the symmetric key used for data encryption.
FERNET_KEY_FILENAME = "fernet.key"

# JWT signing key configuration.
# Defines key file location and required key length.
JWT_SIGNING_KEY_FILENAME = "jwt_signing.key"
JWT_SIGNING_KEY_LENGTH = 40

# gocryptfs integration and filesystem structure.
# Defines encryption params and mount layout.
GOCRYPTFS_PASSPHRASE_LENGTH = 80
GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME = "gocryptfs_passphrase.enc"
GOCRYPTFS_CIPHER_DIRNAME = "cipherdir"
GOCRYPTFS_MOUNTPOINT_DIRNAME = "mountpoint"
GOCRYPTFS_CIPHERDIR_LOCK_PATH = "/tmp/hidden-gocryptfs-cipherdir.lock"

# SQLite storage inside encrypted filesystem.
# Defines DB directory and database filename.
SQLITE_DIRNAME = "db"
SQLITE_FILENAME = "hidden.db"

# File processing and detection parameters.
# Defines chunk size and MIME sniffing limits.
FILE_CHUNK_SIZE_BYTES = 1024 * 64
FILE_MIMETYPE_READ_BYTES = 1024 * 16
FILE_THUMBNAIL_SIZE = (256, 256)
FILES_DIRNAME = "files"
FILES_REVISIONS_DIRNAME = "revisions"
FILES_THUMBNAILS_DIRNAME = "thumbnails"
FILES_TMP_DIRNAME = "tmp"
FILES_MAX_FOLDER_DEPTH = 32
FILES_MAX_PATH_LENGTH_BYTES = 4096

# First admin bootstrap marker (secrets volume).
# Presence indicates initial admin registration completed; readable
# without cipherdir mount for onboarding UX (see app/config.py path).
FIRST_ADMIN_CREATED_FLAG_FILENAME = "first_admin_created.flag"

# Authentication failure limits and verification policy.
# Defines allowed failed attempts for password and TOTP,
# temporary suspension duration, and password verification TTL.
AUTH_FIRST_ADMIN_LOCK_FLAG_PATH = "/tmp/hidden-first-admin.lock"
AUTH_FAILED_PASSWORD_ATTEMPTS = 20
AUTH_FAILED_TOTP_ATTEMPTS = 20
AUTH_FAILED_RECOVERY_CODE_ATTEMPTS = 20
AUTH_FAILED_SUSPEND_SECONDS = 30
AUTH_PASSWORD_VERIFIED_TTL_SECONDS = 120

REGISTER_ATTEMPTS_LIMIT = 200
REGISTER_ATTEMPTS_WINDOW_SECONDS = 60

OBSCURED_VALUE = "*" * 8
