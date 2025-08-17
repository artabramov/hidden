import unittest
from app.models.user_model import User
from unittest.mock import patch
from app.config import get_config
from app.models.document_model import Document  # noqa F401
from app.models.tag_model import Tag  # noqa F401
from app.models.setting_model import Setting  # noqa F401

cfg = get_config()


class UserModelTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.models.user_model.hash_str")
    @patch("app.models.user_model.get_index")
    @patch("app.models.user_model.decrypt_bool")
    @patch("app.models.user_model.decrypt_int")
    @patch("app.models.user_model.decrypt_str")
    @patch("app.models.user_model.encrypt_bool")
    @patch("app.models.user_model.encrypt_int")
    @patch("app.models.user_model.encrypt_str")
    async def test_init_to_dict(
            self, encrypt_str_mock, encrypt_int_mock, encrypt_bool_mock,
            decrypt_str_mock, decrypt_int_mock, decrypt_bool_mock,
            get_index_mock, hash_str_mock):
        encrypt_str_mock.side_effect = [
            "username_encrypted",
            "first_name_encrypted",
            "last_name_encrypted",
            "user_role_encrypted",
            "mfa_secret_encrypted",
            "jti_encrypted",
            None,
            None
        ]
        encrypt_int_mock.side_effect = [
            "password_attempts_encrypted",
            "mfa_attempts_encrypted"
        ]
        encrypt_bool_mock.side_effect = [
            "password_accepted_encrypted",
            "is_active_encrypted"
        ]
        decrypt_str_mock.side_effect = [
            "username",
            "first_name",
            "last_name",
            "user_role",
            None,
            None]
        decrypt_int_mock.side_effect = [
            "created_date"
        ]
        decrypt_bool_mock.side_effect = [
            "is_active"
        ]

        get_index_mock.side_effect = [
            "username_index", "first_name_index", "last_name_index"
        ]
        hash_str_mock.side_effect = ["username_hash", "password_hash"]

        user = User("johndoe", "password", "John", "Doe")

        self.assertIsNone(user.id)
        self.assertIsNone(user.created_date_encrypted)
        self.assertIsNone(user.updated_date_encrypted)
        self.assertIsNone(user.suspended_date_encrypted)
        self.assertEqual(user.username_encrypted, "username_encrypted")
        self.assertEqual(user.username_hash, "username_hash")
        self.assertEqual(user.username_index, "username_index")
        self.assertEqual(user.password_attempts_encrypted,
                         "password_attempts_encrypted")
        self.assertEqual(user.password_accepted_encrypted,
                         "password_accepted_encrypted")
        self.assertEqual(user.first_name_encrypted, "first_name_encrypted")
        self.assertEqual(user.first_name_index, "first_name_index")
        self.assertEqual(user.last_name_encrypted, "last_name_encrypted")
        self.assertEqual(user.last_name_index, "last_name_index")
        self.assertEqual(user.user_role_encrypted, "user_role_encrypted")
        self.assertEqual(user.is_active_encrypted, "is_active_encrypted")
        self.assertEqual(user.mfa_secret_encrypted, "mfa_secret_encrypted")
        self.assertEqual(user.mfa_attempts_encrypted, "mfa_attempts_encrypted")
        self.assertEqual(user.jti_encrypted, "jti_encrypted")
        self.assertEqual(user.user_summary_encrypted, None)
        self.assertEqual(user.userpic_filename_encrypted, None)

        user_to_dict = await user.to_dict()
        self.assertDictEqual(user_to_dict, {
            "id": None,
            "created_date": "created_date",
            "username": "username",
            "first_name": "first_name",
            "last_name": "last_name",
            "user_role": "user_role",
            "is_active": "is_active",
            "user_summary": None,
            "userpic_filename": None,
            "user_meta": {},
        })

    @patch("app.helpers.encrypt_helper.ctx")
    def test_role_reader(self, ctx_mock):
        ctx_mock.secret_key = "secret"
        user = User("johndoe", "password", "John", "Doe", user_role="reader")
        self.assertTrue(user.can_read)
        self.assertFalse(user.can_write)
        self.assertFalse(user.can_edit)
        self.assertFalse(user.can_admin)

    @patch("app.helpers.encrypt_helper.ctx")
    def test_role_writer(self, ctx_mock):
        ctx_mock.secret_key = "secret"
        user = User("johndoe", "password", "John", "Doe", user_role="writer")
        self.assertTrue(user.can_read)
        self.assertTrue(user.can_write)
        self.assertFalse(user.can_edit)
        self.assertFalse(user.can_admin)

    @patch("app.helpers.encrypt_helper.ctx")
    def test_role_editor(self, ctx_mock):
        ctx_mock.secret_key = "secret"
        user = User("johndoe", "password", "John", "Doe", user_role="editor")
        self.assertTrue(user.can_read)
        self.assertTrue(user.can_write)
        self.assertTrue(user.can_edit)
        self.assertFalse(user.can_admin)

    @patch("app.helpers.encrypt_helper.ctx")
    def test_role_admin(self, ctx_mock):
        ctx_mock.secret_key = "secret"
        user = User("johndoe", "password", "John", "Doe", user_role="admin")
        self.assertTrue(user.can_read)
        self.assertTrue(user.can_write)
        self.assertTrue(user.can_edit)
        self.assertTrue(user.can_admin)


if __name__ == "__main__":
    unittest.main()
