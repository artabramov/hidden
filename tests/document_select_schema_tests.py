import unittest
from pydantic import ValidationError
from app.schemas.file_select import (
    FileSelectResponse, UserSelectResponse, FolderSelectResponse,
    RevisionSelectResponse)


class FileSelectSchemaTest(unittest.TestCase):

    def _user_stub(self):
        return UserSelectResponse.model_construct(id=123)

    def _folder_stub(self):
        return FolderSelectResponse.model_construct(id=123)

    def _revision_stub(self):
        return RevisionSelectResponse.model_construct(id=123)

    def test_response_correct(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.id, 42)
        self.assertEqual(res.user, self._user_stub())
        self.assertEqual(res.folder, self._folder_stub())
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.updated_date, 200)
        self.assertEqual(res.flagged, True)
        self.assertEqual(res.filename, "X")
        self.assertEqual(res.filesize, 123)
        self.assertEqual(res.mimetype, "image/jpeg")
        self.assertEqual(res.checksum, "3f6cdcb77bbd")
        self.assertIsNone(res.summary)
        self.assertEqual(res.latest_revision_number, 1)
        self.assertEqual(res.file_revisions, [self._revision_stub()])

    def test_response_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=None,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id="not-int",
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_id_coercion(self):
        res = FileSelectResponse(
            id="42",
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.id, 42)

    def test_response_timestamps_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "missing")

        self.assertEqual(errs[1].get("loc"), ("updated_date",))
        self.assertEqual(errs[1].get("type"), "missing")

    def test_response_timestamps_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=None,
                updated_date=None,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_type")

        self.assertEqual(errs[1].get("loc"), ("updated_date",))
        self.assertEqual(errs[1].get("type"), "int_type")

    def test_response_timestamps_string(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date="not-int",
                updated_date="not-int",
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_parsing")

        self.assertEqual(errs[1].get("loc"), ("updated_date",))
        self.assertEqual(errs[1].get("type"), "int_parsing")

    def test_response_timestamps_coercion(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date="100",
            updated_date="200",
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.updated_date, 200)

    def test_response_flagged_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_flagged_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=None,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged",))
        self.assertEqual(e.get("type"), "bool_type")

    def test_response_flagged_string(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged="not-int",
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_flagged_coercion(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=1,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.flagged, True)

    def test_response_filename_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_filename_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename=None,
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_filename_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename=123,
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_filesize_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_filesize_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=None,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_filesize_string(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize="not-int",
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_filesize_coercion(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize="123",
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.filesize, 123)

    def test_response_mimetype_missing(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertIsNone(res.mimetype)

    def test_response_mimetype_none(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype=None,
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertIsNone(res.mimetype)

    def test_response_mimetype_string(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.mimetype, "image/jpeg")

    def test_response_mimetype_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype=37,
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("mimetype",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_checksum_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("checksum",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_checksum_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum=None,
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("checksum",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_checksum_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum=123,
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("checksum",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_summary_missing(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertIsNone(res.summary)

    def test_response_summary_none(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary=None,
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertIsNone(res.summary)

    def test_response_summary_string(self):
        res = FileSelectResponse(
            id=42,
            user=self._user_stub(),
            folder=self._folder_stub(),
            created_date=100,
            updated_date=200,
            flagged=True,
            filename="X",
            filesize=123,
            mimetype="image/jpeg",
            checksum="3f6cdcb77bbd",
            summary="Some text",
            latest_revision_number=1,
            file_revisions=[self._revision_stub()]
        )
        self.assertEqual(res.summary, "Some text")

    def test_response_summary_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=123,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_user_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=None,
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user",))
        self.assertEqual(e.get("type"), "model_type")

    def test_response_folder_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_folder_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=None,
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=[self._revision_stub()]
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder",))
        self.assertEqual(e.get("type"), "model_type")

    def test_response_revisions_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("file_revisions",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_revisions_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileSelectResponse(
                id=42,
                user=self._user_stub(),
                folder=self._folder_stub(),
                created_date=100,
                updated_date=200,
                flagged=True,
                filename="X",
                filesize=123,
                mimetype="image/jpeg",
                checksum="3f6cdcb77bbd",
                summary=None,
                latest_revision_number=1,
                file_revisions=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("file_revisions",))
        self.assertEqual(e.get("type"), "list_type")
