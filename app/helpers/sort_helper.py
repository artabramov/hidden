"""
The module provides function for creating a sorting index of encrypted
data.
"""

from typing import Union

# Only consider the first INDEX_LENGTH characters
INDEX_LENGTH = 8

# Weight the character by a larger factor
WEIGHT_FACTOR = 40


def get_index(value: Union[str, int]) -> int:
    """
    Calculates a sorting index for a given string based on the first
    characters, weighting each character by its Unicode code point and
    a factor determined by its position in the string. The weight of
    each character is determined by raising weight factor to the power
    of its position index.
    """
    if isinstance(value, int):
        value = str(value)

    i = INDEX_LENGTH - 1
    sorting_index = 0

    for symbol in value[:INDEX_LENGTH]:
        symbol_code = ord(symbol)
        symbol_weight = symbol_code * (WEIGHT_FACTOR ** i)
        sorting_index += symbol_weight
        i -= 1

    return sorting_index
