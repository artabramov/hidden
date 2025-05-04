"""
The module defines validator for user summary.
"""


def user_summary_validate(user_summary: str):
    """Returns None if the summary doen't contain any symbols."""
    if user_summary:
        return user_summary.strip() or None
