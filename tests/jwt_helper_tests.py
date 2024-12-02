import unittest
import asynctest
from unittest.mock import patch, MagicMock
import string
from app.helpers.jwt_helper import jti_create, jwt_encode, jwt_decode


class JwtHelperTestCase(asynctest.TestCase):

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    @patch("app.helpers.jwt_helper.cfg.JTI_LENGTH", 16)
    def test__jti_create(self):
        jti = jti_create()

        self.assertEqual(len(jti), 16)
        self.assertTrue(all(
            c in string.ascii_letters + string.digits for c in jti))

    @patch("app.helpers.jwt_helper.cfg.JWT_SECRET", "supersecretkey")
    @patch("app.helpers.jwt_helper.cfg.JWT_ALGORITHM", "HS256")
    @patch("app.helpers.jwt_helper.time.time", return_value=1609459200)
    @patch("app.helpers.jwt_helper.jwt.encode")
    def test__jwt_encode(self, encode_mock, time_mock):
        user = MagicMock()
        user.id = 123
        user.user_role = "admin"
        user.user_login = "test_user"
        user.jti = "random_jti_string"

        encode_mock.return_value = "encoded_token"

        jwt_token = jwt_encode(user)

        expected_payload = {
            "user_id": 123,
            "user_role": "admin",
            "user_login": "test_user",
            "jti": "random_jti_string",
            "iat": 1609459200
        }

        encode_mock.assert_called_once_with(
            expected_payload,
            "supersecretkey",
            algorithm="HS256"
        )

        self.assertEqual(jwt_token, "encoded_token")

    @patch("app.helpers.jwt_helper.cfg.JWT_SECRET", "supersecretkey")
    @patch("app.helpers.jwt_helper.cfg.JWT_ALGORITHM", "HS256")
    @patch("app.helpers.jwt_helper.jwt.decode")
    def test__jwt_decode(self, decode_mock):
        decoded_payload = {
            "user_id": 123,
            "user_role": "admin",
            "user_login": "test_user",
            "iat": 1609459200,
            "jti": "random_jti_string",
            "exp": 1609462800
        }
        decode_mock.return_value = decoded_payload

        result = jwt_decode("mocked_jwt_token")

        decode_mock.assert_called_once_with(
            "mocked_jwt_token", "supersecretkey", algorithms="HS256")

        expected_result = {
            "user_id": 123,
            "user_role": "admin",
            "user_login": "test_user",
            "iat": 1609459200,
            "jti": "random_jti_string",
            "exp": 1609462800
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
