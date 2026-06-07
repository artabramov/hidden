# tests/services/test_file_tag_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.schemas.file_tag_list import TagListRequest
from app.services.file_tag_list import list_tags


def _make_execute_result(rows):
    """
    Build a mock that mimics session.execute() returning an object
    whose .all() yields the given rows.
    """
    result = MagicMock()
    result.all.return_value = rows
    return AsyncMock(return_value=result)


class TestListTags(unittest.IsolatedAsyncioTestCase):

    async def test_returns_top_tags_ordered_by_count(self):
        rows = [
            SimpleNamespace(tag="python", usage_count=10),
            SimpleNamespace(tag="fastapi", usage_count=7),
            SimpleNamespace(tag="docs", usage_count=3),
        ]
        session = AsyncMock()
        session.execute = _make_execute_result(rows)

        params = TagListRequest(limit=3)

        tags = await list_tags(session=session, params=params)

        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], ("python", 10))
        self.assertEqual(tags[1], ("fastapi", 7))
        self.assertEqual(tags[2], ("docs", 3))

    async def test_returns_empty_list_when_no_tags(self):
        session = AsyncMock()
        session.execute = _make_execute_result(rows=[])

        params = TagListRequest(limit=50)

        tags = await list_tags(session=session, params=params)

        self.assertEqual(tags, [])

    async def test_executes_one_query(self):
        session = AsyncMock()
        session.execute = _make_execute_result(rows=[])

        params = TagListRequest(limit=10)

        await list_tags(session=session, params=params)

        self.assertEqual(session.execute.await_count, 1)

    async def test_limit_applied_via_query(self):
        rows = [
            SimpleNamespace(tag=f"tag{i}", usage_count=10 - i)
            for i in range(5)
        ]
        session = AsyncMock()
        session.execute = _make_execute_result(rows=rows)

        params = TagListRequest(limit=5)

        tags = await list_tags(session=session, params=params)

        self.assertEqual(len(tags), 5)

    async def test_logs_started_and_completed(self):
        session = AsyncMock()
        session.execute = _make_execute_result(rows=[])

        params = TagListRequest(limit=10)

        with patch("app.services.file_tag_list.log") as mock_log:
            await list_tags(session=session, params=params)

        calls = [str(c) for c in mock_log.info.call_args_list]
        self.assertTrue(
            any(E.TAG_LIST_STARTED in c for c in calls),
            "Expected TAG_LIST_STARTED to be logged",
        )
        self.assertTrue(
            any(E.TAG_LIST_COMPLETED in c for c in calls),
            "Expected TAG_LIST_COMPLETED to be logged",
        )

    async def test_default_limit_is_fifty(self):
        params = TagListRequest()
        self.assertEqual(params.limit, 50)

    async def test_limit_maximum_is_one_thousand(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TagListRequest(limit=1001)

    async def test_limit_minimum_is_one(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TagListRequest(limit=0)
