# tests/test_log.py
# SPDX-License-Identifier: Apache-2.0

import io
import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

from app.context import reset_context, set_context_var
from app.log import RequestContextFilter, init_logging


class TestRequestContextFilter(unittest.TestCase):
    def setUp(self):
        reset_context()

    def tearDown(self):
        reset_context()

    def test_adds_request_identifier(self):
        record = logging.LogRecord(
            name="hidden",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        log_filter = RequestContextFilter()

        self.assertTrue(log_filter.filter(record))
        self.assertEqual(record.request_uuid, "-")

        set_context_var("request_uuid", "req-1")
        self.assertTrue(log_filter.filter(record))
        self.assertEqual(record.request_uuid, "req-1")


class TestInitLogging(unittest.TestCase):
    def setUp(self):
        reset_context()
        root = logging.getLogger()
        self._handlers = list(root.handlers)
        self._level = root.level

    def tearDown(self):
        reset_context()
        root = logging.getLogger()
        root.handlers.clear()
        for handler in self._handlers:
            root.addHandler(handler)
        root.setLevel(self._level)

    def test_configures_stdout_handler(self):
        config = MagicMock()
        config.LOG_LEVEL = "warning"
        config.LOG_FORMAT = (
            "%(levelname)s request_uuid=%(request_uuid)s %(message)s"
        )
        buffer = io.StringIO()
        set_context_var("request_uuid", "req-1")

        with (
            patch("app.log.get_config", return_value=config),
            patch("app.log.sys.stdout", buffer),
        ):
            init_logging()
            first = logging.getLogger().handlers[0]
            init_logging()
            logging.getLogger("hidden.test").warning("hello")

        root = logging.getLogger()
        handler = root.handlers[0]
        self.assertEqual(root.level, logging.WARNING)
        self.assertEqual(len(root.handlers), 1)
        self.assertIsNot(handler, first)
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertIs(handler.stream, buffer)
        self.assertIsNot(handler.stream, sys.stdout)
        self.assertEqual(handler.formatter._fmt, config.LOG_FORMAT)
        self.assertIsInstance(handler.filters[0], RequestContextFilter)
        self.assertEqual(
            buffer.getvalue().strip(),
            "WARNING request_uuid=req-1 hello",
        )

    def test_unknown_level_falls_back_to_info(self):
        config = MagicMock()
        config.LOG_LEVEL = "nope"
        config.LOG_FORMAT = "%(message)s"

        with (
            patch("app.log.get_config", return_value=config),
            patch("app.log.sys.stdout", io.StringIO()),
        ):
            init_logging()

        self.assertEqual(logging.getLogger().level, logging.INFO)
