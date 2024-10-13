from typing import Union


def validate_document_name(document_name: str) -> str:
    """
    Validates and normalizes a document name by stripping leading and
    trailing whitespace.
    """
    return document_name.strip() if document_name else None


def validate_document_summary(document_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strips leading and trailing whitespace from the document summary
    if it provided.
    """
    return document_summary.strip() if document_summary else None


def validate_tags(tags: str = None) -> Union[str, None]:
    return tags.strip().lower() if tags else None
