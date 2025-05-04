"""
The module defines validator for a collection summary.
"""


def collection_summary_validate(collection_summary: str):
    """Returns None if the summary doen't contain any symbols."""
    if collection_summary:
        return collection_summary.strip() or None
