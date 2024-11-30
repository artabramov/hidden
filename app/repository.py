"""
The module defines the Repository class, which provides a unified
interface for managing CRUD operations and caching for SQLAlchemy
models, using an async session for database interactions and Redis
for caching. It includes methods for checking existence, inserting,
selecting, updating, deleting, counting, and summing models, along
with transaction management through commit and rollback.
"""

from typing import List, Type, Union
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.managers.entity_manager import EntityManager, ID
from app.managers.cache_manager import CacheManager


class Repository:
    """
    A repository class for managing CRUD operations and caching for
    SQLAlchemy models.
    """

    def __init__(self, session: AsyncSession, cache: Redis,
                 entity_class: Type[DeclarativeBase]):
        """
        Initializes the repository with an async session, Redis cache,
        and the SQLAlchemy model class to manage.
        """
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.entity_class = entity_class

    async def exists(self, **kwargs) -> bool:
        """
        Checks if a SQLAlchemy model matching the given criteria exists
        in the database.
        """
        return await self.entity_manager.exists(self.entity_class, **kwargs)

    async def insert(self, entity: DeclarativeBase, commit: bool = True):
        """
        Inserts a new SQLAlchemy model into the database, with optional
        immediate transaction commit.
        """
        await self.entity_manager.insert(entity, commit=commit)

    async def select(self, **kwargs) -> Union[DeclarativeBase, None]:
        """
        Retrieves a SQLAlchemy model based on the provided criteria
        or ID, using cache if available.
        """
        entity_id, entity = kwargs.get(ID), None

        if self.entity_class._cacheable and entity_id is not None:
            entity = await self.cache_manager.get(self.entity_class, entity_id)

        if not entity and entity_id is not None:
            entity = await self.entity_manager.select(
                self.entity_class, entity_id)

        elif not entity and kwargs:
            entity = await self.entity_manager.select_by(
                self.entity_class, **kwargs)

        if self.entity_class._cacheable and entity:
            await self.cache_manager.set(entity)

        return entity

    async def select_all(self, **kwargs) -> List[DeclarativeBase]:
        """
        Retrieves all SQLAlchemy models that match the given criteria,
        with optional caching.
        """
        entities = await self.entity_manager.select_all(
            self.entity_class, **kwargs)

        if self.entity_class._cacheable:
            for entity in entities:
                await self.cache_manager.set(entity)

        return entities

    async def update(self, entity: DeclarativeBase, commit: bool = True):
        """
        Updates an existing SQLAlchemy model in the database, with
        optional immediate transaction commit.
        """
        await self.entity_manager.update(entity, commit=commit)

        if self.entity_class._cacheable:
            await self.cache_manager.delete(entity)

    async def delete(self, entity: DeclarativeBase, commit: bool = True):
        """
        Deletes a SQLAlchemy model from the database, with optional
        immediate transaction commit.
        """
        await self.entity_manager.delete(entity, commit=commit)

        if self.entity_class._cacheable:
            await self.cache_manager.delete(entity)

    async def delete_all(self, commit: bool = False, **kwargs):

        await self.entity_manager.delete_all(
            self.entity_class, commit=commit, **kwargs)

        if self.entity_class._cacheable:
            await self.cache_manager.delete_all(self.entity_class)

    async def delete_all_from_cache(self):
        if self.entity_class._cacheable:
            await self.cache_manager.delete_all(self.entity_class)

    async def count_all(self, **kwargs) -> int:
        """
        Counts the number of SQLAlchemy models that match the given
        criteria.
        """
        return await self.entity_manager.count_all(self.entity_class, **kwargs)

    async def sum_all(self, column_name: str, **kwargs) -> int:
        """
        Calculates the sum of a specific column for all SQLAlchemy
        models matching the criteria.
        """
        return await self.entity_manager.sum_all(
            self.entity_class, column_name, **kwargs)

    async def commit(self):
        """
        Commits the current transaction to the database.
        """
        await self.entity_manager.commit()

    async def rollback(self):
        """
        Rolls back the current transaction in case of issues.
        """
        await self.entity_manager.rollback()
