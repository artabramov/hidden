# tests/validators/test_validation_errors.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from app.validators import validation_errors as ve


class TestValidationErrorConstants(unittest.TestCase):
    """Shared 422 tuples must stay (error_type, message) pairs."""

    def _assert_pair(self, name: str, pair: tuple[str, str]) -> None:
        self.assertEqual(len(pair), 2, msg=f"{name} must be a 2-tuple")
        err_type, message = pair
        self.assertIsInstance(err_type, str)
        self.assertTrue(err_type, msg=f"{name}: error_type non-empty")
        self.assertIsInstance(message, str)
        self.assertTrue(message.strip(), msg=f"{name}: message non-empty")

    def test_all_exported_pairs_are_well_formed(self):
        pairs = [
            ("VALUE_MISSING_UPPERCASE", ve.VALUE_MISSING_UPPERCASE),
            ("VALUE_MISSING_LOWERCASE", ve.VALUE_MISSING_LOWERCASE),
            ("VALUE_MISSING_DIGIT", ve.VALUE_MISSING_DIGIT),
            ("VALUE_TOO_COMMON", ve.VALUE_TOO_COMMON),
            ("VALUE_NOT_LATIN_EXTENDED", ve.VALUE_NOT_LATIN_EXTENDED),
            (
                "VALUE_NOT_ALPHANUMERIC_EXTENDED",
                ve.VALUE_NOT_ALPHANUMERIC_EXTENDED,
            ),
            ("VALUE_NOT_PATH_SEGMENT", ve.VALUE_NOT_PATH_SEGMENT),
        ]
        for name, pair in pairs:
            with self.subTest(name=name):
                self._assert_pair(name, pair)

    def test_error_types_are_unique(self):
        types_seen: set[str] = set()
        for _name, pair in [
            ("u", ve.VALUE_MISSING_UPPERCASE),
            ("l", ve.VALUE_MISSING_LOWERCASE),
            ("d", ve.VALUE_MISSING_DIGIT),
            ("c", ve.VALUE_TOO_COMMON),
            ("latin", ve.VALUE_NOT_LATIN_EXTENDED),
            ("alnum", ve.VALUE_NOT_ALPHANUMERIC_EXTENDED),
            ("path", ve.VALUE_NOT_PATH_SEGMENT),
        ]:
            err_type = pair[0]
            self.assertNotIn(
                err_type,
                types_seen,
                msg=f"duplicate error_type: {err_type}",
            )
            types_seen.add(err_type)
