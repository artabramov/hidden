# tests/security/test_encryption.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import call, patch

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from app.security.encryption import (
    _HEADER_LEN,
    _KEY_LEN,
    _MAGIC,
    _NONCE_LEN,
    _SALT_LEN,
    _SCRYPT_N,
    _SCRYPT_P,
    _SCRYPT_R,
    _VERSION,
    decrypt_passphrase,
    encrypt_passphrase,
)

_PLAINTEXT = b"\xff\x00secret"
_PASSWORD = b"master-password"


class TestEncryptPassphrase(unittest.TestCase):
    def test_rejects_empty_input(self):
        cases = (
            (b"", _PASSWORD, "plaintext must not be empty"),
            (_PLAINTEXT, b"", "password must not be empty"),
        )

        for plaintext, password, message in cases:
            with self.subTest(message=message):
                with patch("app.security.encryption.os.urandom") as urandom:
                    with self.assertRaises(ValueError) as caught:
                        encrypt_passphrase(plaintext, password)

                self.assertEqual(str(caught.exception), message)
                urandom.assert_not_called()

    def test_builds_versioned_blob(self):
        salt = bytes(range(_SALT_LEN))
        nonce = bytes(range(_NONCE_LEN))
        calls = []

        def spy(**kwargs):
            calls.append(kwargs)
            return Scrypt(**kwargs)

        with (
            patch(
                "app.security.encryption.os.urandom",
                side_effect=[salt, nonce],
            ) as urandom,
            patch("app.security.encryption.Scrypt", side_effect=spy),
        ):
            blob = encrypt_passphrase(_PLAINTEXT, _PASSWORD)

        self.assertEqual(
            urandom.call_args_list,
            [call(_SALT_LEN), call(_NONCE_LEN)],
        )
        self.assertEqual(blob[:4], _MAGIC)
        self.assertEqual(blob[4], _VERSION)
        self.assertEqual(blob[5:5 + _SALT_LEN], salt)
        self.assertEqual(blob[5 + _SALT_LEN:_HEADER_LEN], nonce)
        self.assertEqual(
            calls,
            [{
                "salt": salt,
                "length": _KEY_LEN,
                "n": _SCRYPT_N,
                "r": _SCRYPT_R,
                "p": _SCRYPT_P,
            }],
        )
        self.assertEqual(
            decrypt_passphrase(blob, _PASSWORD),
            _PLAINTEXT,
        )

    def test_format_constants(self):
        self.assertEqual(_MAGIC, b"HENC")
        self.assertEqual(_VERSION, 1)
        self.assertEqual(_SALT_LEN, 16)
        self.assertEqual(_NONCE_LEN, 12)
        self.assertEqual(_KEY_LEN, 32)
        self.assertEqual(_HEADER_LEN, 33)
        self.assertEqual(_SCRYPT_N, 2**15)
        self.assertEqual(_SCRYPT_R, 8)
        self.assertEqual(_SCRYPT_P, 1)


class TestDecryptPassphrase(unittest.TestCase):
    def test_rejects_invalid_blob(self):
        short = b"H" * _HEADER_LEN
        bad_magic = b"XXXX" + b"\x01" + b"\x00" * (_HEADER_LEN - 4)
        bad_version = _MAGIC + b"\x02" + b"\x00" * (_HEADER_LEN - 4)
        cases = (
            (b"", _PASSWORD, "ciphertext must not be empty"),
            (b"x", b"", "password must not be empty"),
            (short, _PASSWORD, "ciphertext too short"),
            (bad_magic, _PASSWORD, "invalid magic"),
            (bad_version, _PASSWORD, "unsupported version"),
        )

        for ciphertext, password, message in cases:
            with self.subTest(message=message):
                with patch(
                    "app.security.encryption._derive_key",
                ) as derive:
                    with self.assertRaises(ValueError) as caught:
                        decrypt_passphrase(ciphertext, password)

                self.assertEqual(str(caught.exception), message)
                derive.assert_not_called()

    def _assert_undecryptable(self, ciphertext, password):
        with self.assertRaises(ValueError) as caught:
            decrypt_passphrase(ciphertext, password)

        self.assertEqual(
            str(caught.exception),
            "invalid password or corrupted data",
        )
        self.assertIsNone(caught.exception.__cause__)

    def test_rejects_wrong_password(self):
        blob = encrypt_passphrase(_PLAINTEXT, _PASSWORD)

        self._assert_undecryptable(blob, b"other-password")

    def test_rejects_corrupted_body(self):
        blob = bytearray(encrypt_passphrase(_PLAINTEXT, _PASSWORD))
        blob[-1] ^= 0xFF

        self._assert_undecryptable(bytes(blob), _PASSWORD)
