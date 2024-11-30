"""
The module defines the EntityManager class for managing database
operations with SQLAlchemy model classes using an asynchronous
SQLAlchemy session. It provides methods for performing CRUD operations,
querying entities with various filters, counting records, aggregating
data, and handling transactions. The EntityManager class supports
operations such as inserting, updating, deleting, and selecting
SQLAlchemy model instances, as well as summing column values and
locking tables to prevent modifications. The class is designed to
work efficiently with large datasets and integrates with SQLAlchemy's
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
    The class is designed to handle entities that are instances of
    SQLAlchemy models.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the EntityManager with a session instance."""
        self.session = session

    @timed
    async def exists(self, cls: Type[DeclarativeBase], **kwargs) -> bool:
        """
        Check if an entity of the specified SQLAlchemy model class
        exists in the database based on the provided filters by
        constructing a query that checks for at least one matching
        entity. The method returns True if a matching entity is
        found, and False otherwise.
        """
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none() is not None

    @timed
    async def insert(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = True):
        """
        Insert a new SQLAlchemy model instance into the database
        by adding the given entity to the session and saving it.
        The "flush" parameter determines whether to immediately
        send changes to the database, while the "commit" parameter
        specifies whether to finalize the transaction and persist
        changes.
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
        Retrieve a SQLAlchemy model instance of the specified class by
        its ID, constructing a query to find the entity with the given
        ID. The method returns the instance if found, or None if no
        matching entity exists.
        """
        async_result = await self.session.execute(
            select(cls).where(cls.id == obj_id).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_by(self, cls: Type[DeclarativeBase],
                        **kwargs) -> Union[DeclarativeBase, None]:
        """
        Retrieve a SQLAlchemy model instance based on the provided
        filters by constructing a query to find a single entity that
        matches the criteria. The method returns the entity if found,
        or None if no matching entity exists.
        """
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_all(self, cls: Type[DeclarativeBase],
                         **kwargs) -> List[DeclarativeBase]:
        """
        Retrieve all SQLAlchemy model instances of the specified class
        that match the provided filters by constructing a query with
        optional ordering, pagination, and limiting. If a subquery is
        included in the filters, the results will only include entities
        whose IDs are present in that subquery. The method returns a
        list of matching entities.
        """
        query = select(cls) \
            .where(*self._where(cls, **kwargs)) \
            .order_by(self._order_by(cls, **kwargs)) \
            .offset(self._offset(**kwargs)) \
            .limit(self._limit(**kwargs)) \

        if SUBQUERY in kwargs:
            query = query.filter(cls.id.in_(kwargs[SUBQUERY]))

        async_result = await self.session.execute(query)
        data = async_result.unique().scalars().all()
        return data

    @timed
    async def select_rows(self, sql: str) -> list:
        """
        Asynchronously execute the provided SQL query and return all
        result rows as a list. This method allows for direct execution
        of raw SQL statements within the session.
        """
        async_result = await self.session.execute(text(sql))
        return async_result.fetchall()

    @timed
    async def update(self, obj: DeclarativeBase, flush: bool = True,
                     commit: bool = False):
        """
        Update an existing SQLAlchemy model instance in the database by
        merging the changes of the given entity with the session. The
        "flush" parameter determines whether to immediately send changes
        to the database, while the "commit" parameter specifies whether
        to finalize the transaction and persist changes.
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
        Delete a SQLAlchemy model instance from the database by removing
        the specified entity from the session. This marks the object for
        deletion, and changes will not be persisted until the session is
        flushed or committed. The "flush" parameter determines whether
        to immediately send changes to the database, while the "commit"
        parameter indicates whether to finalize the deletion in the
        database.
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
        Delete all SQLAlchemy model instances of the specified class
        that match the provided filters by constructing a query for
        deletion and handling large datasets in batches. The "flush"
        parameter determines whether to immediately send changes to
        the database, while the "commit" parameter indicates whether
        to finalize the deletions in the database. The method
        processes deletions in batches.
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
        Count the number of SQLAlchemy model instances of the specified
        class that match the provided filters by constructing a query
        to count all entities meeting the criteria. If a subquery is
        included, it counts only those entities whose IDs are present
        in that subquery.
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
        Sum the values of a specified column for all SQLAlchemy model
        instances matching the filters. Constructs a query to calculate
        the sum of the values in the specified column for entities
        meeting the criteria. If a subquery is provided, it sums only
        those values for entities whose IDs are present in the subquery.
        """
        query = select(func.sum(getattr(cls, column_name))).where(
            *self._where(cls, **kwargs))

        if SUBQUERY in kwargs:
            query = query.filter(cls.id.in_(kwargs[SUBQUERY]))

        async_result = await self.session.execute(query)
        return async_result.unique().scalars().one_or_none() or 0

    @timed
    async def subquery(self, cls: Type[DeclarativeBase],
                       foreign_key: str, **kwargs) -> select:
        """
        Constructs and returns a subquery for the given SQLAlchemy model
        class, selecting the values of the specified foreign key column
        and applying the provided filters. This method builds a subquery
        object that can be used to filter other queries based on the
        foreign key column values of entities that match the specified
        criteria.
        """
        subquery = select(getattr(cls, foreign_key)).filter(
            *self._where(cls, **kwargs)).subquery()
        return subquery

    @timed
    async def flush(self):
        """
        Flush the session to synchronize with the database. Sends all
        pending changes in the session to the database but does not
        commit the transaction.
        """
        await self.session.flush()

    @timed
    async def commit(self):
        """
        Commit the current transaction. Commits all changes made during
        the current transaction, making them permanent in the database.
        """
        await self.session.commit()

    @timed
    async def rollback(self):
        """
        Roll back the current transaction. Reverts all changes made
        during the current transaction, undoing any modifications to
        maintain consistency.
        """
        await self.session.rollback()

    def _where(self, cls: Type[DeclarativeBase], **kwargs) -> list:
        """
        Construct a WHERE clause from the provided filter criteria for
        SQLAlchemy queries. Builds SQLAlchemy filter conditions based on
        keyword arguments to be used in a query's WHERE clause.
        """
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in RESERVED_KEYS}:
            column_name, operator = key.split("__")

            if hasattr(cls, column_name):
                value = kwargs[key]

                if value is not None:
                    if operator == "in":
                        value = [x.strip() for x in value.split(",")]

                    elif operator in ["like", "ilike"]:
                        value = "%" + value + "%"

                    else:
                        value = value

                    column = getattr(cls, column_name)
                    operation = getattr(
                        column, RESERVED_OPERATORS[operator])(value)
                    where.append(operation)
        return where

    def _order_by(self, cls: Type[DeclarativeBase],
                  **kwargs) -> Union[asc, desc, None]:
        """
        Construct an ORDER BY clause from the provided sorting criteria
        for SQLAlchemy queries. Builds SQLAlchemy ordering conditions
        based on keyword arguments to be used in a query's ORDER BY
        clause.
        """
        order_by = getattr(cls, kwargs.get(ORDER_BY))

        if kwargs.get(ORDER) == ASC:
            return asc(order_by)

        elif kwargs.get(ORDER) == DESC:
            return desc(order_by)

        elif kwargs.get(ORDER) == RAND:
            return func.random()

    def _offset(self, **kwargs) -> Optional[int]:
        """
        Get the offset value from the provided pagination settings for
        SQLAlchemy queries. Retrieves the starting point for pagination
        from the keyword arguments, indicating where the query results
        should start.
        """
        return kwargs.get(OFFSET)

    def _limit(self, **kwargs) -> Optional[int]:
        """
        Get the limit value from the provided pagination settings for
        SQLAlchemy queries. Retrieves the maximum number of results to
        return from the keyword arguments, capping the number of query
        results.
        """
        return kwargs.get(LIMIT)
