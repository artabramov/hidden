import unittest
import string
from unittest.mock import patch, MagicMock
from app.helpers.jwt_helper import generate_jti, jwt_encode, jwt_decode


class JwtHelperTestCase(unittest.TestCase):

    @patch("app.helpers.jwt_helper.random")
    @patch("app.helpers.jwt_helper.cfg")
    def test_generate_jti(self, cfg_mock, random_mock):
        cfg_mock.JTI_LENGTH = 40
        random_mock.choices.return_value = "random"

        result = generate_jti()
        self.assertEqual(result, random_mock.choices.return_value)

        random_mock.choices.assert_called_with(
            string.ascii_letters + string.digits, k=cfg_mock.JTI_LENGTH)

    @patch("app.helpers.jwt_helper.cfg.JWT_SECRET", "supersecretkey")
    @patch("app.helpers.jwt_helper.cfg.JWT_ALGORITHM", "HS256")
    @patch("app.helpers.jwt_helper.time.time")
    @patch("app.helpers.jwt_helper.jwt.encode")
    def test_jwt_encode(self, encode_mock, time_mock):
        user = MagicMock()
        user.id = 123
        user.user_role = "admin"
        user.username = "test_user"
        user.jti = "jti"

        encode_mock.return_value = "encoded_token"
        time_mock.return_value = 123456

        jwt_token = jwt_encode(user)

        expected_payload = {
            "user_id": 123,
            "user_role": "admin",
            "username": "test_user",
            "jti": "jti",
            "iat": time_mock.return_value
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
    def test_jwt_decode(self, decode_mock):
        decoded_payload = {
            "user_id": 123,
            "user_role": "admin",
            "username": "test_user",
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
            "username": "test_user",
            "iat": 1609459200,
            "jti": "random_jti_string",
            "exp": 1609462800
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
