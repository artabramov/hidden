# tests/schemas/test_file_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace

from pydantic import ValidationError

from app.models.file import FileType
from app.schemas.file_list import (
    FileListItemResponse,
    FileListRequest,
    FileListResponse,
    build_file_list_item_response,
)


class TestFileListRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = FileListRequest(
            folder_id__eq=1,
            created_at__ge=100,
            created_at__le=200,
            updated_at__ge=300,
            updated_at__le=400,
            is_starred__eq=True,
            filename__ilike="document",
            mimetype__ilike="text",
            offset=10,
            limit=20,
            order_by="filename",
            order="desc",
        )

        self.assertEqual(req.created_at__ge, 100)
        self.assertEqual(req.created_at__le, 200)
        self.assertEqual(req.updated_at__ge, 300)
        self.assertEqual(req.updated_at__le, 400)
        self.assertTrue(req.is_starred__eq)
        self.assertEqual(req.filename__ilike, "document")
        self.assertEqual(req.mimetype__ilike, "text")
        self.assertEqual(req.offset, 10)
        self.assertEqual(req.limit, 20)
        self.assertEqual(req.order_by, "filename")
        self.assertEqual(req.order, "desc")
        self.assertEqual(req.folder_id__eq, 1)

    def test_uses_defaults(self):
        req = FileListRequest()

        self.assertIsNone(req.folder_id__eq)
        self.assertIsNone(req.created_at__ge)
        self.assertIsNone(req.created_at__le)
        self.assertIsNone(req.updated_at__ge)
        self.assertIsNone(req.updated_at__le)
        self.assertIsNone(req.is_starred__eq)
        self.assertIsNone(req.filename__ilike)
        self.assertIsNone(req.mimetype__ilike)
        self.assertEqual(req.offset, 0)
        self.assertEqual(req.limit, 50)
        self.assertEqual(req.order_by, "filename")
        self.assertEqual(req.order, "asc")

    def test_strips_string_fields(self):
        req = FileListRequest(
            filename__ilike="  document  ",
            mimetype__ilike="  text/plain  ",
        )

        self.assertEqual(req.filename__ilike, "document")
        self.assertEqual(req.mimetype__ilike, "text/plain")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileListRequest(other=1)

    def test_folder_id_eq_explicit_none(self):
        req = FileListRequest(folder_id__eq=None)

        self.assertIsNone(req.folder_id__eq)

    def test_folder_id_eq_rejects_non_positive_value(self):
        with self.assertRaises(ValidationError) as cm:
            FileListRequest(folder_id__eq=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folder_id__eq",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_order_by_accepts_all_allowed_values(self):
        values = [
            "id",
            "created_at",
            "updated_at",
            "is_starred",
            "filename",
            "filesize",
            "mimetype",
            "comments_count",
            "latest_revision_number",
        ]

        for value in values:
            req = FileListRequest(order_by=value)
            self.assertEqual(req.order_by, value)

    def test_order_by_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            FileListRequest(order_by="name")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("order_by",))
        self.assertEqual(error["type"], "literal_error")

    def test_order_accepts_rand(self):
        req = FileListRequest(order="rand")

        self.assertEqual(req.order, "rand")

    def test_order_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            FileListRequest(order="random")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("order",))
        self.assertEqual(error["type"], "literal_error")

    def test_timestamp_filters_reject_negative_values(self):
        fields = [
            "created_at__ge",
            "created_at__le",
            "updated_at__ge",
            "updated_at__le",
        ]

        for field in fields:
            with self.assertRaises(ValidationError) as cm:
                FileListRequest(**{field: -1})

            error = cm.exception.errors()[0]
            self.assertEqual(error["loc"], (field,))
            self.assertEqual(error["type"], "greater_than_equal")

    def test_offset_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            FileListRequest(offset=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("offset",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_limit_rejects_zero(self):
        with self.assertRaises(ValidationError) as cm:
            FileListRequest(limit=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("limit",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_limit_rejects_value_above_maximum(self):
        with self.assertRaises(ValidationError) as cm:
            FileListRequest(limit=501)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("limit",))
        self.assertEqual(error["type"], "less_than_equal")


class TestFileListItemResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileListItemResponse(
            id=1,
            folder_id=2,
            created_by={
                "id": 3,
                "display_name": "Uploader",
            },
            created_at=100,
            updated_by={
                "id": 4,
                "display_name": "Updater",
            },
            updated_at=200,
            is_starred=True,
            filename="document.txt",
            filesize=1024,
            mimetype="text/plain",
            checksum="a" * 64,
            summary="File summary.",
            comments_count=1,
            latest_revision_number=2,
            file_tags=["docs", "text"],
            has_thumbnail=True,
            filetype=FileType.TEXT,
        )

        self.assertEqual(resp.file_id, 1)
        self.assertEqual(resp.folder_id, 2)
        self.assertEqual(resp.created_by.user_id, 3)
        self.assertEqual(resp.created_by.display_name, "Uploader")
        self.assertEqual(resp.updated_by.user_id, 4)
        self.assertEqual(resp.updated_by.display_name, "Updater")
        self.assertEqual(resp.created_at, 100)
        self.assertEqual(resp.updated_at, 200)
        self.assertTrue(resp.is_starred)
        self.assertEqual(resp.filename, "document.txt")
        self.assertEqual(resp.filesize, 1024)
        self.assertEqual(resp.mimetype, "text/plain")
        self.assertEqual(resp.checksum, "a" * 64)
        self.assertEqual(resp.summary, "File summary.")
        self.assertEqual(resp.comments_count, 1)
        self.assertEqual(resp.latest_revision_number, 2)
        self.assertEqual(resp.file_tags, ["docs", "text"])
        self.assertTrue(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.TEXT)

    def test_accepts_none_optional_fields(self):
        resp = FileListItemResponse(
            id=1,
            folder_id=2,
            created_by={
                "id": 3,
                "display_name": "Uploader",
            },
            created_at=100,
            updated_by=None,
            updated_at=None,
            is_starred=False,
            filename="document.txt",
            filesize=1024,
            mimetype=None,
            checksum="a" * 64,
            summary=None,
            comments_count=0,
            latest_revision_number=0,
            file_tags=[],
            has_thumbnail=False,
            filetype=FileType.BINARY,
        )

        self.assertIsNone(resp.updated_by)
        self.assertIsNone(resp.updated_at)
        self.assertIsNone(resp.mimetype)
        self.assertIsNone(resp.summary)
        self.assertFalse(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.BINARY)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileListItemResponse(
                id=1,
                folder_id=2,
                created_by={
                    "id": 3,
                    "display_name": "Uploader",
                },
                created_at=100,
                updated_by=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=1024,
                mimetype=None,
                checksum="a" * 64,
                summary=None,
                comments_count=0,
                latest_revision_number=0,
                file_tags=[],
                has_thumbnail=False,
                filetype=FileType.BINARY,
                other=1,
            )

    def test_required_fields(self):
        required_fields = [
            "id",
            "folder_id",
            "created_by",
            "created_at",
            "is_starred",
            "filename",
            "filesize",
            "checksum",
            "comments_count",
            "latest_revision_number",
            "file_tags",
            "has_thumbnail",
            "filetype",
        ]

        for field in required_fields:
            data = {
                "id": 1,
                "folder_id": 2,
                "created_by": {
                    "id": 3,
                    "display_name": "Uploader",
                },
                "created_at": 100,
                "updated_by": None,
                "updated_at": None,
                "is_starred": False,
                "filename": "document.txt",
                "filesize": 1024,
                "mimetype": None,
                "checksum": "a" * 64,
                "summary": None,
                "comments_count": 0,
                "latest_revision_number": 0,
                "file_tags": [],
                "has_thumbnail": False,
                "filetype": FileType.BINARY,
            }
            data.pop(field)

            with self.assertRaises(ValidationError) as cm:
                FileListItemResponse(**data)

            error = cm.exception.errors()[0]
            self.assertEqual(error["loc"], (field,))
            self.assertEqual(error["type"], "missing")

    def test_rejects_negative_filesize(self):
        with self.assertRaises(ValidationError) as cm:
            FileListItemResponse(
                id=1,
                folder_id=2,
                created_by={
                    "id": 3,
                    "display_name": "Uploader",
                },
                created_at=100,
                updated_by=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=-1,
                mimetype=None,
                checksum="a" * 64,
                summary=None,
                comments_count=0,
                latest_revision_number=0,
                file_tags=[],
                has_thumbnail=False,
                filetype=FileType.BINARY,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filesize",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_rejects_negative_comments_count(self):
        with self.assertRaises(ValidationError) as cm:
            FileListItemResponse(
                id=1,
                folder_id=2,
                created_by={
                    "id": 3,
                    "display_name": "Uploader",
                },
                created_at=100,
                updated_by=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=1024,
                mimetype=None,
                checksum="a" * 64,
                summary=None,
                comments_count=-1,
                latest_revision_number=0,
                file_tags=[],
                has_thumbnail=False,
                filetype=FileType.BINARY,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("comments_count",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_rejects_negative_latest_revision_number(self):
        with self.assertRaises(ValidationError) as cm:
            FileListItemResponse(
                id=1,
                folder_id=2,
                created_by={
                    "id": 3,
                    "display_name": "Uploader",
                },
                created_at=100,
                updated_by=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=1024,
                mimetype=None,
                checksum="a" * 64,
                summary=None,
                comments_count=0,
                latest_revision_number=-1,
                file_tags=[],
                has_thumbnail=False,
                filetype=FileType.BINARY,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("latest_revision_number",))
        self.assertEqual(error["type"], "greater_than_equal")


class TestFileListResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = FileListResponse(
            files=[
                {
                    "id": 1,
                    "folder_id": 2,
                    "created_by": {
                        "id": 3,
                        "display_name": "Uploader",
                    },
                    "created_at": 100,
                    "updated_by": None,
                    "updated_at": None,
                    "is_starred": False,
                    "filename": "document.txt",
                    "filesize": 1024,
                    "mimetype": None,
                    "checksum": "a" * 64,
                    "summary": None,
                    "comments_count": 0,
                    "latest_revision_number": 0,
                    "file_tags": [],
                    "has_thumbnail": False,
                    "filetype": FileType.BINARY,
                },
            ],
            files_count=1,
        )

        self.assertEqual(len(resp.files), 1)
        self.assertEqual(resp.files_count, 1)
        self.assertEqual(resp.files[0].file_id, 1)
        self.assertEqual(resp.files[0].created_by.user_id, 3)
        self.assertEqual(resp.files[0].filename, "document.txt")

    def test_accepts_empty_files(self):
        resp = FileListResponse(
            files=[],
            files_count=0,
        )

        self.assertEqual(resp.files, [])
        self.assertEqual(resp.files_count, 0)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileListResponse(
                files=[],
                files_count=0,
                other=1,
            )

    def test_files_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileListResponse(files_count=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("files",))
        self.assertEqual(error["type"], "missing")

    def test_files_count_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileListResponse(files=[])

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("files_count",))
        self.assertEqual(error["type"], "missing")

    def test_files_count_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            FileListResponse(
                files=[],
                files_count=-1,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("files_count",))
        self.assertEqual(error["type"], "greater_than_equal")


class TestBuildFileListItemResponse(unittest.TestCase):

    def test_builds_response(self):
        class FileObj:

            def __init__(self):
                self.id = 1
                self.folder_id = 2
                self.created_at = 100
                self.updated_at = 200
                self.is_starred = True
                self.filename = "document.txt"
                self.filesize = 1024
                self.mimetype = "text/plain"
                self.checksum = "a" * 64
                self.summary = "File summary."
                self.comments_count = 1
                self.latest_revision_number = 2
                self.file_created_by_user = SimpleNamespace(
                    id=3,
                    display_name="Uploader",
                )
                self.file_updated_by_user = SimpleNamespace(
                    id=4,
                    display_name="Updater",
                )
                self.file_tags = [
                    SimpleNamespace(tag="docs"),
                    SimpleNamespace(tag="text"),
                ]
                self.file_thumbnail = SimpleNamespace(id=10)

            @property
            def has_thumbnail(self):
                return self.file_thumbnail is not None

            @property
            def filetype(self):
                return FileType.TEXT

        resp = build_file_list_item_response(FileObj())

        self.assertIsInstance(resp, FileListItemResponse)
        self.assertEqual(resp.file_id, 1)
        self.assertEqual(resp.created_by.user_id, 3)
        self.assertEqual(resp.created_by.display_name, "Uploader")
        self.assertEqual(resp.updated_by.user_id, 4)
        self.assertEqual(resp.updated_by.display_name, "Updater")
        self.assertEqual(resp.file_tags, ["docs", "text"])
        self.assertTrue(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.TEXT)

    def test_builds_response_with_nullable_fields(self):
        class FileObj:

            def __init__(self):
                self.id = 1
                self.folder_id = 2
                self.created_at = 100
                self.updated_at = None
                self.is_starred = False
                self.filename = "document.txt"
                self.filesize = 1024
                self.mimetype = None
                self.checksum = "a" * 64
                self.summary = None
                self.comments_count = 0
                self.latest_revision_number = 0
                self.file_created_by_user = SimpleNamespace(
                    id=3,
                    display_name="Uploader",
                )
                self.file_updated_by_user = None
                self.file_tags = []
                self.file_thumbnail = None

            @property
            def has_thumbnail(self):
                return self.file_thumbnail is not None

            @property
            def filetype(self):
                return FileType.BINARY

        resp = build_file_list_item_response(FileObj())

        self.assertIsInstance(resp, FileListItemResponse)
        self.assertEqual(resp.file_id, 1)
        self.assertIsNone(resp.updated_by)
        self.assertIsNone(resp.updated_at)
        self.assertIsNone(resp.mimetype)
        self.assertIsNone(resp.summary)
        self.assertEqual(resp.file_tags, [])
        self.assertFalse(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.BINARY)
