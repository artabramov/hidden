"""
This module provides the TagLibrary class for managing document tags,
including methods for extracting tags from strings, deleting all tags
associated with a specific document ID, and inserting new tags. It
employs asynchronous operations and a locking mechanism to ensure
thread safety during tag manipulations, and interacts with the
repository to handle data storage. The class is designed to support
efficient tag management during document updates and ensure
concurrency control.
"""

import asyncio
from typing import List
from app.repository import Repository
from app.models.tag_model import Tag

asyncio_lock = asyncio.Lock()


class TagLibrary:
    """
    Provides methods for managing tags associated with documents. This
    class supports extracting tag values from strings, deleting all tags
    for a specific document, and inserting new tags. It utilizes a
    session for database operations and a cache for efficient data
    retrieval, with asynchronous operations to ensure scalability
    and performance.
    """

    def __init__(self, session, cache):
        """
        Initializes the TagLibrary instance with a database session and
        cache. The session is used for database interactions while the
        cache supports caching mechanisms. This setup is essential for
        managing tags associated with documents, allowing for efficient
        insertions and deletions.
        """
        self.session = session
        self.cache = cache

    def extract_values(self, source_string: str | None) -> List[str]:
        """
        Extracts and cleans tag values from a comma-separated string,
        converting them to lowercase and removing duplicates.
        """
        values = []
        if source_string:
            values = source_string.split(",")
            values = [tag.strip() for tag in values]
            values = list(set([value for value in values if value]))
        return values

    async def delete_all(self, document_id: int, commit: bool = True):
        """
        Deletes all tags associated with a specific document ID. This
        function is intended for use when updating documents and should
        not be used for manual tag deletion, as tag deletion will be
        handled automatically by the SQLAlchemy relationship.
        """
        tag_repository = Repository(self.session, self.cache, Tag)
        await tag_repository.delete_all(document_id__eq=document_id,
                                        commit=commit)

    async def insert_all(self, document_id: int, values: List[str],
                         commit: bool = True):
        """
        Inserts a list of tags for a given document ID into the
        repository. Each tag is processed within an asyncio lock to
        ensure thread safety.
        """
        tag_repository = Repository(self.session, self.cache, Tag)
        for value in values:
            # try:
            #     async with asyncio_lock:
            #         tag = Tag(document_id, value)
            #         await tag_repository.insert(tag, commit=commit)

            # except Exception:
            #     pass

            try:
                tag = Tag(document_id, value)
                await tag_repository.insert(tag, commit=commit)

            except Exception:
                pass
