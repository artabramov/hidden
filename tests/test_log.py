# tests/test_log.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

from app.log import RequestContextFilter, init_logging


class TestRequestContextFilter(unittest.TestCase):

    def test_injects_request_uuid_from_context(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="message",
            args=(),
            exc_info=None,
        )

        with patch(
            "app.log.get_context_var",
            return_value="request-123",
        ) as mock_get_context_var:
            result = RequestContextFilter().filter(record)

        self.assertTrue(result)
        self.assertEqual(record.request_uuid, "request-123")
        mock_get_context_var.assert_called_once_with("request_uuid", "-")

    def test_uses_default_request_uuid_when_context_is_empty(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="message",
            args=(),
            exc_info=None,
        )

        with patch(
            "app.log.get_context_var",
            return_value="-",
        ):
            result = RequestContextFilter().filter(record)

        self.assertTrue(result)
        self.assertEqual(record.request_uuid, "-")


class TestInitLogging(unittest.TestCase):

    def tearDown(self):
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)

    def test_configures_root_logger_with_stream_handler(self):
        config = MagicMock()
        config.LOG_LEVEL = "DEBUG"
        config.LOG_FORMAT = (
            "%(levelname)s %(request_uuid)s %(message)s"
        )

        with (
            patch("app.log.get_config", return_value=config),
            patch("app.log.sys.stdout", sys.stdout),
        ):
            init_logging()

        root_logger = logging.getLogger()

        self.assertEqual(root_logger.level, logging.DEBUG)
        self.assertEqual(len(root_logger.handlers), 1)

        handler = root_logger.handlers[0]

        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertIs(handler.stream, sys.stdout)
        self.assertEqual(len(handler.filters), 1)
        self.assertIsInstance(handler.filters[0], RequestContextFilter)
        self.assertIsInstance(handler.formatter, logging.Formatter)

    def test_replaces_existing_root_handlers(self):
        root_logger = logging.getLogger()
        old_handler = logging.NullHandler()
        root_logger.addHandler(old_handler)

        config = MagicMock()
        config.LOG_LEVEL = "INFO"
        config.LOG_FORMAT = "%(message)s"

        with patch("app.log.get_config", return_value=config):
            init_logging()

        root_logger = logging.getLogger()

        self.assertEqual(len(root_logger.handlers), 1)
        self.assertIsNot(root_logger.handlers[0], old_handler)

    def test_unknown_log_level_falls_back_to_info(self):
        config = MagicMock()
        config.LOG_LEVEL = "UNKNOWN"
        config.LOG_FORMAT = "%(message)s"

        with patch("app.log.get_config", return_value=config):
            init_logging()

        root_logger = logging.getLogger()

        self.assertEqual(root_logger.level, logging.INFO)
