import unittest
from app.validators.user_summary_validator import user_summary_validate


class UserSummaryValidatorTest(unittest.TestCase):

    def test_user_summary_validator_none(self):
        user_summary = user_summary_validate(None)
        self.assertIsNone(user_summary)

    def test_user_summary_validator_empty(self):
        user_summary = user_summary_validate("")
        self.assertIsNone(user_summary)

    def test_user_summary_validator_whitespaces(self):
        user_summary = user_summary_validate(" ")
        self.assertIsNone(user_summary)

    def test_user_summary_validator_str(self):
        user_summary = user_summary_validate(" Text ")
        self.assertEqual(user_summary, "Text")


if __name__ == "__main__":
    unittest.main()
