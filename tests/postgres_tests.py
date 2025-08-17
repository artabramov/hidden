import unittest
from unittest.mock import patch
from app.postgres import SessionManager


class DatabaseTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.config.get_config")
    @patch("app.postgres.create_async_engine")
    @patch("app.postgres.async_sessionmaker")
    def test_session_manager(
            self, sessionmaker_mock, create_engine_mock, get_config_mock):
        get_config_mock.return_value.POSTGRES_USERNAME = "test_user"
        get_config_mock.return_value.POSTGRES_PASSWORD = "test_pass"
        get_config_mock.return_value.POSTGRES_HOST = "localhost"
        get_config_mock.return_value.POSTGRES_PORT = "5432"
        get_config_mock.return_value.POSTGRES_DATABASE = "test_db"
        get_config_mock.return_value.POSTGRES_POOL_SIZE = 10
        get_config_mock.return_value.POSTGRES_POOL_OVERFLOW = 5

        session_manager = SessionManager()

        self.assertEqual(
            session_manager.async_engine, create_engine_mock.return_value)
        self.assertEqual(
            session_manager.async_sessionmaker, sessionmaker_mock.return_value)


if __name__ == "__main__":
    unittest.main()
