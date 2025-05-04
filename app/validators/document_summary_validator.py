"""
The module defines validator for a document summary.
"""


def document_summary_validate(document_summary: str):
    """Returns None if the summary doen't contain any symbols."""
    if document_summary:
        return document_summary.strip() or None
