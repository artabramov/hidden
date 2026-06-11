# tests/security/test_encryption.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock, patch

from cryptography.fernet import Fernet

from app.security import encryption


class TestEncryption(unittest.TestCase):
    def tearDown(self):
        encryption.get_fernet.cache_clear()

    def test_encrypt_passphrase_raises_when_plaintext_empty(self):
        with self.assertRaises(ValueError) as cm:
            encryption.encrypt_passphrase(b"", b"password")

        self.assertEqual(str(cm.exception), "plaintext must not be empty")

    def test_encrypt_passphrase_raises_when_password_empty(self):
        with self.assertRaises(ValueError) as cm:
            encryption.encrypt_passphrase(b"plaintext", b"")

        self.assertEqual(str(cm.exception), "password must not be empty")

    def test_decrypt_passphrase_raises_when_ciphertext_empty(self):
        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(b"", b"password")

        self.assertEqual(str(cm.exception), "ciphertext must not be empty")

    def test_decrypt_passphrase_raises_when_password_empty(self):
        ciphertext = encryption.encrypt_passphrase(
            b"plaintext",
            b"password",
        )

        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(ciphertext, b"")

        self.assertEqual(str(cm.exception), "password must not be empty")

    def test_decrypt_passphrase_raises_when_ciphertext_too_short(self):
        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(b"short", b"password")

        self.assertEqual(str(cm.exception), "ciphertext too short")

    def test_decrypt_passphrase_raises_when_magic_invalid(self):
        ciphertext = encryption.encrypt_passphrase(
            b"plaintext",
            b"password",
        )
        corrupted = b"XXXX" + ciphertext[4:]

        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(corrupted, b"password")

        self.assertEqual(str(cm.exception), "invalid magic")

    def test_decrypt_passphrase_raises_when_version_unsupported(self):
        ciphertext = encryption.encrypt_passphrase(
            b"plaintext",
            b"password",
        )
        corrupted = ciphertext[:4] + b"\x02" + ciphertext[5:]

        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(corrupted, b"password")

        self.assertEqual(str(cm.exception), "unsupported version")

    def test_encrypt_and_decrypt_passphrase_roundtrip(self):
        plaintext = b"secret-passphrase"
        password = b"master-password"

        ciphertext = encryption.encrypt_passphrase(
            plaintext,
            password,
        )
        decrypted = encryption.decrypt_passphrase(
            ciphertext,
            password,
        )

        self.assertIsInstance(ciphertext, bytes)
        self.assertNotEqual(ciphertext, plaintext)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_passphrase_returns_distinct_ciphertexts_for_same_input(
        self,
    ):
        plaintext = b"secret-passphrase"
        password = b"master-password"

        ciphertext_1 = encryption.encrypt_passphrase(
            plaintext,
            password,
        )
        ciphertext_2 = encryption.encrypt_passphrase(
            plaintext,
            password,
        )

        self.assertNotEqual(ciphertext_1, ciphertext_2)
        self.assertEqual(
            encryption.decrypt_passphrase(ciphertext_1, password),
            plaintext,
        )
        self.assertEqual(
            encryption.decrypt_passphrase(ciphertext_2, password),
            plaintext,
        )

    def test_decrypt_passphrase_raises_when_password_invalid(self):
        ciphertext = encryption.encrypt_passphrase(
            b"secret-passphrase",
            b"correct-password",
        )

        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(
                ciphertext,
                b"wrong-password",
            )

        self.assertEqual(
            str(cm.exception),
            "invalid password or corrupted data",
        )

    def test_decrypt_passphrase_raises_when_body_corrupted(self):
        ciphertext = encryption.encrypt_passphrase(
            b"secret-passphrase",
            b"correct-password",
        )
        corrupted = ciphertext[:-1] + bytes([ciphertext[-1] ^ 0x01])

        with self.assertRaises(ValueError) as cm:
            encryption.decrypt_passphrase(
                corrupted,
                b"correct-password",
            )

        self.assertEqual(
            str(cm.exception),
            "invalid password or corrupted data",
        )

    def test_generate_fernet_key_returns_valid_key_string(self):
        key = encryption.generate_fernet_key()

        self.assertIsInstance(key, str)
        Fernet(key.encode())

    def test_get_fernet_returns_fernet_from_config_key(self):
        config = MagicMock()
        config.FERNET_KEY = Fernet.generate_key().decode()

        with patch(
            "app.security.encryption.get_config",
            return_value=config,
        ):
            fernet = encryption.get_fernet()

        self.assertIsInstance(fernet, Fernet)

    def test_get_fernet_is_cached(self):
        config = MagicMock()
        config.FERNET_KEY = Fernet.generate_key().decode()

        with patch(
            "app.security.encryption.get_config",
            return_value=config,
        ) as get_config_mock:
            fernet_1 = encryption.get_fernet()
            fernet_2 = encryption.get_fernet()

        self.assertIs(fernet_1, fernet_2)
        get_config_mock.assert_called_once_with()

    def test_encrypt_string_encrypts_with_cached_fernet(self):
        fernet = MagicMock()
        fernet.encrypt.return_value = b"encrypted-value"

        with patch(
            "app.security.encryption.get_fernet",
            return_value=fernet,
        ) as get_fernet_mock:
            result = encryption.encrypt_string("plain-value")

        self.assertEqual(result, "encrypted-value")
        get_fernet_mock.assert_called_once_with()
        fernet.encrypt.assert_called_once_with(b"plain-value")

    def test_decrypt_string_decrypts_with_cached_fernet(self):
        fernet = MagicMock()
        fernet.decrypt.return_value = b"plain-value"

        with patch(
            "app.security.encryption.get_fernet",
            return_value=fernet,
        ) as get_fernet_mock:
            result = encryption.decrypt_string("encrypted-value")

        self.assertEqual(result, "plain-value")
        get_fernet_mock.assert_called_once_with()
        fernet.decrypt.assert_called_once_with(b"encrypted-value")
