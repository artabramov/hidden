# app/repositories/orm.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Any

from sqlalchemy import Select, asc, desc, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import ColumnElement

from app.db.base import Base

ID = "id"
ORDER_BY = "order_by"
ORDER = "order"
OFFSET = "offset"
LIMIT = "limit"
ASC = "asc"
DESC = "desc"
RAND = "rand"

RESERVED_KEYS = {ORDER_BY, ORDER, OFFSET, LIMIT}


class ORMRepository:
    """
    Generic async repository for SQLAlchemy ORM models. Provides
    CRUD operations, filtering, ordering, pagination, and helpers.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with active async SQLAlchemy session.
        Session is reused by all repository operations.
        """
        self.session = session

    async def insert(
        self,
        obj: Base,
        flush: bool = True,
        commit: bool = False,
    ) -> Base:
        """
        Add ORM object to current session and optionally persist it.
        Returns the same object after optional flush or commit.
        """
        self.session.add(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

        return obj

    async def select(
        self,
        cls: type[Base],
        obj_id: Any | None = None,
        **filters: Any,
    ) -> Base | None:
        """
        Select single ORM object by id or dynamic filters.
        Returns first matching object or None when nothing is found.
        """
        if obj_id is not None and ID in filters:
            raise ValueError("Use either obj_id or id filter, not both")

        query = select(cls)

        if obj_id is not None:
            filters[ID] = obj_id

        query = query.where(*self._build_where(cls, **filters)).limit(1)

        result = await self.session.execute(query)
        return result.scalars().first()

    async def update(
        self,
        obj: Base,
        flush: bool = True,
        commit: bool = False,
    ) -> Base:
        """
        Flush or commit changes for already attached ORM object.
        Returns the same updated object instance.
        """
        if flush:
            await self.flush()

        if commit:
            await self.commit()

        return obj

    async def delete(
        self,
        obj: Base,
        flush: bool = True,
        commit: bool = False,
    ) -> None:
        """
        Delete ORM object from current session and optionally persist it.
        Flushes or commits the deletion depending on method flags.
        """
        await self.session.delete(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    async def select_all(
        self,
        cls: type[Base],
        **filters: Any,
    ) -> list[Base]:
        """
        Select all ORM objects matching dynamic filters.
        Applies filtering, ordering, and pagination to the query.
        """
        query = select(cls).where(*self._build_where(cls, **filters))
        query = self._apply_ordering(cls, query, **filters)
        query = self._apply_pagination(query, **filters)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def select_parent_chain(
        self,
        obj: Base,
        parent_id_attr: str = "parent_id",
    ) -> tuple[Base, ...]:
        """
        Return parent chain for a self-referential ORM object using a
        recursive CTE. Parents are returned as an ordered tuple:
        (direct parent, ..., root). Returns empty tuple if no parent.
        Performs a single query and does not rely on ORM relationships.
        """
        cls = type(obj)
        parent_id = getattr(obj, parent_id_attr)

        if parent_id is None:
            return ()

        id_column = getattr(cls, "id")

        chain = (
            select(
                cls,
                literal(1).label("depth"),
            )
            .where(id_column == parent_id)
            .cte(name="parent_chain", recursive=True)
        )

        parent_alias = aliased(cls)

        chain = chain.union_all(
            select(
                parent_alias,
                (chain.c.depth + 1).label("depth"),
            )
            .where(getattr(parent_alias, "id") == getattr(
                chain.c, parent_id_attr
            ))
        )

        result = await self.session.execute(
            select(cls)
            .join(chain, id_column == chain.c.id)
            .order_by(chain.c.depth)
        )

        return tuple(result.scalars().all())

    async def count_all(
        self,
        cls: type[Base],
        **filters: Any,
    ) -> int:
        """
        Count ORM objects matching dynamic filters.
        Returns integer count for the generated query.
        """
        query = select(func.count()).select_from(cls)
        query = query.where(*self._build_where(cls, **filters))

        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def flush(self) -> None:
        """
        Flush pending session changes without committing transaction.
        Makes generated values available inside current transaction.
        """
        await self.session.flush()

    async def commit(self) -> None:
        """
        Commit current session transaction.
        Persists all pending changes to the database.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Roll back current session transaction.
        Discards all uncommitted changes in current unit of work.
        """
        await self.session.rollback()

    def make_subquery(
        self,
        cls: type[Base],
        column_name: str,
        **filters: Any,
    ):
        """
        Build SELECT subquery for one mapped column with dynamic filters.
        Returns SQLAlchemy selectable suitable for nested conditions.
        """
        column = self._get_column(cls, column_name)
        return select(column).where(*self._build_where(cls, **filters))

    def _build_where(
        self,
        cls: type[Base],
        **filters: Any,
    ) -> list[ColumnElement[bool]]:
        """
        Convert dynamic filter mapping into SQLAlchemy WHERE conditions.
        Supports comparison, membership, null, pattern, and subquery
        filters.

        Filtering syntax:
        - field=value
        - field__eq=value
        - field__ne=value
        - field__gt=value
        - field__ge=value
        - field__lt=value
        - field__le=value
        - field__in=[...]
        - field__like="abc%"
        - field__ilike="%abc%"
        - field__is=None
        - field__isnot=None
        - field__subquery=select(...)
        """
        conditions: list[ColumnElement[bool]] = []

        for key, value in filters.items():
            if key in RESERVED_KEYS:
                continue

            column_name, operator = self._split_filter_key(key)
            column = self._get_column(cls, column_name)

            if operator == "eq":
                conditions.append(column == value)
            elif operator == "ne":
                conditions.append(column != value)
            elif operator == "gt":
                conditions.append(column > value)
            elif operator == "ge":
                conditions.append(column >= value)
            elif operator == "lt":
                conditions.append(column < value)
            elif operator == "le":
                conditions.append(column <= value)
            elif operator == "in":
                if not isinstance(value, (list, tuple, set)):
                    raise TypeError("Filter expects list, tuple, or set")
                conditions.append(column.in_(value))
            elif operator == "like":
                if not isinstance(value, str):
                    raise TypeError("Filter expects str")
                conditions.append(column.like(value))
            elif operator == "ilike":
                if not isinstance(value, str):
                    raise TypeError("Filter expects str")
                conditions.append(column.ilike(value))
            elif operator == "is":
                conditions.append(column.is_(value))
            elif operator == "isnot":
                conditions.append(column.is_not(value))
            elif operator == "subquery":
                conditions.append(column.in_(value))
            else:
                raise ValueError("Unsupported operator in filter")

        return conditions

    def _apply_ordering(
        self,
        cls: type[Base],
        query: Select[Any],
        **filters: Any,
    ) -> Select[Any]:
        """
        Apply ORDER BY clause to query from reserved filter keys.
        Supports ascending, descending, and random ordering modes.
        """
        order_by_name = filters.get(ORDER_BY)
        order = filters.get(ORDER, ASC)

        if order == RAND:
            return query.order_by(func.random())

        if order_by_name is None:
            return query

        column = self._get_column(cls, order_by_name)

        if order == ASC:
            return query.order_by(asc(column))
        if order == DESC:
            return query.order_by(desc(column))

        raise ValueError("Unsupported order")

    def _apply_pagination(
        self,
        query: Select[Any],
        **filters: Any,
    ) -> Select[Any]:
        """
        Apply offset and limit pagination parameters to query.
        Accepts only non-negative integer values for both parameters.
        """
        offset = filters.get(OFFSET)
        limit = filters.get(LIMIT)

        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("Offset must be a non-negative integer")
            query = query.offset(offset)

        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                raise ValueError("Limit must be a non-negative integer")
            query = query.limit(limit)

        return query

    def _split_filter_key(self, key: str) -> tuple[str, str]:
        """
        Split dynamic filter key into column name and operator.
        Uses equality operator when filter key has no explicit suffix.
        """
        if "__" not in key:
            return key, "eq"

        column_name, operator = key.rsplit("__", 1)

        if not column_name:
            raise ValueError(f"Invalid filter key '{key}'")

        return column_name, operator

    def _get_column(self, cls: type[Base], column_name: str):
        """
        Resolve mapped model attribute by its column name.
        Raises AttributeError when model has no such mapped attribute.
        """
        if not hasattr(cls, column_name):
            raise AttributeError(f"Model has no column '{column_name}'")
        return getattr(cls, column_name)
