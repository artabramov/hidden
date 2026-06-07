# app/runtime/passphrase.py
# SPDX-License-Identifier: SSPL-1.0

import argparse
import getpass
import os
import sys

from app.constants import GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME
from app.security.encryption import decrypt_passphrase

# NOTE (ADR-05): gocryptfs passphrase is stored encrypted.
# The passphrase is protected with a master password and is never
# persisted in plaintext on disk. It is only decrypted in memory for
# the mount operation and is not retained after mount completes. This
# adds a second protection layer: access to data requires both the
# passphrase and the master password.

_CLI_EPILOG = """
Emergency decryption: read HENC blob from path, decrypt with a password
typed at the terminal (no echo), write plaintext to standard output.

The path argument is optional. When omitted, the path is derived from the
INSTALL_SECRETS_DIR environment variable. The master password is read
interactively (no echo). Output goes to stdout; redirect to a file if needed.

Example (path from INSTALL_SECRETS_DIR env):
  python3 -m app.runtime.passphrase

Example (explicit path, print to terminal):
  python3 -m app.runtime.passphrase ./passphrase.enc

Example (explicit path, save to file):
  python3 -m app.runtime.passphrase ./passphrase.enc > ./passphrase.key
""".strip()


def _print_decrypt_value_error(exc: ValueError) -> None:
    """Map decrypt errors to stderr messages."""
    msg = str(exc)
    if msg == "invalid password or corrupted data":
        print(
            "Decryption failed: wrong password, or the file is corrupted "
            "or not an encrypted key file.",
            file=sys.stderr,
        )
    elif msg == "ciphertext too short":
        print(
            "This file is too small to be a valid encrypted key file.",
            file=sys.stderr,
        )
    elif msg == "invalid magic":
        print(
            "This file does not look like an encrypted key file.",
            file=sys.stderr,
        )
    elif msg == "unsupported version":
        print(
            "This encrypted key file uses an unsupported format version.",
            file=sys.stderr,
        )
    else:
        print(f"Decryption failed: {msg}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="passphrase",
        description="Decrypt key material with a password (emergency use).",
        epilog=_CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help=(
            "Path to encrypted blob. When omitted, derived from "
            "INSTALL_SECRETS_DIR environment variable."
        ),
    )
    args = parser.parse_args(argv)

    if args.path is not None:
        path = args.path
    else:
        secrets_dir = os.environ.get("INSTALL_SECRETS_DIR")
        if not secrets_dir:
            print(
                "No path given and INSTALL_SECRETS_DIR is not set.",
                file=sys.stderr,
            )
            return 1
        path = os.path.join(
            secrets_dir,
            GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME
        )

    try:
        with open(path, "rb") as f:
            blob = f.read()
    except OSError as exc:
        print(f"Could not read file: {exc}", file=sys.stderr)
        return 1

    password = getpass.getpass("Enter master password: ").encode("utf-8")

    try:
        plaintext = decrypt_passphrase(blob, password)
    except ValueError as exc:
        _print_decrypt_value_error(exc)
        return 1

    sys.stdout.buffer.write(plaintext)
    if sys.stdout.isatty():
        sys.stdout.buffer.write(b"\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
