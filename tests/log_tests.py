import logging
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import app.log as log_mod


class LogTest(unittest.TestCase):
    def setUp(self):
        self.cfg = SimpleNamespace(
            LOG_FILENAME="/var/log/hidden/hidden.log",
            LOG_FILESIZE=1048576,
            LOG_FILES_LIMIT=5,
            LOG_FORMAT="%(levelname)s %(request_uuid)s %(message)s",
            LOG_NAME="app",
            LOG_LEVEL=logging.DEBUG,
        )

    @patch("app.log.logging.getLogger")
    @patch("app.log.ConcurrentRotatingFileHandler")
    def test_init_logger_configures_once_and_sets_state(
            self, crfh_mock, getLogger_mock):
        app = SimpleNamespace(state=SimpleNamespace(config=self.cfg))

        handler = MagicMock()
        handler.baseFilename = self.cfg.LOG_FILENAME
        crfh_mock.return_value = handler

        logger_obj = MagicMock()
        logger_obj.handlers = []

        def _add(h):
            logger_obj.handlers.append(h)

        logger_obj.addHandler.side_effect = _add
        getLogger_mock.return_value = logger_obj

        log = log_mod.init_logger(app)

        self.assertIs(log, logger_obj)
        crfh_mock.assert_called_once_with(
            filename=self.cfg.LOG_FILENAME,
            maxBytes=self.cfg.LOG_FILESIZE,
            backupCount=self.cfg.LOG_FILES_LIMIT,
            encoding="utf-8",
        )
        handler.setFormatter.assert_called_once()
        fmt = handler.setFormatter.call_args[0][0]
        self.assertIsInstance(fmt, logging.Formatter)
        self.assertEqual(getattr(fmt, "_fmt", None), self.cfg.LOG_FORMAT)
        getLogger_mock.assert_called_once_with(self.cfg.LOG_NAME)
        self.assertEqual(len(logger_obj.handlers), 1)
        self.assertIs(app.state.log, logger_obj)
        logger_obj.setLevel.assert_called_with(self.cfg.LOG_LEVEL)
        self.assertFalse(getattr(logger_obj, "propagate", True))

        log2 = log_mod.init_logger(app)
        self.assertIs(log2, logger_obj)
        self.assertEqual(len(logger_obj.handlers), 1)
        logger_obj.addHandler.assert_called_once()

    @patch("app.log.logging.getLogger")
    @patch("app.log.ConcurrentRotatingFileHandler")
    def test_init_logger_no_duplicate_when_same_file_already_attached(
            self, crfh_mock, getLogger_mock):
        app = SimpleNamespace(state=SimpleNamespace(config=self.cfg))
        handler_existing = SimpleNamespace(baseFilename=self.cfg.LOG_FILENAME)
        logger_obj = MagicMock()
        logger_obj.handlers = [handler_existing]
        getLogger_mock.return_value = logger_obj
        crfh_mock.return_value = MagicMock()

        log_mod.init_logger(app)

        logger_obj.addHandler.assert_not_called()
        logger_obj.setLevel.assert_called_with(self.cfg.LOG_LEVEL)
        self.assertFalse(getattr(logger_obj, "propagate", True))
        self.assertIs(app.state.log, logger_obj)
