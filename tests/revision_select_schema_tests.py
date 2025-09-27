import unittest
from pydantic import ValidationError
from app.schemas.revision_select import (
    RevisionSelectResponse, UserSelectResponse)


class RevisionSelectSchemaTest(unittest.TestCase):

    def _user_stub(self):
        return UserSelectResponse.model_construct(id=123)

    def test_response_correct(self):
        res = RevisionSelectResponse(
            id=42,
            user=self._user_stub(),
            document_id=37,
            created_date=100,
            revision_number=1,
            uuid="8e8fc24abf80",
            filesize=123,
            checksum="3f6cdcb77bbd",
        )
        self.assertEqual(res.id, 42)
        self.assertEqual(res.user, self._user_stub())
        self.assertEqual(res.document_id, 37)
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.revision_number, 1)
        self.assertEqual(res.uuid, "8e8fc24abf80")
        self.assertEqual(res.filesize, 123)
        self.assertEqual(res.checksum, "3f6cdcb77bbd")

    def test_response_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=None,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id="not-int",
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_id_coercion(self):
        res = RevisionSelectResponse(
            id="42",
            user=self._user_stub(),
            document_id=37,
            created_date=100,
            revision_number=1,
            uuid="8e8fc24abf80",
            filesize=123,
            checksum="3f6cdcb77bbd",
        )
        self.assertEqual(res.id, 42)

    def test_response_document_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_document_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=None,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_document_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id="not-int",
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_document_id_coercion(self):
        res = RevisionSelectResponse(
            id=42,
            user=self._user_stub(),
            document_id="37",
            created_date=100,
            revision_number=1,
            uuid="8e8fc24abf80",
            filesize=123,
            checksum="3f6cdcb77bbd",
        )
        self.assertEqual(res.document_id, 37)

    def test_response_timestamp_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "missing")

    def test_response_timestamp_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=None,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_type")

    def test_response_timestamps_string(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date="not-int",
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_parsing")

    def test_response_timestamps_coercion(self):
        res = RevisionSelectResponse(
            id=42,
            user=self._user_stub(),
            document_id=37,
            created_date="100",
            revision_number=1,
            uuid="8e8fc24abf80",
            filesize=123,
            checksum="3f6cdcb77bbd",
        )
        self.assertEqual(res.created_date, 100)

    def test_response_revision_number_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("revision_number",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_revision_number_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=None,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("revision_number",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_revision_number_string(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number="not-int",
                uuid="8e8fc24abf80",
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("revision_number",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_revision_number_coercion(self):
        res = RevisionSelectResponse(
            id=42,
            user=self._user_stub(),
            document_id=37,
            created_date=100,
            revision_number="1",
            uuid="8e8fc24abf80",
            filesize=123,
            checksum="3f6cdcb77bbd",
        )
        self.assertEqual(res.revision_number, 1)

    def test_response_uuid_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("uuid",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_uuid_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid=None,
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("uuid",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_uuid_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid=12,
                filesize=123,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("uuid",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_filesize_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_filesize_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=None,
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_filesize_string(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize="not-int",
                checksum="3f6cdcb77bbd",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_filesize_coercion(self):
        res = RevisionSelectResponse(
            id=42,
            user=self._user_stub(),
            document_id=37,
            created_date=100,
            revision_number=1,
            uuid="8e8fc24abf80",
            filesize="123",
            checksum="3f6cdcb77bbd",
        )
        self.assertEqual(res.filesize, 123)

    def test_response_checksum_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("checksum",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_checksum_none(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("checksum",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_checksum_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            RevisionSelectResponse(
                id=42,
                user=self._user_stub(),
                document_id=37,
                created_date=100,
                revision_number=1,
                uuid="8e8fc24abf80",
                filesize=123,
                checksum=123,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("checksum",))
        self.assertEqual(e.get("type"), "string_type")
