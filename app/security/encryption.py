# app/security/encryption.py
# SPDX-License-Identifier: SSPL-1.0

import os
import struct
from functools import lru_cache

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from app.config import get_config

_MAGIC = b"HENC"
_VERSION: int = 1
_SALT_LEN: int = 16
_NONCE_LEN: int = 12
_KEY_LEN: int = 32
_HEADER_LEN: int = 4 + 1 + _SALT_LEN + _NONCE_LEN

_SCRYPT_N: int = 2**15
_SCRYPT_R: int = 8
_SCRYPT_P: int = 1


def _derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=_KEY_LEN,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
    )
    return kdf.derive(password)


def encrypt_passphrase(plaintext: bytes, password: bytes) -> bytes:
    """Encrypt plaintext with password; return an opaque blob."""
    if not plaintext:
        raise ValueError("plaintext must not be empty")
    if not password:
        raise ValueError("password must not be empty")
    salt = os.urandom(_SALT_LEN)
    nonce = os.urandom(_NONCE_LEN)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    body = aesgcm.encrypt(nonce, plaintext, None)
    return (
        _MAGIC
        + struct.pack("B", _VERSION)
        + salt
        + nonce
        + body
    )


def decrypt_passphrase(ciphertext: bytes, password: bytes) -> bytes:
    """Decrypt a blob produced by encrypt function."""
    if not ciphertext:
        raise ValueError("ciphertext must not be empty")
    if not password:
        raise ValueError("password must not be empty")
    if len(ciphertext) < _HEADER_LEN + 1:
        raise ValueError("ciphertext too short")
    if ciphertext[:4] != _MAGIC:
        raise ValueError("invalid magic")
    version = ciphertext[4]
    if version != _VERSION:
        raise ValueError("unsupported version")
    salt = ciphertext[5:5 + _SALT_LEN]
    nonce = ciphertext[5 + _SALT_LEN:_HEADER_LEN]
    body = ciphertext[_HEADER_LEN:]
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, body, None)
    except Exception:
        raise ValueError(
            "invalid password or corrupted data",
        ) from None


def generate_fernet_key() -> str:
    return Fernet.generate_key().decode()


@lru_cache(maxsize=1)
def get_fernet() -> Fernet:
    config = get_config()
    return Fernet(config.FERNET_KEY.encode())


def encrypt_string(value: str) -> str:
    return get_fernet().encrypt(value.encode()).decode()


def decrypt_string(value: str) -> str:
    return get_fernet().decrypt(value.encode()).decode()
