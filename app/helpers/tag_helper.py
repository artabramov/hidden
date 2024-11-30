"""
The module provides functionality for extracting and cleaning tag values
from a comma-separated string. It converts the values to lowercase and
removes duplicates.
"""

from typing import List


def extract_tag_values(source_string: str = None) -> List[str]:
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
