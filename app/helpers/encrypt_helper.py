"""
The module provides functions for encrypting and decrypting data of
types such as bytes, strings, integers, and booleans using AES
encryption with PBKDF2 key derivation. It also includes functionality
for generating cryptographic salts and hashing string values using
the SHA-512 algorithm.

Original | Encrypted
length   | length
---------|----------
15       | 64
31       | 88
47       | 108
63       | 128
79       | 152
95       | 172
111      | 192
127      | 216
255      | 384
511      | 728
1023     | 1408
2047     | 2776
4095     | 5504
16383    | 21888
32767    | 43736
"""

import os
import base64
import hashlib
from typing import Union
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from app.config import get_config
from app.context import get_context

cfg = get_config()
ctx = get_context()


def generate_encryption_salt() -> bytes:
    """
    Generates a random byte sequence to be used as a salt for AES key
    derivation.
    """
    return os.urandom(cfg.CRYPTOGRAPHY_SALT_LENGTH)


def extract_aes_key(secret_key: str, salt: bytes) -> bytes:
    """
    Derives a cryptographic AES key from a given secret string and salt
    using the PBKDF2 algorithm with HMAC-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=cfg.CRYPTOGRAPHY_KEY_LENGTH,
        salt=salt, iterations=cfg.CRYPTOGRAPHY_PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(secret_key.encode())


def encrypt_bytes(data: bytes = None) -> Union[bytes, None]:
    """
    Encrypts a byte sequence using AES in CBC mode with PKCS7 padding
    and returns the encrypted data, which includes the salt, IV, and
    ciphertext.
    """
    if data is None:
        return None

    salt = generate_encryption_salt()
    iv = os.urandom(cfg.CRYPTOGRAPHY_IV_LENGTH)
    key = extract_aes_key(ctx.secret_key, salt)

    algorithm = algorithms.AES(key)
    mode = modes.CBC(iv)

    cipher = Cipher(algorithm, mode, backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_data = salt + iv + ciphertext
    return encrypted_data


def decrypt_bytes(encrypted_data: bytes = None) -> Union[bytes, None]:
    """
    Decrypts a byte sequence previously encrypted with AES by extracting
    the salt and IV, deriving the key, and removing padding from the
    plaintext.
    """
    if encrypted_data is None:
        return None

    # Extract the salt and IV from the encrypted data
    salt = encrypted_data[:cfg.CRYPTOGRAPHY_SALT_LENGTH]
    iv = encrypted_data[
        cfg.CRYPTOGRAPHY_SALT_LENGTH:cfg.CRYPTOGRAPHY_SALT_LENGTH +
        cfg.CRYPTOGRAPHY_IV_LENGTH]
    ciphertext = encrypted_data[
        cfg.CRYPTOGRAPHY_SALT_LENGTH + cfg.CRYPTOGRAPHY_IV_LENGTH:]

    # Derive the AES key using the salt
    key = extract_aes_key(ctx.secret_key, salt)

    cipher = Cipher(
        algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt and unpad the ciphertext
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data


def encrypt_str(value: str = None) -> Union[str, None]:
    """
    Encrypts a string using AES and returns the result as a
    base64-encoded string.
    """
    if value is None:
        return None

    encrypted_data = encrypt_bytes(value.encode())
    return base64.b64encode(encrypted_data).decode("utf-8")


def decrypt_str(encrypted_data: str = None) -> Union[str, None]:
    """
    Decodes a base64-encoded encrypted string, decrypts it using AES,
    and returns the original string.
    """
    if encrypted_data is None:
        return None

    encrypted_bytes = base64.b64decode(encrypted_data)
    decrypted_data = decrypt_bytes(encrypted_bytes)
    return decrypted_data.decode()


def encrypt_int(value: int = None) -> Union[str, None]:
    """
    Encrypts an integer by converting it to a string and applying string
    encryption, returning a base64-encoded result.
    """
    if value is None:
        return None

    return encrypt_str(str(value))


def decrypt_int(encrypted_value: str = None) -> Union[str, None]:
    """
    Decrypts a base64-encoded string representing an encrypted integer
    and returns the original integer value.
    """
    if encrypted_value is None:
        return None

    return int(decrypt_str(encrypted_value))


def encrypt_bool(value: bool = None) -> Union[str, None]:
    """
    Encrypts a boolean value by converting it to an integer and
    encrypting the result as a base64-encoded string.
    """
    if value is None:
        return None

    return encrypt_int(int(value))


def decrypt_bool(encrypted_value: bool = None) -> Union[bool, None]:
    """
    Decrypts a base64-encoded string representing an encrypted boolean
    and returns the original boolean value.
    """
    if encrypted_value is None:
        return None

    return bool(decrypt_int(encrypted_value))


def hash_str(value: str = None) -> Union[str, None]:
    """
    Hashes a string concatenated with the application's secret key using
    SHA-512 and returns the hexadecimal digest.
    """
    if value is None:
        return None

    encoded_value = (value + ctx.secret_key).encode()
    hash = hashlib.sha512(encoded_value)
    return hash.hexdigest()
