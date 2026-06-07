# tests/repositories/test_orm.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class _TestBase(DeclarativeBase):
    pass


class _Sample(_TestBase):
    __tablename__ = "orm_test_sample"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(10))


class _Tree(_TestBase):
    __tablename__ = "orm_test_tree"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(50))


from tests.helpers import set_minimal_app_config_env  # noqa: E402


set_minimal_app_config_env()

import app.repositories.orm as orm  # noqa: E402


class TestORMRepository(unittest.IsolatedAsyncioTestCase):
    # --- insert ---

    async def test_insert_adds_flush_commit(self):
        session = MagicMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        out = await repo.insert(obj, flush=True, commit=True)

        session.add.assert_called_once_with(obj)
        session.flush.assert_awaited_once()
        session.commit.assert_awaited_once()
        self.assertIs(out, obj)

    async def test_insert_no_flush_no_commit(self):
        session = MagicMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        out = await repo.insert(obj, flush=False, commit=False)

        session.add.assert_called_once_with(obj)
        session.flush.assert_not_awaited()
        session.commit.assert_not_awaited()
        self.assertIs(out, obj)

    async def test_insert_commit_without_flush_both_paths_as_written(self):
        session = MagicMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        out = await repo.insert(obj, flush=False, commit=True)

        session.add.assert_called_once_with(obj)
        session.flush.assert_not_awaited()
        session.commit.assert_awaited_once()
        self.assertIs(out, obj)

    # --- select ---

    async def test_select_by_obj_id(self):
        session = MagicMock()
        found = _Sample()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = found
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.select(_Sample, obj_id=7)

        session.execute.assert_awaited_once()
        self.assertIs(out, found)

    async def test_select_with_filters(self):
        session = MagicMock()
        found = _Sample()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = found
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.select(_Sample, name__eq="x")

        self.assertIs(out, found)

    async def test_select_raises_when_obj_id_and_id_filter(self):
        session = MagicMock()
        session.execute = AsyncMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(ValueError):
            await repo.select(_Sample, obj_id=1, id=1)

        session.execute.assert_not_awaited()

    async def test_select_returns_none_when_not_found(self):
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.select(_Sample, obj_id=999)

        self.assertIsNone(out)
        session.execute.assert_awaited_once()

    async def test_select_obj_id_is_translated_to_id_filter(self):
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        await repo.select(_Sample, obj_id=7)

        executed_query = session.execute.await_args.args[0]
        compiled = str(
            executed_query.compile(compile_kwargs={"literal_binds": True})
        )

        self.assertIn("WHERE", compiled)
        self.assertIn("orm_test_sample.id = 7", compiled)
        self.assertIn("LIMIT 1", compiled)

    async def test_select_with_id_filter(self):
        session = MagicMock()
        found = _Sample()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = found
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.select(_Sample, id=5)

        self.assertIs(out, found)

        executed_query = session.execute.await_args.args[0]
        compiled = str(
            executed_query.compile(compile_kwargs={"literal_binds": True})
        )
        self.assertIn("orm_test_sample.id = 5", compiled)

    # --- update ---

    async def test_update_flush_commit(self):
        session = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        out = await repo.update(obj, flush=True, commit=True)

        session.flush.assert_awaited_once()
        session.commit.assert_awaited_once()
        self.assertIs(out, obj)

    async def test_update_no_flush_no_commit(self):
        session = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        out = await repo.update(obj, flush=False, commit=False)

        session.flush.assert_not_awaited()
        session.commit.assert_not_awaited()
        self.assertIs(out, obj)

    async def test_update_commit_without_flush(self):
        session = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        out = await repo.update(obj, flush=False, commit=True)

        session.flush.assert_not_awaited()
        session.commit.assert_awaited_once()
        self.assertIs(out, obj)

    # --- delete ---

    async def test_delete_session_delete_flush_commit(self):
        session = MagicMock()
        session.delete = AsyncMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        await repo.delete(obj, flush=True, commit=True)

        session.delete.assert_awaited_once_with(obj)
        session.flush.assert_awaited_once()
        session.commit.assert_awaited_once()

    async def test_delete_without_flush_and_commit(self):
        session = MagicMock()
        session.delete = AsyncMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        obj = _Sample()
        repo = orm.ORMRepository(session)

        await repo.delete(obj, flush=False, commit=False)

        session.delete.assert_awaited_once_with(obj)
        session.flush.assert_not_awaited()
        session.commit.assert_not_awaited()

    # --- select_parent_chain ---

    async def test_select_parent_chain_returns_empty_tuple_for_root(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        obj = _Tree()
        obj.id = 1
        obj.parent_id = None

        out = await repo.select_parent_chain(obj)

        self.assertEqual(out, ())
        session.execute.assert_not_called()

    async def test_select_parent_chain_executes_recursive_cte_query(self):
        session = MagicMock()
        session.execute = AsyncMock()

        result = MagicMock()
        result.scalars.return_value.all.return_value = ["parent", "root"]
        session.execute.return_value = result

        repo = orm.ORMRepository(session)

        obj = _Tree()
        obj.id = 3
        obj.parent_id = 2

        out = await repo.select_parent_chain(obj)

        self.assertEqual(out, ("parent", "root"))
        session.execute.assert_awaited_once()

        query = session.execute.await_args.args[0]
        query_sql = str(query)

        self.assertIn("WITH RECURSIVE parent_chain", query_sql)
        self.assertIn("UNION ALL", query_sql)
        self.assertIn("parent_chain.depth", query_sql)
        self.assertIn("ORDER BY parent_chain.depth", query_sql)

    async def test_select_parent_chain_uses_parent_id_as_anchor(self):
        session = MagicMock()
        session.execute = AsyncMock()

        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        repo = orm.ORMRepository(session)

        obj = _Tree()
        obj.id = 5
        obj.parent_id = 4

        await repo.select_parent_chain(obj)

        query = session.execute.await_args.args[0]
        query_sql = str(query.compile(compile_kwargs={"literal_binds": True}))

        self.assertIn("WHERE orm_test_tree.id = 4", query_sql)

    async def test_select_parent_chain_returns_tuple_not_list(self):
        session = MagicMock()
        session.execute = AsyncMock()

        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        repo = orm.ORMRepository(session)

        obj = _Tree()
        obj.id = 3
        obj.parent_id = 2

        out = await repo.select_parent_chain(obj)

        self.assertIsInstance(out, tuple)

    async def test_select_parent_chain_uses_custom_parent_id_attr(self):
        class _CustomTree(_TestBase):
            __tablename__ = "orm_test_custom_tree"

            id: Mapped[int] = mapped_column(Integer, primary_key=True)
            owner_id: Mapped[int | None] = mapped_column(
                Integer,
                nullable=True,
            )
            name: Mapped[str] = mapped_column(String(50))

        session = MagicMock()
        session.execute = AsyncMock()

        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        repo = orm.ORMRepository(session)

        obj = _CustomTree()
        obj.id = 3
        obj.owner_id = 2

        await repo.select_parent_chain(
            obj,
            parent_id_attr="owner_id",
        )

        query = session.execute.await_args.args[0]
        query_sql = str(query)

        self.assertIn("owner_id", query_sql)
        self.assertIn("WITH RECURSIVE parent_chain", query_sql)

    # --- select_all ---

    async def test_select_all_returns_list(self):
        session = MagicMock()
        rows = [_Sample(), _Sample()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = rows
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.select_all(_Sample)

        self.assertEqual(out, rows)

    async def test_select_all_with_filters_ordering_and_pagination(self):
        session = MagicMock()
        rows = [_Sample()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = rows
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.select_all(
            _Sample,
            status__eq="ok",
            order_by="name",
            order=orm.DESC,
            offset=2,
            limit=5,
        )

        self.assertEqual(out, rows)

        executed_query = session.execute.await_args.args[0]
        compiled = str(
            executed_query.compile(compile_kwargs={"literal_binds": True})
        )

        self.assertIn("WHERE", compiled)
        self.assertIn("status = 'ok'", compiled)
        self.assertIn("ORDER BY", compiled)
        self.assertIn("DESC", compiled)
        self.assertIn("LIMIT 5", compiled)
        self.assertIn("OFFSET 2", compiled)

    # --- count_all ---

    async def test_count_all_returns_scalar_int(self):
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 42
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.count_all(_Sample)

        self.assertEqual(out, 42)

    async def test_count_all_with_filters(self):
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        session.execute = AsyncMock(return_value=mock_result)
        repo = orm.ORMRepository(session)

        out = await repo.count_all(_Sample, status__eq="ok")

        self.assertEqual(out, 3)

        executed_query = session.execute.await_args.args[0]
        compiled = str(
            executed_query.compile(compile_kwargs={"literal_binds": True})
        )

        self.assertIn("count", compiled.lower())
        self.assertIn("status = 'ok'", compiled)

    # --- flush / commit / rollback ---

    async def test_flush_commit_rollback_delegate(self):
        session = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        repo = orm.ORMRepository(session)

        await repo.flush()
        await repo.commit()
        await repo.rollback()

        session.flush.assert_awaited_once()
        session.commit.assert_awaited_once()
        session.rollback.assert_awaited_once()

    # --- make_subquery ---

    def test_make_subquery(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        sq = repo.make_subquery(_Sample, "id", status__eq="ok")

        self.assertTrue(str(sq).startswith("SELECT"))

    def test_make_subquery_missing_column_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(AttributeError):
            repo.make_subquery(_Sample, "missing")

    # --- _split_filter_key ---

    def test_split_filter_key_plain_field(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        col, op = repo._split_filter_key("name")

        self.assertEqual(col, "name")
        self.assertEqual(op, "eq")

    def test_split_filter_key_with_operator(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        col, op = repo._split_filter_key("name__ne")

        self.assertEqual(col, "name")
        self.assertEqual(op, "ne")

    def test_split_filter_key_invalid_empty_column(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(ValueError):
            repo._split_filter_key("__ne")

    def test_split_filter_key_uses_last_separator(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        col, op = repo._split_filter_key("user__name__like")

        self.assertEqual(col, "user__name")
        self.assertEqual(op, "like")

    # --- _get_column ---

    def test_get_column_resolves_attribute(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        col = repo._get_column(_Sample, "name")

        self.assertIs(col, _Sample.name)

    def test_get_column_missing_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(AttributeError):
            repo._get_column(_Sample, "nope")

    # --- _build_where ---

    def test_build_where_eq_and_ne(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(_Sample, name="a", status__ne="b")

        self.assertEqual(len(conds), 2)

    def test_build_where_comparison_ops(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(
            _Sample,
            id__gt=1,
            id__ge=1,
            id__lt=10,
            id__le=10,
        )

        self.assertEqual(len(conds), 4)

    def test_build_where_in_requires_sequence(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(TypeError):
            repo._build_where(_Sample, id__in="not-a-seq")

    def test_build_where_in_accepts_tuple(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(_Sample, id__in=(1, 2))

        self.assertEqual(len(conds), 1)

    def test_build_where_like_ilike_require_str(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(TypeError):
            repo._build_where(_Sample, name__like=123)
        with self.assertRaises(TypeError):
            repo._build_where(_Sample, name__ilike=())

    def test_build_where_is_and_isnot(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(
            _Sample,
            name__is=None,
            status__isnot=None,
        )

        self.assertEqual(len(conds), 2)

    def test_build_where_subquery(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        inner = select(_Sample.id)

        conds = repo._build_where(_Sample, id__subquery=inner)

        self.assertEqual(len(conds), 1)

    def test_build_where_skips_reserved_keys(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(
            _Sample,
            name="x",
            order_by="name",
            order=orm.ASC,
            offset=0,
            limit=10,
        )

        self.assertEqual(len(conds), 1)

    def test_build_where_unsupported_operator(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(ValueError):
            repo._build_where(_Sample, name__bogus="x")

    def test_build_where_like_and_ilike(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(
            _Sample,
            name__like="a%",
            name__ilike="%b%",
        )

        self.assertEqual(len(conds), 2)

    def test_build_where_in_accepts_set(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(_Sample, id__in={1, 2, 3})

        self.assertEqual(len(conds), 1)

    def test_build_where_is_and_isnot_non_none(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        conds = repo._build_where(
            _Sample,
            name__is="abc",
            status__isnot="def",
        )

        self.assertEqual(len(conds), 2)

    def test_build_where_subquery_compiles(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        inner = select(_Sample.id).where(_Sample.status == "ok")

        conds = repo._build_where(_Sample, id__subquery=inner)

        self.assertEqual(len(conds), 1)
        compiled = str(
            conds[0].compile(compile_kwargs={"literal_binds": True})
        )
        self.assertIn("IN", compiled)
        self.assertIn("SELECT", compiled)

    def test_build_where_missing_column_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)

        with self.assertRaises(AttributeError):
            repo._build_where(_Sample, missing__eq=1)

    # --- _apply_ordering ---

    def test_apply_ordering_none_returns_query(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        out = repo._apply_ordering(_Sample, q)

        self.assertIs(out, q)

    def test_apply_ordering_rand(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        out = repo._apply_ordering(_Sample, q, order=orm.RAND)

        compiled = str(out.compile(compile_kwargs={"literal_binds": False}))
        self.assertIn("random", compiled.lower())

    def test_apply_ordering_asc_desc(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        asc_q = repo._apply_ordering(
            _Sample,
            q,
            order_by="name",
            order=orm.ASC,
        )
        desc_q = repo._apply_ordering(
            _Sample,
            q,
            order_by="name",
            order=orm.DESC,
        )

        self.assertIn("ORDER BY", str(asc_q.compile()))
        self.assertIn("ORDER BY", str(desc_q.compile()))

    def test_apply_ordering_unsupported_order(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        with self.assertRaises(ValueError):
            repo._apply_ordering(
                _Sample,
                q,
                order_by="name",
                order="sideways",
            )

    def test_apply_ordering_with_order_but_no_order_by_returns_query(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        out = repo._apply_ordering(_Sample, q, order=orm.DESC)

        self.assertIs(out, q)

    def test_apply_ordering_missing_column_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        with self.assertRaises(AttributeError):
            repo._apply_ordering(
                _Sample,
                q,
                order_by="missing",
                order=orm.ASC,
            )

    # --- _apply_pagination ---

    def test_apply_pagination_offset_limit(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        out = repo._apply_pagination(q, offset=5, limit=3)

        self.assertIn("LIMIT", str(out.compile()))
        self.assertIn("OFFSET", str(out.compile()))

    def test_apply_pagination_negative_offset_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        with self.assertRaises(ValueError):
            repo._apply_pagination(q, offset=-1)

    def test_apply_pagination_non_int_offset_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        with self.assertRaises(ValueError):
            repo._apply_pagination(q, offset="0")

    def test_apply_pagination_negative_limit_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        with self.assertRaises(ValueError):
            repo._apply_pagination(q, limit=-1)

    def test_apply_pagination_non_int_limit_raises(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        with self.assertRaises(ValueError):
            repo._apply_pagination(q, limit="10")

    def test_apply_pagination_without_values_returns_same_query(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        out = repo._apply_pagination(q)

        self.assertIs(out, q)

    def test_apply_pagination_zero_offset_and_limit(self):
        session = MagicMock()
        repo = orm.ORMRepository(session)
        q = select(_Sample)

        out = repo._apply_pagination(q, offset=0, limit=0)

        compiled = str(out.compile())
        self.assertIn("LIMIT", compiled)
        self.assertIn("OFFSET", compiled)
