
"""
The module defines the class for managing database operations with
SQLAlchemy model classes using an asynchronous SQLAlchemy session.
The class supports operations such as inserting, updating, deleting,
and selecting SQLAlchemy model instances, as well as summing column
values and locking tables to prevent modifications. The class is
designed to work with large datasets and integrates with SQLAlchemy
asynchronous capabilities for non-blocking database interactions.
"""

from typing import Union, Type, List, Optional
from sqlalchemy import select, text, asc, desc
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.decorators.timed_decorator import timed

ID = "id"
SUBQUERY = "subquery"
ORDER_BY, ORDER = "order_by", "order"
ASC, DESC, RAND = "asc", "desc", "rand"
OFFSET, LIMIT = "offset", "limit"
RESERVED_KEYS = [SUBQUERY, ORDER_BY, ORDER, OFFSET, LIMIT]
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


class EntityManager:
    """
    Manages database operations for SQLAlchemy model classes. Provides
    methods to perform CRUD operations, count records, aggregate data,
    and manage transactions using an asynchronous SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the class with a Postgres connection."""
        self.session = session

    @timed
    async def exists(self, cls: Type[DeclarativeBase], **kwargs) -> bool:
        """
        Checks if an entity of the SQLAlchemy model class exists
        in the database based on the provided filters.
        """
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none() is not None

    @timed
    async def insert(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = True):
        """
        Inserts a new SQLAlchemy model instance into the database by
        adding the given entity to the session and saving it. The "flush"
        parameter determines whether to immediately send changes to the
        database. The "commit" parameter specifies whether to finalize
        the transaction and persist changes.
        """
        self.session.add(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def select(self, cls: Type[DeclarativeBase],
                     obj_id: int) -> Union[DeclarativeBase, None]:
        """
        Retrieves a SQLAlchemy model instance of the specified class
        by its ID.
        """
        async_result = await self.session.execute(
            select(cls).where(cls.id == obj_id).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_by(self, cls: Type[DeclarativeBase],
                        **kwargs) -> Union[DeclarativeBase, None]:
        """
        Retrieves a SQLAlchemy model instance based on the provided
        filters by constructing a query to find a single entity that
        matches the criteria.
        """
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_all(self, cls: Type[DeclarativeBase],
                         **kwargs) -> List[DeclarativeBase]:
        """
        Retrieves all SQLAlchemy model instances of the specified class
        that match the provided filters by constructing a query with
        optional ordering, pagination, and limiting.
        """
        query = select(cls).where(*self._where(cls, **kwargs))

        if ORDER_BY in kwargs and ORDER in kwargs:
            query = query.order_by(self._order_by(cls, **kwargs))

        if OFFSET in kwargs:
            query = query.offset(self._offset(**kwargs))

        if LIMIT in kwargs:
            query = query.limit(self._limit(**kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(cls.id.in_(kwargs[SUBQUERY]))

        async_result = await self.session.execute(query)
        data = async_result.unique().scalars().all()
        return data

    @timed
    async def select_rows(self, sql: str) -> list:
        """Executes the SQL query and return all result rows."""
        async_result = await self.session.execute(text(sql))
        return async_result.fetchall()

    @timed
    async def update(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = False):
        """
        Updates an existing SQLAlchemy model instance in the database
        by merging the changes of the given entity with the session. The
        "flush" parameter determines whether to immediately send changes
        to the database. The "commit" parameter specifies whether to
        finalize the transaction and persist changes.
        """
        await self.session.merge(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def delete(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = False):
        """
        Deletes a SQLAlchemy model instance from the database by
        removing the specified entity from the session. It marks the
        object for deletion, and changes will not be persisted until
        the session is flushed or committed. The "flush" parameter
        determines whether to immediately send changes to the database.
        The "commit" parameter indicates whether to finalize the
        deletion in the database.
        """
        await self.session.delete(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def delete_all(self, cls: Type[DeclarativeBase], flush: bool = True,
                         commit: bool = False, **kwargs):
        """
        Deletes all SQLAlchemy model instances of the specified class
        that match the provided filters by constructing a query for
        deletion and handling large datasets in batches. The "flush"
        parameter determines whether to immediately send changes to
        the database. The "commit" parameter indicates whether to
        finalize the deletions in the database.
        """
        kwargs = kwargs | {ORDER_BY: ID, ORDER: ASC, OFFSET: 0,
                           LIMIT: DELETE_ALL_BATCH_SIZE}

        while objs := await self.select_all(cls, **kwargs):
            kwargs[OFFSET] += kwargs[LIMIT]
            for obj in objs:
                await self.delete(obj, flush=flush, commit=commit)

    @timed
    async def count_all(self, cls: Type[DeclarativeBase], **kwargs) -> int:
        """
        Counta the number of SQLAlchemy model instances of the specified
        class that match the provided filters by constructing a query
        to count all entities meeting the criteria.
        """
        query = select(func.count(getattr(cls, ID))).where(
                *self._where(cls, **kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(cls.id.in_(kwargs[SUBQUERY]))

        async_result = await self.session.execute(query)
        return async_result.unique().scalars().one_or_none() or 0

    @timed
    async def sum_all(self, cls: Type[DeclarativeBase], column_name: str,
                      **kwargs) -> int:
        """
        Sums the values of a specified column for all SQLAlchemy model
        instances matching the filters. Constructs a query to calculate
        the sum of the values in the specified column for entities
        meeting the criteria.
        """
        query = select(func.sum(getattr(cls, column_name))).where(
            *self._where(cls, **kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(cls.id.in_(kwargs[SUBQUERY]))

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

    @timed
    async def flush(self):
        """
        Flushes the session to synchronize with the database. Sends all
        pending changes in the session to the database but does not
        commit the transaction.
        """
        await self.session.flush()

    @timed
    async def commit(self):
        """
        Commits all changes made during the current transaction, making
        them permanent in the database.
        """
        await self.session.commit()

    @timed
    async def rollback(self):
        """
        Reverts all changes made during the current transaction, undoing
        any modifications to maintain consistency.
        """
        await self.session.rollback()

    def _where(self, cls: Type[DeclarativeBase], **kwargs) -> list:
        """
        Construct a "where" clause from the provided filter criteria for
        SQLAlchemy queries. Builds SQLAlchemy filter conditions based on
        keyword arguments to be used in a query.
        """
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in RESERVED_KEYS}:
            column_name, operator = key.split("__")

            if hasattr(cls, column_name):
                value = kwargs[key]

                if value is not None or operator == "ne":
                    if operator == "in":
                        value = [x.strip() for x in value.split(",")]

                    elif operator in ["like", "ilike"]:
                        value = "%" + value + "%"

                    column = getattr(cls, column_name)
                    operation = getattr(
                        column, RESERVED_OPERATORS[operator])(value)
                    where.append(operation)
        return where

    def _order_by(self, cls: Type[DeclarativeBase],
                  **kwargs) -> Union[asc, desc, None]:
        """
        Builds SQLAlchemy ordering conditions based on keyword arguments
        to be used in a query.
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
