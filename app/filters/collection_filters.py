"""
The module provides functions for filtering collection attributes, such
as collection name and collection summary. These filters are used within
Pydantic schemas.
"""

from typing import Union


def filter_collection_name(collection_name: str = None) -> Union[str, None]:
    """
    Filters a collection name by stripping leading and trailing
    whitespace. If the input is empty, it returns none. Otherwise, it
    returns the trimmed collection name.
    """
    return collection_name.strip() if collection_name else None


def filter_collection_summary(collection_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Filters a collection summary. If there is no input, or if the input
    is an empty string or consists only of whitespace, it returns none.
    Otherwise, it returns the trimmed user signature.
    """
    if collection_summary:
        return collection_summary.strip() or None
    return None
