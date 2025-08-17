"""
The module defines validator for a tag value.
"""


def tag_value_validate(tag_value: str):
    """Converts all letters to lower case."""
    if tag_value:
        tag_value = tag_value.strip()

    if tag_value:
        return tag_value.lower()
