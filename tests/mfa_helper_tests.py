import unittest
from unittest.mock import patch
from app.helpers.mfa_helper import generate_mfa_secret


class MfaHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.mfa_helper.pyotp")
    def test_generate_mfa_secret(self, pyotp_mock):
        pyotp_mock.random_base32.return_value = "random"

        result = generate_mfa_secret()
        self.assertEqual(result, pyotp_mock.random_base32.return_value)

        pyotp_mock.random_base32.assert_called_once()


if __name__ == "__main__":
    unittest.main()
