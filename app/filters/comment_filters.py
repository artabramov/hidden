"""
The module provides functions for filtering comment attributes,
such as comment content. The validator is used within Pydantic schemas.
"""


def filter_comment_content(comment_content: str) -> str:
    """
    Filters a comment content by stripping leading and trailing
    whitespace. If the input is empty, it returns none. Otherwise, it
    returns the trimmed comment content.
    """
    return comment_content.strip() if comment_content else None
