"""
Asynchronous data-access manager that wraps an ORM session with a
small, consistent interface for common patterns: existence checks,
single-record fetches, list retrieval with keyword-style filters,
ordering and pagination, textual statements, batched deletions, and
simple aggregates such as counts and sums. Queries are constructed from
field/operator pairs, support membership and pattern matching, and can
emit subqueries for use in higher-level filters. The API keeps
transaction control explicit with flush/commit/rollback helpers and
avoids blocking by leveraging the underlying async engine.
"""


from typing import Union, Type, List, Optional
from sqlalchemy import select, text, asc, desc
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

ID = "id"
SUBQUERY = "subquery"
ORDER_BY, ORDER = "order_by", "order"
ASC, DESC, RAND = "asc", "desc", "rand"
OFFSET, LIMIT = "offset", "limit"
RESERVED_KEYS = {SUBQUERY, ORDER_BY, ORDER, OFFSET, LIMIT}
RESERVED_OPERATORS = {
    "in": "in_",
    "eq": "__eq__",
    "ne": "__ne__",
    "ge": "__ge__",
    "le": "__le__",
    "gt": "__gt__",
    "lt": "__lt__",
    "like": "like",
    "ilike": "ilike",
}
DELETE_ALL_BATCH_SIZE = 500

# NOTE: On all SQLAlchemy models set sqlite_autoincrement to True in
# __table_args__ to prevent ID reuse after deletes in SQLite; primary
# key alone is not enough.


class EntityManager:
    """
    Coordinates database operations for ORM entities over an async
    session. Exposes CRUD, query helpers, aggregation, and transaction
    control.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the class with an asynchronous SQLAlchemy session.
        """
        self.session = session

    async def exists(self, cls: Type[DeclarativeBase], **kwargs) -> bool:
        """
        Checks if an entity of the SQLAlchemy model class exists
        in the database based on the provided filters.
        """
        query = select(1).select_from(cls).where(
            *self._where(cls, **kwargs)).limit(1)
        res = await self.session.execute(query)
        return res.scalar_one_or_none() is not None

    async def insert(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = True):
        """
        Adds a new entity to the current unit of work. Optionally
        flushes pending changes and commits the transaction.
        """
        self.session.add(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    async def select(self, cls: Type[DeclarativeBase],
                     obj_id: int) -> Union[DeclarativeBase, None]:
        """
        Fetches a single entity by its primary identifier. Returns
        the matching record or None when absent.
        """
        async_result = await self.session.execute(
            select(cls).where(getattr(cls, ID) == obj_id).limit(1))
        return async_result.unique().scalars().one_or_none()

    async def select_by(self, cls: Type[DeclarativeBase],
                        **kwargs) -> Union[DeclarativeBase, None]:
        """
        Fetches a single entity using filter criteria. Returns
        the first match or None when nothing qualifies.
        """
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none()

    async def select_all(self, cls: Type[DeclarativeBase],
                         **kwargs) -> List[DeclarativeBase]:
        """
        Returns all entities matching filters with optional ordering
        and pagination. Intended for result lists without eager loading
        or joins.
        """
        query = select(cls).where(*self._where(cls, **kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(getattr(cls, ID).in_(kwargs[SUBQUERY]))

        if ORDER_BY in kwargs and ORDER in kwargs:
            query = query.order_by(self._order_by(cls, **kwargs))

        if OFFSET in kwargs:
            query = query.offset(self._offset(**kwargs))

        if LIMIT in kwargs:
            query = query.limit(self._limit(**kwargs))

        async_result = await self.session.execute(query)
        data = async_result.unique().scalars().all()
        return data

    async def select_rows(self, sql: str) -> list:
        """
        Executes a textual statement and returns raw result rows.
        """
        async_result = await self.session.execute(text(sql))
        return async_result.all()

    async def update(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = False):
        """
        Merges an entity's state into the current unit of work.
        Optionally flushes pending changes and commits the transaction.
        """
        await self.session.merge(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    async def delete(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = False):
        """
        Marks an entity for removal from persistent storage. Optionally
        flushes pending changes and commits the transaction.
        """
        managed = await self.session.merge(obj)
        await self.session.delete(managed)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    async def delete_all(self, cls: Type[DeclarativeBase], flush: bool = True,
                         commit: bool = False, **kwargs):
        """
        Removes entities matching filters in bounded batches. Iterates
        until no further matches remain, minimizing pressure.
        """
        kwargs = kwargs | {ORDER_BY: ID, ORDER: ASC, OFFSET: 0,
                           LIMIT: DELETE_ALL_BATCH_SIZE}

        while objs := await self.select_all(cls, **kwargs):
            kwargs[OFFSET] += kwargs[LIMIT]
            for obj in objs:
                await self.delete(obj, flush=flush, commit=commit)

    async def count_all(self, cls: Type[DeclarativeBase], **kwargs) -> int:
        """
        Counts entities matching the given criteria using an aggregate
        query. Returns zero when no rows qualify.
        """
        query = select(func.count(getattr(cls, ID))).where(
                *self._where(cls, **kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(getattr(cls, ID).in_(kwargs[SUBQUERY]))

        async_result = await self.session.execute(query)
        return async_result.unique().scalars().one_or_none() or 0

    async def sum_all(self, cls: Type[DeclarativeBase], column_name: str,
                      **kwargs) -> int:
        """
        Computes a sum over a numeric column for entities matching
        filters. Returns zero when no rows qualify or the aggregate
        is null.
        """
        query = select(func.sum(getattr(cls, column_name))).where(
            *self._where(cls, **kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(getattr(cls, ID).in_(kwargs[SUBQUERY]))

        async_result = await self.session.execute(query)
        return async_result.unique().scalars().one_or_none() or 0

    async def subquery(self, cls: Type[DeclarativeBase],
                       foreign_key: str, **kwargs) -> select:
        """
        Constructs a subquery for the given SQLAlchemy model class,
        selecting the values of the specified foreign key column and
        applying the provided filters. It builds a subquery object that
        can be used to filter other queries based on the foreign key.
        """
        subquery = select(getattr(cls, foreign_key)).filter(
            *self._where(cls, **kwargs)).subquery()
        return subquery

    async def flush(self):
        """
        Synchronizes pending changes in the session with the database.
        Does not finalize the transaction or release locks.
        """
        await self.session.flush()

    async def commit(self):
        """
        Commits all changes made during the current transaction, making
        them permanent in the database.
        """
        await self.session.commit()

    async def rollback(self):
        """
        Reverts all changes made during the current transaction, undoing
        any modifications to maintain consistency.
        """
        await self.session.rollback()

    def _where(self, cls: Type[DeclarativeBase], **kwargs) -> list:
        """
        Constructs predicate expressions from keyword-style criteria.
        Supports comparisons, membership checks, and pattern matching.
        """
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in RESERVED_KEYS}:
            column_name, operator = key.split("__", 1)

            if hasattr(cls, column_name):
                value = kwargs[key]

                if value is not None or operator == "ne":
                    if operator == "in":
                        value = [x.strip() for x in value.split(",")]

                    elif operator in ["like", "ilike"]:
                        value = f"%{value}%"

                    column = getattr(cls, column_name)
                    operation = getattr(
                        column, RESERVED_OPERATORS[operator])(value)
                    where.append(operation)
        return where

    def _order_by(self, cls: Type[DeclarativeBase],
                  **kwargs) -> Union[asc, desc, None]:
        """
        Builds an ordering expression from provided options. Supports
        ascending, descending, and randomized order.
        """
        if ORDER_BY in kwargs and kwargs[ORDER_BY]:
            order_by = getattr(cls, kwargs[ORDER_BY])
        else:
            order_by = getattr(cls, ID)

        if ORDER in kwargs and kwargs[ORDER]:
            order = kwargs[ORDER]
        else:
            order = ASC

        if order == ASC:
            return asc(order_by)

        elif order == DESC:
            return desc(order_by)

        elif order == RAND:
            return func.random()

    def _offset(self, **kwargs) -> Optional[int]:
        """
        Retrieves the starting point for pagination from the keyword
        arguments, indicating where the query results should start.
        """
        return kwargs.get(OFFSET)

    def _limit(self, **kwargs) -> Optional[int]:
        """
        Retrieves the maximum number of results to return from the
        keyword arguments, capping the number of query results.
        """
        return kwargs.get(LIMIT)
