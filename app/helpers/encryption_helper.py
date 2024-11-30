"""
The module provides functions for encrypting and decrypting data using
AES encryption with PBKDF2 key derivation. It includes utilities for
generating a random salt, deriving an AES key from a password and salt,
encrypting and decrypting both bytes and string values, and returning
encrypted data as base64-encoded strings.
"""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from app.config import get_config

cfg = get_config()


def generate_encryption_salt() -> bytes:
    """
    Generates a random salt for AES key derivation.
    """
    return os.urandom(cfg.CRYPTOGRAPHY_SALT_LENGTH)


def extract_encryption_key(password: str, salt: bytes) -> bytes:
    """
    Derives an AES key from the given password and salt using PBKDF2
    with HMAC-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=cfg.CRYPTOGRAPHY_KEY_LENGTH,
        salt=salt,
        iterations=cfg.CRYPTOGRAPHY_PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_bytes(data: bytes) -> bytes:
    """
    Encrypts the provided data using AES encryption with CBC mode.
    The salt, IV, and ciphertext are concatenated and returned as a
    single encrypted value.
    """
    salt = generate_encryption_salt()
    iv = os.urandom(cfg.CRYPTOGRAPHY_IV_LENGTH)
    key = extract_encryption_key(cfg.CRYPTOGRAPHY_PASSWORD, salt)

    cipher = Cipher(
        algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_data = salt + iv + ciphertext
    return encrypted_data


def encrypt_value(value: str) -> str:
    """
    Encrypts the given string value and returns the encrypted data as a
    base64-encoded string.
    """
    encrypted_data = encrypt_bytes(value.encode())
    return base64.b64encode(encrypted_data).decode("utf-8")


def decrypt_bytes(encrypted_data: bytes) -> bytes:
    """
    Decrypts the encrypted data. The encrypted data contains the salt,
    IV, and ciphertext concatenated together.
    """
    # Extract the salt and IV from the encrypted data
    salt = encrypted_data[:cfg.CRYPTOGRAPHY_SALT_LENGTH]
    iv = encrypted_data[
        cfg.CRYPTOGRAPHY_SALT_LENGTH:cfg.CRYPTOGRAPHY_SALT_LENGTH +
        cfg.CRYPTOGRAPHY_IV_LENGTH]
    ciphertext = encrypted_data[
        cfg.CRYPTOGRAPHY_SALT_LENGTH + cfg.CRYPTOGRAPHY_IV_LENGTH:]

    # Derive the AES key using the salt
    key = extract_encryption_key(cfg.CRYPTOGRAPHY_PASSWORD, salt)

    cipher = Cipher(
        algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt and unpad the ciphertext
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data


def decrypt_value(encrypted_data: str) -> str:
    """
    The function decodes the base64 string into bytes, decrypts it using
    AES, and returns the decrypted string.
    """
    encrypted_bytes = base64.b64decode(encrypted_data)
    decrypted_data = decrypt_bytes(encrypted_bytes)
    return decrypted_data.decode()
