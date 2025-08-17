from typing import Union
import unicodedata

INDEX_LENGTH = 6
WEIGHT_FACTOR = 40
COARSE_SHIFT = 17

# Pre-calculated position weights
_WEIGHTS = tuple(WEIGHT_FACTOR ** i for i in range(
    INDEX_LENGTH - 1, -1, -1))

# Precomputed quantization divisor (without bit shifts)
QUANT_DIVISOR = 2 ** COARSE_SHIFT

# Unicode normalization form used during canonicalization
NORMALIZATION_FORM = "NFC"


def _canonicalize(value: str) -> str:
    """
    Perform case-insensitive canonicalization of a string: apply
    aggressive locale-independent lowercasing, normalize to a canonical
    single form.
    """
    return unicodedata.normalize(NORMALIZATION_FORM, value.casefold())


def get_index(value: Union[str, int]) -> int:
    """
    Compute a quantized sorting index for ORDER BY.

  Goal:
  - Allow DB-side ORDER BY without decrypting values.
  - Leak as little as possible about the plaintext.

  Approach:
  - Take the first N Unicode code points after case-insensitive
    canonicalization (casefold + NORMALIZATION_FORM). We sort by code
    point order, not by locale/collation.
  - Compute a positional integer index with WEIGHT_FACTOR so earlier
    code points dominate later ones.
  - Quantize the result by dropping COARSE_SHIFT least significant bits.
    This keeps the mapping monotonic (DB can still ORDER BY a single
    column) but makes the index many-to-one, which reduces
    reconstructability of the prefix.
    """
    if isinstance(value, int):
        value = str(value)

    s = _canonicalize(value)

    idx = 0
    for pos, ch in enumerate(s[:INDEX_LENGTH]):
        idx += ord(ch) * _WEIGHTS[pos]

    return idx // QUANT_DIVISOR
