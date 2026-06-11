# tests/schemas/test_file_select.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace

from pydantic import ValidationError

from app.models.file import FileType
from app.schemas.file_select import (
    FileSelectCommentResponse,
    FileSelectResponse,
    FileSelectRevisionResponse,
    FileSelectUserResponse,
    build_file_response,
)


class TestFileSelectUserResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileSelectUserResponse(
            id=1,
            display_name="Test User",
        )

        self.assertEqual(resp.user_id, 1)
        self.assertEqual(resp.display_name, "Test User")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileSelectUserResponse(
                id=1,
                display_name="Test User",
                other=1,
            )


class TestFileSelectCommentResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileSelectCommentResponse(
            id=1,
            created_by={
                "id": 2,
                "display_name": "Comment Author",
            },
            created_at=100,
            updated_at=200,
            body="Comment body.",
        )

        self.assertEqual(resp.comment_id, 1)
        self.assertEqual(resp.created_by.user_id, 2)
        self.assertEqual(
            resp.created_by.display_name,
            "Comment Author",
        )
        self.assertEqual(resp.created_at, 100)
        self.assertEqual(resp.updated_at, 200)
        self.assertEqual(resp.body, "Comment body.")

    def test_accepts_none_optional_fields(self):
        resp = FileSelectCommentResponse(
            id=1,
            created_by={
                "id": 2,
                "display_name": "Comment Author",
            },
            created_at=100,
            updated_at=None,
            body="Comment body.",
        )

        self.assertIsNone(resp.updated_at)


class TestFileSelectRevisionResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileSelectRevisionResponse(
            id=1,
            revision_number=2,
            created_by={
                "id": 3,
                "display_name": "Revision Author",
            },
            created_at=100,
            filesize=1024,
            mimetype="text/plain",
            checksum="a" * 64,
        )

        self.assertEqual(resp.revision_id, 1)
        self.assertEqual(resp.revision_number, 2)
        self.assertEqual(resp.created_by.user_id, 3)
        self.assertEqual(
            resp.created_by.display_name,
            "Revision Author",
        )
        self.assertEqual(resp.created_at, 100)
        self.assertEqual(resp.filesize, 1024)
        self.assertEqual(resp.mimetype, "text/plain")
        self.assertEqual(resp.checksum, "a" * 64)

    def test_accepts_none_optional_fields(self):
        resp = FileSelectRevisionResponse(
            id=1,
            revision_number=1,
            created_by={
                "id": 3,
                "display_name": "Revision Author",
            },
            created_at=100,
            filesize=1024,
            mimetype=None,
            checksum="a" * 64,
        )

        self.assertIsNone(resp.mimetype)


class TestFileSelectResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileSelectResponse(
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
            file_comments=[
                {
                    "id": 5,
                    "created_by": {
                        "id": 6,
                        "display_name": "Comment Author",
                    },
                    "created_at": 300,
                    "updated_at": None,
                    "body": "Comment body.",
                },
            ],
            file_revisions=[
                {
                    "id": 7,
                    "revision_number": 1,
                    "created_by": {
                        "id": 8,
                        "display_name": "Revision Author",
                    },
                    "created_at": 400,
                    "filesize": 512,
                    "mimetype": "text/plain",
                    "checksum": "b" * 64,
                },
            ],
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
        self.assertEqual(len(resp.file_comments), 1)
        self.assertEqual(len(resp.file_revisions), 1)

    def test_accepts_none_optional_fields(self):
        resp = FileSelectResponse(
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
            file_comments=[],
            file_revisions=[],
        )

        self.assertIsNone(resp.updated_by)
        self.assertIsNone(resp.updated_at)
        self.assertIsNone(resp.mimetype)
        self.assertIsNone(resp.summary)
        self.assertFalse(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.BINARY)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileSelectResponse(
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
                file_comments=[],
                file_revisions=[],
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
            "file_comments",
            "file_revisions",
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
                "updated_by_user": None,
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
                "file_comments": [],
                "file_revisions": [],
            }
            data.pop(field)

            with self.assertRaises(ValidationError) as cm:
                FileSelectResponse(**data)

            error = cm.exception.errors()[0]
            self.assertEqual(error["loc"], (field,))
            self.assertEqual(error["type"], "missing")


class TestBuildFileResponse(unittest.TestCase):

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
                self.file_comments = [
                    SimpleNamespace(
                        id=5,
                        created_at=300,
                        updated_at=None,
                        body="Comment body.",
                        comment_created_by_user=SimpleNamespace(
                            id=6,
                            display_name="Comment Author",
                        ),
                    ),
                ]
                self.file_revisions = [
                    SimpleNamespace(
                        id=7,
                        revision_number=1,
                        created_at=400,
                        filesize=512,
                        mimetype="text/plain",
                        checksum="b" * 64,
                        revision_created_by_user=SimpleNamespace(
                            id=8,
                            display_name="Revision Author",
                        ),
                    ),
                ]

            @property
            def has_thumbnail(self):
                return self.file_thumbnail is not None

            @property
            def filetype(self):
                return FileType.TEXT

        resp = build_file_response(FileObj())

        self.assertIsInstance(resp, FileSelectResponse)
        self.assertEqual(resp.file_id, 1)
        self.assertEqual(resp.created_by.user_id, 3)
        self.assertEqual(resp.created_by.display_name, "Uploader")
        self.assertEqual(resp.updated_by.user_id, 4)
        self.assertEqual(resp.updated_by.display_name, "Updater")
        self.assertEqual(resp.file_tags, ["docs", "text"])
        self.assertTrue(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.TEXT)
        self.assertEqual(resp.file_comments[0].comment_id, 5)
        self.assertEqual(
            resp.file_comments[0].created_by.display_name,
            "Comment Author",
        )
        self.assertEqual(resp.file_revisions[0].revision_id, 7)
        self.assertEqual(
            resp.file_revisions[0].created_by.display_name,
            "Revision Author",
        )

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
                self.file_comments = []
                self.file_revisions = []

            @property
            def has_thumbnail(self):
                return self.file_thumbnail is not None

            @property
            def filetype(self):
                return FileType.BINARY

        resp = build_file_response(FileObj())

        self.assertEqual(resp.file_id, 1)
        self.assertIsNone(resp.updated_by)
        self.assertIsNone(resp.mimetype)
        self.assertFalse(resp.has_thumbnail)
        self.assertEqual(resp.filetype, FileType.BINARY)
