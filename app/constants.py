# app/constants.py
# SPDX-License-Identifier: Apache-2.0

# NOTE (ADR-01): Naming and code style conventions follow PEP 8.
# 1. Code style follows PEP 8 with line length limits: 79 characters
#    for code and 72 characters for comments, enforced with flake8.
# 2. File names use `<resource>_<action>` to group related logic by
#    domain resource and improve locality in listings.
# 3. Function names use `<action>_<resource>` to preserve natural
#    reading order and improve readability.

HIDDEN_TITLE = "Hidden S3 — encrypted self-hosted S3 storage"

GOCRYPTFS_PASSPHRASE_LENGTH = 80
GOCRYPTFS_PASSPHRASE_FILENAME = "gocryptfs_passphrase.enc"

WATCHDOG_HEARTBEAT_PATH = "/tmp/gocryptfs-watchdog.touch"

VERSITY_ACCESS_KEY_LENGTH = 20
VERSITY_ACCESS_KEY_FILENAME = "versity_access.key"

VERSITY_SECRET_KEY_LENGTH = 40
VERSITY_SECRET_KEY_FILENAME = "versity_secret.key"

VERSITY_DATA_DIRNAME = "data"
VERSITY_IAM_DIRNAME = "iam"
