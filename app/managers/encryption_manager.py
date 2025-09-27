"""
Asynchronous-friendly encryption utilities wrapped in a manager class.
Provides AES-GCM with HKDF-based or raw-key setup.
"""

import os
import base64
import hmac
import hashlib
from typing import Optional, Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from app.config import Config


class EncryptionManager:
    """
    Coordinates symmetric encryption primitives behind a simple API.
    Accepts configuration and a secret at construction.
    """

    def __init__(self, config: Config, secret_key: Union[str, bytes]):
        """
        Initializes AES-GCM with a key derived or taken as-is from the
        secret.
        """
        self.config = config

        enc = self.config.CRYPTO_DEFAULT_ENCODING
        # keep the raw secret in bytes; no decoding required
        if isinstance(secret_key, (bytes, bytearray)):
            raw_secret = bytes(secret_key)
        else:
            raw_secret = secret_key.encode(enc)

        # derive or use raw for AES-GCM
        if self.config.CRYPTO_DERIVE_WITH_HKDF:
            salt_b64 = self.config.CRYPTO_HKDF_SALT_B64
            salt = base64.b64decode(salt_b64) if salt_b64 is not None else None
            self.key = HKDF(
                algorithm=hashes.SHA256(),
                length=self.config.CRYPTO_KEY_LENGTH,
                salt=salt,
                info=self.config.CRYPTO_HKDF_INFO,
            ).derive(raw_secret)

            # optional: separate HMAC key (key separation)
            self._hmac_key = HKDF(
                algorithm=hashes.SHA256(),
                length=self.config.CRYPTO_KEY_LENGTH,
                salt=salt,
                info=b"hmac-v1",
            ).derive(raw_secret)
        else:
            self.key = raw_secret
            self._hmac_key = raw_secret

        self.aesgcm = AESGCM(self.key)
        self.nonce_len = self.config.CRYPTO_NONCE_LENGTH
        self.default_aad = self.config.CRYPTO_AAD_DEFAULT

    def encrypt_bytes(self, data: bytes = None) -> Optional[bytes]:
        """
        Encrypts bytes and returns nonce||ciphertext (tag included).
        """
        if data is None:
            return None

        nonce = os.urandom(self.nonce_len)
        ct = self.aesgcm.encrypt(nonce, data, associated_data=self.default_aad)
        return nonce + ct

    def decrypt_bytes(self, payload: bytes = None) -> Optional[bytes]:
        """
        Decrypts bytes produced by this encryptor and verifies
        authenticity.
        """
        if payload is None:
            return None

        nonce, ct = payload[:self.nonce_len], payload[self.nonce_len:]
        return self.aesgcm.decrypt(nonce, ct, associated_data=self.default_aad)

    def encrypt_str(self, value: str = None) -> Optional[str]:
        """
        Encrypts text by encoding with the configured charset and
        base64-wrapping the result. Returns a textual envelope of
        the binary ciphertext.
        """
        if value is None:
            return None

        enc = self.config.CRYPTO_DEFAULT_ENCODING
        blob = self.encrypt_bytes(value.encode(enc))
        return base64.b64encode(blob).decode(enc)

    def decrypt_str(self, token: str = None) -> Optional[str]:
        """
        Decrypts a base64 text produced by the string encryptor. Returns
        the original text decoded with the configured charset.
        """
        if token is None:
            return None

        enc = self.config.CRYPTO_DEFAULT_ENCODING
        blob = base64.b64decode(token)
        return self.decrypt_bytes(blob).decode(enc)

    def encrypt_int(self, value: int = None) -> Optional[str]:
        """
        Encrypts an integer by converting to text and using string
        encryption. Returns a base64 token suitable for storage or
        transport.
        """
        if value is None:
            return None

        return self.encrypt_str(str(value))

    def decrypt_int(self, token: str = None) -> Optional[int]:
        """
        Decrypts a base64 token and parses the original integer value.
        Raises on invalid numeric form as part of fail-fast behavior.
        """
        if token is None:
            return None

        return int(self.decrypt_str(token))

    def encrypt_bool(self, value: bool = None) -> Optional[str]:
        """
        Encrypts a boolean by mapping to an integer and using string
        encryption. Returns a base64 token consistent with other scalar
        helpers.
        """
        if value is None:
            return None

        return self.encrypt_int(1 if value else 0)

    def decrypt_bool(self, token: str = None) -> Optional[bool]:
        """
        Decrypts a base64 token and maps the integer back to a boolean.
        Treats nonzero values as True and zero as False.
        """
        if token is None:
            return None

        return bool(self.decrypt_int(token))

    def get_hash(self, value: str) -> str:
        """
        Computes an HMAC-SHA-512 over the given value using
        a MAC-dedicated key. Returns a lowercase hexadecimal digest.
        """
        enc = self.config.CRYPTO_DEFAULT_ENCODING
        return hmac.new(
            self._hmac_key,
            value.encode(enc),
            hashlib.sha512
        ).hexdigest()
