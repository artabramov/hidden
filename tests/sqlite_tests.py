import unittest
from types import SimpleNamespace
from unittest.mock import patch
from sqlalchemy import MetaData
from app.sqlite import SessionManager, get_session, init_database, Base


class FakeSession:
    def __init__(self):
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1

    async def close(self):
        self.close_calls += 1


class FakeConn:
    def __init__(self):
        self.run_sync_called_with = None

    async def run_sync(self, fn):
        self.run_sync_called_with = fn


class FakeBeginCtx:
    def __init__(self, conn: FakeConn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class SqliteTest(unittest.IsolatedAsyncioTestCase):
    @patch("app.sqlite.async_sessionmaker")
    @patch("app.sqlite.event.listens_for")
    @patch("app.sqlite.create_async_engine")
    @patch("app.sqlite.Path.mkdir")
    async def test_session_manager_no_side_effects(
        self, mkdir_mock, create_engine_mock, listens_for_mock,
        sessionmaker_mock
    ):
        listens_for_mock.side_effect = lambda *a, **k: (lambda fn: fn)
        fake_engine = SimpleNamespace(sync_engine=object())
        create_engine_mock.return_value = fake_engine
        sessionmaker_mock.return_value = "SM"

        sm = SessionManager(sqlite_path="/any/path/test.db", sql_echo=True)

        mkdir_mock.assert_called_once()
        create_engine_mock.assert_called_once()
        sessionmaker_mock.assert_called_once()
        self.assertEqual(sm.async_sessionmaker, "SM")

    async def test_dependency_get_session_commit(self):
        fake_session = FakeSession()
        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(
                    sessionmanager=SimpleNamespace(
                        get_session=lambda: fake_session)
                )
            )
        )

        agen = get_session(request)
        s = await agen.__anext__()
        self.assertIs(s, fake_session)

        try:
            await agen.asend(None)
        except StopAsyncIteration:
            pass

        self.assertEqual(fake_session.commit_calls, 1)
        self.assertEqual(fake_session.rollback_calls, 0)
        self.assertEqual(fake_session.close_calls, 1)

    async def test_dependency_get_session_rollback_on_error(self):
        fake_session = FakeSession()
        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(
                    sessionmanager=SimpleNamespace(
                        get_session=lambda: fake_session)
                )
            )
        )

        agen = get_session(request)
        _ = await agen.__anext__()

        with self.assertRaises(RuntimeError):
            await agen.athrow(RuntimeError("boom"))

        self.assertEqual(fake_session.commit_calls, 0)
        self.assertEqual(fake_session.rollback_calls, 1)
        self.assertEqual(fake_session.close_calls, 1)

    async def test_init_database_calls_create_all(self):
        fake_conn = FakeConn()
        fake_begin_ctx = FakeBeginCtx(fake_conn)
        fake_engine = SimpleNamespace(begin=lambda: fake_begin_ctx)
        fake_sm = SimpleNamespace(async_engine=fake_engine)

        await init_database(fake_sm)

        fn = fake_conn.run_sync_called_with
        self.assertTrue(callable(fn))
        self.assertEqual(getattr(fn, "__name__", ""), "create_all")
        self.assertIs(fn.__self__, Base.metadata)
        self.assertIsInstance(fn.__self__, MetaData)
