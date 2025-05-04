import unittest
from unittest.mock import patch, MagicMock
from app.log import get_log, ContextualFilter


class LogTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.log.ctx")
    def test_contextual_filter(self, ctx_mock):
        ctx_mock.request_uuid = "abcd-1234"
        msg = MagicMock()

        contextual_filter = ContextualFilter()
        result = contextual_filter.filter(msg)

        self.assertTrue(result)
        msg.request_uuid = ctx_mock.request_uuid

    @patch("app.log.ContextualFilter")
    @patch("app.log.logging")
    @patch("app.log.RotatingFileHandler")
    @patch("app.log.cfg")
    def test_get_log(self, cfg_mock, HandlerMock, logging_mock, FilterMock):
        cfg_mock.LOG_FILENAME = "filename"
        cfg_mock.LOG_FILESIZE = 1234
        cfg_mock.LOG_FILES_LIMIT = 5
        cfg_mock.LOG_FORMAT = "format"
        cfg_mock.LOG_NAME = "name"
        cfg_mock.LOG_LEVEL = "level"

        handler_mock = MagicMock()
        HandlerMock.return_value = handler_mock

        log_mock = MagicMock()
        logging_mock.getLogger.return_value = log_mock

        get_log.cache_clear()
        result = get_log()
        self.assertEqual(result, log_mock)

        HandlerMock.assert_called_with(
            filename=cfg_mock.LOG_FILENAME,
            maxBytes=cfg_mock.LOG_FILESIZE,
            backupCount=cfg_mock.LOG_FILES_LIMIT
        )
        logging_mock.Formatter.assert_called_with(cfg_mock.LOG_FORMAT)
        handler_mock.setFormatter.assert_called_with(
            logging_mock.Formatter.return_value
        )
        logging_mock.getLogger.assert_called_with(cfg_mock.LOG_NAME)
        log_mock.addHandler.assert_called_with(handler_mock)
        log_mock.addFilter.assert_called_with(FilterMock.return_value)
        log_mock.setLevel.assert_called_with(cfg_mock.LOG_LEVEL)


if __name__ == "__main__":
    unittest.main()
