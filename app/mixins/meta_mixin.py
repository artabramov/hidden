"""
The module defines a mixin class for SQLAlchemy models that provides
utility methods for interacting with related metadata entries stored
in separate meta tables.
"""

from functools import reduce
from typing import Union
from sqlalchemy.orm import DeclarativeBase

META_LAST_LOGIN_DATE = "last_login_date"
META_UPDATES_COUNT = "updates_count"
META_DOWNLOADS_COUNT = "downloads_count"


class MetaMixin:
    """
    Mixin class for adding to SQLAlchemy model classes that store extra
    data in *_meta tables. The class provides methods for working with
    metadata, such as getting and setting values, changing values that
    represent integers. The metadata class should not be related to any
    classes other than the parent SQLAlchemy model.
    """

    @property
    def meta_relationship(self) -> str:
        """
        Returns the name of the relationship attribute on the parent
        model that links to the metadata entries.
        """
        relationships = self._meta.__mapper__.relationships
        return list(relationships._data.values())[0].back_populates

    def get_meta(self, meta_key: str) -> Union[DeclarativeBase, None]:
        """
        Retrieves the metadata object associated with the given metadata
        key, or returns None if not found.
        """
        return reduce(lambda x, y: y if y.meta_key == meta_key else x,
                      getattr(self, self.meta_relationship), None)

    def set_meta(self, meta_key: str, meta_value: str):
        """
        Sets or updates the metadata value for the given key by either
        modifying an existing entry or appending a new one.
        """
        meta = self.get_meta(meta_key)
        if not meta:
            meta = self._meta(self.id, meta_key, meta_value)
            getattr(self, self.meta_relationship).append(meta)
        else:
            meta.meta_value = meta_value
