import unittest
import asynctest
from unittest.mock import patch, MagicMock
from app.helpers.hash_helper import cfg, get_hash


class HashHelperTestCase(asynctest.TestCase):

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    @patch("app.helpers.hash_helper.get_config")
    @patch("app.helpers.hash_helper.hashlib.sha512")
    def test__get_hash(self, sha512_mock, get_config_mock):
        value = "some_value"
        expected_hash = "expected_sha512_hash"

        hash_mock = MagicMock()
        hash_mock.hexdigest.return_value = expected_hash
        sha512_mock.return_value = hash_mock

        result = get_hash(value)

        sha512_mock.assert_called_once_with(
            (value + cfg.HASHLIB_SALT).encode())
        hash_mock.hexdigest.assert_called_once()
        self.assertEqual(result, expected_hash)


if __name__ == "__main__":
    unittest.main()
