"""
The module provides functions for filtering document attributes such as
filename, summary, and tags. These filters are used to ensure the input
data is cleaned (trimmed and standardized) before being processed
further.
"""

from typing import Union


def filter_document_filename(document_filename: str) -> str:
    """
    Filters a document name by stripping leading and trailing whitespace.
    """
    return document_filename.strip() if document_filename else None


def filter_document_summary(document_summary: str = None) -> Union[str, None]:
    """
    Filters a document summary. If the input is empty or consists only
    of whitespace, it returns None. Otherwise, it returns the trimmed
    document summary.
    """
    if document_summary:
        return document_summary.strip() or None
    return None


def filter_tags(tags: str = None) -> Union[str, None]:
    """
    Filters tags by stripping leading and trailing whitespace and
    converting them to lowercase. If the input is empty, it returns None.
    """
    return tags.strip().lower() if tags else None
