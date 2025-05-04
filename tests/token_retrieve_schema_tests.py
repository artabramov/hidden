
import unittest
from pydantic import ValidationError
from app.schemas.token_retrieve_schema import TokenRetrieveRequest


class TokenRetrieveSchemaTest(unittest.TestCase):

    def test_request_correct(self):
        data = {
            "username": "TestUser",
            "user_totp": "123456",
            "token_exp": 3600
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.username, "testuser")
        self.assertEqual(schema.user_totp, "123456")
        self.assertEqual(schema.token_exp, 3600)

    def test_username_empty(self):
        data = {
            "username": "",
            "user_totp": "123456",
            "token_exp": 3600
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_username_too_short(self):
        data = {
            "username": "T",
            "user_totp": "123456",
            "token_exp": 3600
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_username_too_long(self):
        data = {
            "username": "T" * 48,
            "user_totp": "123456",
            "token_exp": 3600
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_username_length_min(self):
        data = {
            "username": "qw",
            "user_totp": "123456",
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.username, "qw")

    def test_username_length_max(self):
        data = {
            "username": "q" * 47,
            "user_totp": "123456",
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.username, "q" * 47)

    def test_username_lowercase(self):
        data = {
            "username": "QwErTy",
            "user_totp": "123456",
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.username, "qwerty")

    def test_user_totp_missing(self):
        data = {
            "username": "username",
            "token_exp": 3600
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_user_totp_too_short(self):
        data = {
            "username": "username",
            "user_totp": "12345",
            "token_exp": 3600
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_user_totp_too_long(self):
        data = {
            "username": "username",
            "user_totp": "1234567",
            "token_exp": 3600
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_user_totp_correct(self):
        data = {
            "username": "username",
            "user_totp": "123456",
            "token_exp": 3600
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.username, "username")
        self.assertEqual(schema.user_totp, "123456")
        self.assertEqual(schema.token_exp, 3600)

    def test_token_exp_missing(self):
        data = {
            "username": "username",
            "user_totp": "123456"
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.token_exp, None)

    def test_token_exp_zero(self):
        data = {
            "username": "username",
            "user_totp": "123456",
            "token_exp": "0",
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)

    def test_token_exp_min(self):
        data = {
            "username": "username",
            "user_totp": "123456",
            "token_exp": "1",
        }
        schema = TokenRetrieveRequest(**data)
        self.assertEqual(schema.token_exp, 1)

    def test_token_exp_str(self):
        data = {
            "username": "username",
            "user_totp": "123456",
            "token_exp": "exp",
        }
        with self.assertRaises(ValidationError):
            TokenRetrieveRequest(**data)


if __name__ == "__main__":
    unittest.main()
