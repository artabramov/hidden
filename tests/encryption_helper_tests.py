import unittest
import asynctest
from unittest.mock import patch, MagicMock
from app.helpers.encryption_helper import (
    cfg, generate_encryption_salt, extract_encryption_key,
    encrypt_bytes, decrypt_bytes, encrypt_value, decrypt_value)


class EncryptionHelperTestCase(asynctest.TestCase):

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    @patch("app.helpers.encryption_helper.cfg")
    @patch("app.helpers.encryption_helper.os")
    def test__generate_encryption_salt(self, os_mock, cfg_mock):
        cfg_mock.CRYPTOGRAPHY_SALT_LENGTH = 16
        os_mock.urandom.return_value = "salt"

        result = generate_encryption_salt()
        self.assertEqual(result, os_mock.urandom.return_value)

        os_mock.urandom.assert_called_once_with(
            cfg_mock.CRYPTOGRAPHY_SALT_LENGTH)

    @patch("app.helpers.encryption_helper.default_backend")
    @patch("app.helpers.encryption_helper.hashes")
    @patch("app.helpers.encryption_helper.PBKDF2HMAC")
    def test__extract_encryption_key(self, pbdkdf2_mock, hashes_mock,
                                     default_backend_mock):
        password = "password"
        salt = "salt"
        hashes_mock.SHA256.return_value = "algorithm"
        default_backend_mock.return_value = "default_backend"

        result = extract_encryption_key(password, salt)
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

    @patch("app.helpers.encryption_helper.default_backend")
    @patch("app.helpers.encryption_helper.padding")
    @patch("app.helpers.encryption_helper.modes")
    @patch("app.helpers.encryption_helper.algorithms")
    @patch("app.helpers.encryption_helper.Cipher")
    @patch("app.helpers.encryption_helper.extract_encryption_key")
    @patch("app.helpers.encryption_helper.os")
    @patch("app.helpers.encryption_helper.generate_encryption_salt")
    def test__encrypt_bytes(
        self,  # For class-based tests
        generate_encryption_salt_mock, os_mock, extract_encryption_key_mock,
        cipher_mock, algorithms_mock, modes_mock, padding_mock,
        default_backend_mock
    ):
        # Setup mock return values
        bytes_value = b"value"
        mock_salt = b"salt"
        mock_iv = b"1234567890123456"
        mock_key = b"123456789012345678901234"
        mock_ciphertext = b"ciphertext_data"

        # Mock return values for each of the functions
        generate_encryption_salt_mock.return_value = mock_salt
        os_mock.urandom.return_value = mock_iv
        extract_encryption_key_mock.return_value = mock_key
        cipher_mock.return_value.encryptor.return_value.update.return_value = mock_ciphertext  # noqa E501
        cipher_mock.return_value.encryptor.return_value.finalize.return_value = b""  # noqa E501

        # Mock padding behavior
        padder_mock = MagicMock()
        padding_mock.PKCS7.return_value.padder.return_value = padder_mock
        padder_mock.update.return_value = b"padded_data"
        padder_mock.finalize.return_value = b""

        # Call the function
        result = encrypt_bytes(bytes_value)

        # Assert mocks were called
        generate_encryption_salt_mock.assert_called_once_with()
        os_mock.urandom.assert_called_once_with(cfg.CRYPTOGRAPHY_IV_LENGTH)
        extract_encryption_key_mock.assert_called_once_with(
            cfg.CRYPTOGRAPHY_PASSWORD,
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
        expected_result = mock_salt + mock_iv + mock_ciphertext
        assert result == expected_result

    @patch("app.helpers.encryption_helper.default_backend")
    @patch("app.helpers.encryption_helper.padding")
    @patch("app.helpers.encryption_helper.modes")
    @patch("app.helpers.encryption_helper.algorithms")
    @patch("app.helpers.encryption_helper.Cipher")
    @patch("app.helpers.encryption_helper.extract_encryption_key")
    @patch("app.helpers.encryption_helper.os")
    def test__decrypt_bytes(self, os_mock, extract_encryption_key_mock,
                            cipher_mock, algorithms_mock, modes_mock,
                            padding_mock, default_backend_mock):

        encrypted_data = b"salt" + b"iv" + b"ciphertext"
        salt = encrypted_data[:cfg.CRYPTOGRAPHY_SALT_LENGTH]
        iv = encrypted_data[cfg.CRYPTOGRAPHY_SALT_LENGTH:cfg.CRYPTOGRAPHY_SALT_LENGTH + cfg.CRYPTOGRAPHY_IV_LENGTH]  # noqa E501
        ciphertext = encrypted_data[cfg.CRYPTOGRAPHY_SALT_LENGTH + cfg.CRYPTOGRAPHY_IV_LENGTH:]  # noqa E501

        # Mocks
        extract_encryption_key_mock.return_value = b"123456789012345678901234"
        unpadder_mock = MagicMock()
        padding_mock.PKCS7.return_value.unpadder.return_value = unpadder_mock

        decryptor_mock = MagicMock()
        cipher_mock.return_value.decryptor.return_value = decryptor_mock

        decryptor_mock.update.return_value = b"some padded data"
        decryptor_mock.finalize.return_value = b"finalize data"

        unpadder_mock.update.return_value = b"some padded datafinalize data"
        unpadder_mock.finalize.return_value = b"decrypted data"

        decrypt_bytes(encrypted_data)

        os_mock.assert_not_called()
        extract_encryption_key_mock.assert_called_once_with(
            cfg.CRYPTOGRAPHY_PASSWORD, salt)

        cipher_mock.assert_called_once_with(
            algorithms_mock.AES.return_value, modes_mock.CBC.return_value,
            backend=default_backend_mock.return_value
        )

        padding_mock.PKCS7.assert_called_once_with(
            algorithms_mock.AES.block_size
        )
        decryptor_mock.update.assert_called_once()
        decryptor_mock.finalize.assert_called_once_with()
        unpadder_mock.update.assert_called_once_with(
            b"some padded data" + b"finalize data")
        unpadder_mock.finalize.assert_called_once_with()

    @patch("app.helpers.encryption_helper.encrypt_bytes")
    @patch("app.helpers.encryption_helper.base64.b64encode")
    def test__encrypt_value(self, b64encode_mock, encrypt_bytes_mock):
        # Prepare mock values
        value = "test_value"
        encrypted_data = b"encrypted_data"
        base64_encoded_data = b"base64encodeddata"
        encrypt_bytes_mock.return_value = encrypted_data
        b64encode_mock.return_value = base64_encoded_data

        result = encrypt_value(value)

        encrypt_bytes_mock.assert_called_once_with(value.encode())
        b64encode_mock.assert_called_once_with(encrypted_data)
        self.assertEqual(result, base64_encoded_data.decode("utf-8"))

    @patch("app.helpers.encryption_helper.base64.b64decode")
    @patch("app.helpers.encryption_helper.decrypt_bytes")
    def test__decrypt_value(self, decrypt_bytes_mock, b64decode_mock):
        encrypted_data = "base64encodeddata"
        encrypted_bytes = b"encrypted_data"
        decrypted_data = b"decrypted_value"
        b64decode_mock.return_value = encrypted_bytes
        decrypt_bytes_mock.return_value = decrypted_data

        result = decrypt_value(encrypted_data)

        b64decode_mock.assert_called_once_with(encrypted_data)
        decrypt_bytes_mock.assert_called_once_with(encrypted_bytes)
        self.assertEqual(result, decrypted_data.decode())


if __name__ == "__main__":
    unittest.main()
