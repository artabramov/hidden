import unittest
from unittest.mock import patch, MagicMock
from app.helpers.encrypt_helper import (
    cfg, generate_encryption_salt, extract_aes_key,
    encrypt_bytes, decrypt_bytes, encrypt_str, decrypt_str,
    encrypt_int, decrypt_int, encrypt_bool, decrypt_bool,
    hash_str)


class EncryptHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.encrypt_helper.cfg")
    @patch("app.helpers.encrypt_helper.os")
    def test_generate_encryption_salt(self, os_mock, cfg_mock):
        cfg_mock.CRYPTOGRAPHY_SALT_LENGTH = 16
        os_mock.urandom.return_value = "salt"

        result = generate_encryption_salt()
        self.assertEqual(result, os_mock.urandom.return_value)

        os_mock.urandom.assert_called_once_with(
            cfg_mock.CRYPTOGRAPHY_SALT_LENGTH)

    @patch("app.helpers.encrypt_helper.default_backend")
    @patch("app.helpers.encrypt_helper.hashes")
    @patch("app.helpers.encrypt_helper.PBKDF2HMAC")
    def test_extract_aes_key(self, pbdkdf2_mock, hashes_mock,
                             default_backend_mock):
        password = "password"
        salt = "salt"
        hashes_mock.SHA256.return_value = "algorithm"
        default_backend_mock.return_value = "default_backend"

        result = extract_aes_key(password, salt)
        self.assertEqual(result, pbdkdf2_mock.return_value.derive.return_value)

        pbdkdf2_mock.assert_called_once_with(
            algorithm=hashes_mock.SHA256.return_value,
            length=cfg.CRYPTOGRAPHY_KEY_LENGTH,
            salt=salt,
            iterations=cfg.CRYPTOGRAPHY_PBKDF2_ITERATIONS,
            backend=default_backend_mock.return_value)

        pbdkdf2_mock.return_value.derive.assert_called_once_with(
            password.encode()
        )

    @patch("app.helpers.encrypt_helper.ctx")
    @patch("app.helpers.encrypt_helper.default_backend")
    @patch("app.helpers.encrypt_helper.padding")
    @patch("app.helpers.encrypt_helper.modes")
    @patch("app.helpers.encrypt_helper.algorithms")
    @patch("app.helpers.encrypt_helper.Cipher")
    @patch("app.helpers.encrypt_helper.extract_aes_key")
    @patch("app.helpers.encrypt_helper.os")
    @patch("app.helpers.encrypt_helper.generate_encryption_salt")
    def test_encrypt_bytes(self, generate_encryption_salt_mock, os_mock,
                           extract_aes_key_mock, cipher_mock,
                           algorithms_mock, modes_mock, padding_mock,
                           default_backend_mock, ctx_mock):
        ctx_mock.secret_key = "SECRETKEY"
        bytes_value = b"value"
        salt_mock = b"salt"
        iv_mock = b"1234567890123456"
        key_mock = b"123456789012345678901234"
        ciphertext_mock = b"ciphertext_data"

        generate_encryption_salt_mock.return_value = salt_mock
        os_mock.urandom.return_value = iv_mock
        extract_aes_key_mock.return_value = key_mock
        cipher_mock.return_value.encryptor.return_value.update.return_value = ciphertext_mock  # noqa E501
        cipher_mock.return_value.encryptor.return_value.finalize.return_value = b""  # noqa E501

        padder_mock = MagicMock()
        padding_mock.PKCS7.return_value.padder.return_value = padder_mock
        padder_mock.update.return_value = b"padded_data"
        padder_mock.finalize.return_value = b""

        result = encrypt_bytes(bytes_value)

        # Assert mocks were called
        generate_encryption_salt_mock.assert_called_once_with()
        os_mock.urandom.assert_called_once_with(cfg.CRYPTOGRAPHY_IV_LENGTH)
        extract_aes_key_mock.assert_called_once_with(
            "SECRETKEY",
            generate_encryption_salt_mock.return_value
        )
        cipher_mock.assert_called_once_with(
            algorithms_mock.AES.return_value, modes_mock.CBC.return_value,
            backend=default_backend_mock.return_value
        )
        padding_mock.PKCS7.assert_called_once_with(
            algorithms_mock.AES.block_size)

        # Assert the padder was used correctly
        padder_mock.update.assert_called_once_with(bytes_value)
        padder_mock.finalize.assert_called_once_with()

        # Test that the final encrypted data is salt + iv + ciphertext
        expected_result = salt_mock + iv_mock + ciphertext_mock
        assert result == expected_result

    def test_encrypt_bytes_none(self):
        result = encrypt_bytes(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.ctx")
    @patch("app.helpers.encrypt_helper.default_backend")
    @patch("app.helpers.encrypt_helper.padding")
    @patch("app.helpers.encrypt_helper.modes")
    @patch("app.helpers.encrypt_helper.algorithms")
    @patch("app.helpers.encrypt_helper.Cipher")
    @patch("app.helpers.encrypt_helper.extract_aes_key")
    @patch("app.helpers.encrypt_helper.os")
    def test_decrypt_bytes(self, os_mock, extract_aes_key_mock, cipher_mock,
                           algorithms_mock, modes_mock, padding_mock,
                           default_backend_mock, ctx_mock):
        ctx_mock.secret_key = "SECRETKEY"

        encrypted_data = b"salt" + b"iv" + b"ciphertext"
        salt = encrypted_data[:cfg.CRYPTOGRAPHY_SALT_LENGTH]

        extract_aes_key_mock.return_value = b"123456789012345678901234"
        unpadder_mock = MagicMock()
        padding_mock.PKCS7.return_value.unpadder.return_value = unpadder_mock

        decryptor_mock = MagicMock()
        cipher_mock.return_value.decryptor.return_value = decryptor_mock

        decryptor_mock.update.return_value = b"some padded data"
        decryptor_mock.finalize.return_value = b"finalize data"

        unpadder_mock.update.return_value = b"some padded datafinalize data"
        unpadder_mock.finalize.return_value = b"decrypted data"

        result = decrypt_bytes(encrypted_data)
        self.assertEqual(
            result, b"some padded datafinalize datadecrypted data")

        os_mock.assert_not_called()
        extract_aes_key_mock.assert_called_once_with("SECRETKEY", salt)

        cipher_mock.assert_called_once_with(
            algorithms_mock.AES.return_value, modes_mock.CBC.return_value,
            backend=default_backend_mock.return_value)

        padding_mock.PKCS7.assert_called_once_with(
            algorithms_mock.AES.block_size)
        decryptor_mock.update.assert_called_once()
        decryptor_mock.finalize.assert_called_once_with()
        unpadder_mock.update.assert_called_once_with(
            b"some padded data" + b"finalize data")
        unpadder_mock.finalize.assert_called_once_with()

    def test_decrypt_bytes_none(self):
        """When decrypt None value instead a binary data."""
        result = decrypt_bytes(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.encrypt_bytes")
    @patch("app.helpers.encrypt_helper.base64.b64encode")
    def test_encrypt_str(self, b64encode_mock, encrypt_bytes_mock):
        value = "test_value"
        encrypted_data = b"encrypted_data"
        base64_encoded_data = b"base64encodeddata"
        encrypt_bytes_mock.return_value = encrypted_data
        b64encode_mock.return_value = base64_encoded_data

        result = encrypt_str(value)

        encrypt_bytes_mock.assert_called_once_with(value.encode())
        b64encode_mock.assert_called_once_with(encrypted_data)
        self.assertEqual(result, base64_encoded_data.decode("utf-8"))

    def test_encrypt_str_none(self):
        result = encrypt_str(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.base64.b64decode")
    @patch("app.helpers.encrypt_helper.decrypt_bytes")
    def test_decrypt_str(self, decrypt_bytes_mock, b64decode_mock):
        encrypted_data = "base64encodeddata"
        encrypted_bytes = b"encrypted_data"
        decrypted_data = b"decrypted_value"
        b64decode_mock.return_value = encrypted_bytes
        decrypt_bytes_mock.return_value = decrypted_data

        result = decrypt_str(encrypted_data)

        b64decode_mock.assert_called_once_with(encrypted_data)
        decrypt_bytes_mock.assert_called_once_with(encrypted_bytes)
        self.assertEqual(result, decrypted_data.decode())

    def test_decrypt_str_none(self):
        """When decrypt None value instead a string."""
        result = decrypt_str(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.encrypt_str")
    def test_encrypt_int(self, encrypt_str_mock):
        value = 12345
        encrypted_value = "encrypted_int"
        encrypt_str_mock.return_value = encrypted_value

        result = encrypt_int(value)

        encrypt_str_mock.assert_called_once_with(str(value))
        self.assertEqual(result, encrypted_value)

    def test_encrypt_int_none(self):
        result = encrypt_int(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.decrypt_str")
    def test_decrypt_int(self, decrypt_str_mock):
        encrypted_value = "encrypted_int"
        decrypted_value = "12345"
        decrypt_str_mock.return_value = decrypted_value

        result = decrypt_int(encrypted_value)

        decrypt_str_mock.assert_called_once_with(encrypted_value)
        self.assertEqual(result, int(decrypted_value))

    def test_decrypt_int_none(self):
        result = decrypt_int(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.encrypt_int")
    def test_encrypt_bool_true(self, encrypt_int_mock):
        encrypt_int_mock.return_value = "encrypted_int"

        result = encrypt_bool(True)

        encrypt_int_mock.assert_called_once_with(1)
        self.assertEqual(result, "encrypted_int")

    @patch("app.helpers.encrypt_helper.encrypt_int")
    def test_encrypt_bool_false(self, encrypt_int_mock):
        encrypt_int_mock.return_value = "encrypted_int"

        result = encrypt_bool(False)

        encrypt_int_mock.assert_called_once_with(0)
        self.assertEqual(result, "encrypted_int")

    def test_encrypt_bool_none(self):
        result = encrypt_bool(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.decrypt_int")
    def test_decrypt_bool_true(self, decrypt_int_mock):
        encrypted_value = "encrypted_bool"
        decrypt_int_mock.return_value = 1

        result = decrypt_bool(encrypted_value)

        decrypt_int_mock.assert_called_once_with(encrypted_value)
        self.assertTrue(result)

    @patch("app.helpers.encrypt_helper.decrypt_int")
    def test_decrypt_bool_false(self, decrypt_int_mock):
        encrypted_value = "encrypted_bool"
        decrypt_int_mock.return_value = 0

        result = decrypt_bool(encrypted_value)

        decrypt_int_mock.assert_called_once_with(encrypted_value)
        self.assertFalse(result)

    def test_decrypt_bool_none(self):
        result = decrypt_bool(None)
        self.assertIsNone(result)

    @patch("app.helpers.encrypt_helper.ctx")
    @patch("app.helpers.encrypt_helper.hashlib.sha512")
    def test_hash_str(self, sha512_mock, ctx_mock):
        value = "some_value"
        expected_hash = "expected_sha512_hash"

        ctx_mock.secret_key = "secret_key"

        hash_mock = MagicMock()
        hash_mock.hexdigest.return_value = expected_hash
        sha512_mock.return_value = hash_mock

        result = hash_str(value)

        sha512_mock.assert_called_once_with((value + "secret_key").encode())
        hash_mock.hexdigest.assert_called_once()
        self.assertEqual(result, expected_hash)


if __name__ == "__main__":
    unittest.main()
