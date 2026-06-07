# tests/services/test_file_flip.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.file_thumbnail import FileThumbnail
from app.models.folder import Folder
from app.models.user import User
from app.schemas.file_flip import FileFlipRequest
from app.services.file_flip import _cleanup_path, flip_file
import app.services.file_flip as file_flip


class TestFlipFile(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        super().setUp()
        self._log_patcher = patch(
            "app.services.file_flip.log",
            MagicMock(),
        )
        self._log_patcher.start()
        self.addCleanup(self._log_patcher.stop)

        self._uuid_patcher = patch(
            "app.services.file_flip.uuid.uuid4",
            return_value=uuid.UUID("00000000-0000-4000-8000-0000000000aa"),
        )
        self._uuid_patcher.start()
        self.addCleanup(self._uuid_patcher.stop)

        self.thumbnail_cache_mock = MagicMock()
        self._thumbnail_cache_patcher = patch(
            "app.services.file_flip.get_thumbnail_cache",
            return_value=self.thumbnail_cache_mock,
        )
        self._thumbnail_cache_patcher.start()
        self.addCleanup(self._thumbnail_cache_patcher.stop)

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_folder(self):
        folder = MagicMock(spec=Folder)
        folder.id = 2
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False
        folder.get_absolute_dir.return_value = "/mnt/files/folder"
        return folder

    def _build_file(self, folder):
        file = MagicMock(spec=File)
        file.id = 1
        file.filename = "image.png"
        file.filesize = 100
        file.mimetype = "image/png"
        file.checksum = "old-checksum"
        file.updated_by = None
        file.latest_revision_number = 0
        file.file_folder = folder
        file.get_absolute_path.return_value = "/mnt/files/folder/image.png"
        file.is_image = True
        return file

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    async def test_flips_file_creates_revision_commits_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        old_thumbnail = None

        repository = AsyncMock()
        repository.select.side_effect = [file, old_thumbnail]
        repository.select_parent_chain.return_value = parent_chain
        repository.count_all.return_value = 0

        lock_context = self._build_lock_context()

        class _ImageTrueThenFalse:
            __slots__ = ("_n",)

            def __init__(self) -> None:
                self._n = 0

            def __bool__(self) -> bool:
                self._n += 1
                return self._n == 1

        file.is_image = _ImageTrueThenFalse()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ) as flip_image_mock,
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ) as get_filesize_mock,
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ) as get_mimetype_mock,
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ) as get_checksum_mock,
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ) as file_revision_mock,
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await flip_file(
                session=session,
                user=user,
                file_id=1,
                data=data,
            )

        self.assertIs(result, file)

        repository.select.assert_any_await(File, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )
        file.get_absolute_path.assert_called_once_with(folder, parent_chain)

        lock_file_mock.assert_called_once_with(
            "/mnt/files/folder/image.png",
            LockType.WRITE,
        )

        isdir_mock.assert_awaited_once_with("/mnt/files/folder/image.png")
        isfile_mock.assert_awaited_once_with("/mnt/files/folder/image.png")
        flip_image_mock.assert_awaited_once_with(
            "/mnt/files/folder/image.png",
            "/tmp/flipped",
            "horizontal",
        )

        get_filesize_mock.assert_any_await("/tmp/flipped")
        get_mimetype_mock.assert_any_await("/tmp/flipped")
        get_checksum_mock.assert_awaited_once_with("/tmp/flipped")

        repository.count_all.assert_awaited_once_with(
            file_revision_mock,
            file_id=1,
        )

        file_revision_mock.assert_called_once()
        self.assertEqual(file_revision_mock.call_args.kwargs["file_id"], 1)
        self.assertEqual(file_revision_mock.call_args.kwargs["created_by"], 10)
        self.assertEqual(
            file_revision_mock.call_args.kwargs["revision_number"],
            1,
        )
        self.assertEqual(
            file_revision_mock.call_args.kwargs["filename"],
            "image.png",
        )
        self.assertEqual(file_revision_mock.call_args.kwargs["filesize"], 100)
        self.assertEqual(
            file_revision_mock.call_args.kwargs["mimetype"],
            "image/png",
        )
        self.assertEqual(
            file_revision_mock.call_args.kwargs["checksum"],
            "old-checksum",
        )

        self.assertEqual(
            copy_mock.await_args_list,
            [
                call("/mnt/files/folder/image.png", "/mnt/revisions/rev-1"),
                call("/tmp/flipped", "/mnt/files/folder/image.png"),
            ],
        )

        repository.insert.assert_awaited_once_with(revision)
        repository.update.assert_awaited_once_with(file)

        self.assertEqual(file.filesize, 200)
        self.assertEqual(file.mimetype, "image/png")
        self.assertEqual(file.checksum, "new-checksum")
        self.assertEqual(file.updated_by, 10)
        self.assertEqual(file.latest_revision_number, 1)

        delete_mock.assert_awaited_once_with("/tmp/flipped")

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_FLIP_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=1,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        repository.select.assert_any_await(FileThumbnail, file_id=1)

        emit_mock.assert_awaited_once_with(
            E.FILE_FLIP_COMPLETED,
            session,
            file,
        )

    async def test_raises_not_found_when_file_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await flip_file(session, user, 1, data)

        repository.select.assert_awaited_once_with(File, obj_id=1)
        repository.select_parent_chain.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_file_is_not_image(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)
        file.mimetype = "text/plain"
        file.is_image = False

        repository = AsyncMock()
        repository.select.return_value = file

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await flip_file(session, user, 1, data)

        repository.select_parent_chain.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_folder_is_protected(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        folder.is_write_protected_recursive.return_value = True
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await flip_file(session, user, 1, data)

        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_path_is_directory(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ) as flip_image_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await flip_file(session, user, 1, data)

        isdir_mock.assert_awaited_once_with("/mnt/files/folder/image.png")
        isfile_mock.assert_not_awaited()
        flip_image_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_file_missing_on_disk(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ) as flip_image_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await flip_file(session, user, 1, data)

        isfile_mock.assert_awaited_once_with("/mnt/files/folder/image.png")
        flip_image_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_and_cleans_tmp_when_flip_fails(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(side_effect=RuntimeError("bad image")),
            ),
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await flip_file(session, user, 1, data)

        delete_mock.assert_awaited_once_with("/tmp/flipped")
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rollback_deletes_revision_insert_fails_before_replace(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.insert.side_effect = RuntimeError("db failed")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await flip_file(session, user, 1, data)

        copy_mock.assert_awaited_once_with(
            "/mnt/files/folder/image.png",
            "/mnt/revisions/rev-1",
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_has_awaits([
            call("/tmp/flipped"),
            call("/mnt/revisions/rev-1"),
        ])
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_restores_original_when_error_after_replace(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.update.side_effect = RuntimeError("db failed")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await flip_file(session, user, 1, data)

        self.assertEqual(
            copy_mock.await_args_list,
            [
                call("/mnt/files/folder/image.png", "/mnt/revisions/rev-1"),
                call("/tmp/flipped", "/mnt/files/folder/image.png"),
                call("/mnt/revisions/rev-1", "/mnt/files/folder/image.png"),
            ],
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_has_awaits([
            call("/tmp/flipped"),
            call("/mnt/revisions/rev-1"),
        ])
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_deletes_old_thumbnail_and_creates_new_thumbnail(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        old_thumbnail = MagicMock(spec=FileThumbnail)
        old_thumbnail.absolute_path = "/mnt/thumbs/old"

        new_thumbnail = MagicMock(spec=FileThumbnail)
        new_thumbnail.absolute_path = "/mnt/thumbs/new"

        repository = AsyncMock()
        repository.select.side_effect = [file, old_thumbnail]
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(side_effect=[200, 20]),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(side_effect=["image/png", "image/webp"]),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.FileThumbnail",
                return_value=new_thumbnail,
            ) as thumbnail_mock,
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.create_thumbnail",
                new=AsyncMock(),
            ) as create_thumbnail_mock,
            patch(
                "app.services.file_flip.get_image_size",
                new=AsyncMock(return_value=(320, 240)),
            ),
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result = await flip_file(session, user, 1, data)

        self.assertIs(result, file)

        repository.delete.assert_awaited_once_with(
            old_thumbnail,
            flush=False,
        )
        delete_mock.assert_has_awaits([
            call("/tmp/flipped"),
            call("/mnt/thumbs/old"),
        ])

        thumbnail_mock.assert_called_once()
        self.assertEqual(thumbnail_mock.call_args.kwargs["file_id"], 1)
        self.assertEqual(thumbnail_mock.call_args.kwargs["created_by"], 10)

        create_thumbnail_mock.assert_awaited_once_with(
            "/mnt/files/folder/image.png",
            "/mnt/thumbs/new",
        )

        self.assertEqual(new_thumbnail.filesize, 20)
        self.assertEqual(new_thumbnail.mimetype, "image/webp")
        self.assertEqual(new_thumbnail.width, 320)
        self.assertEqual(new_thumbnail.height, 240)

        repository.insert.assert_has_awaits([
            call(revision),
            call(new_thumbnail, flush=False),
        ])
        self.assertEqual(repository.commit.await_count, 3)
        self.assertIs(file.file_thumbnail, new_thumbnail)

    async def test_thumbnail_failure_is_best_effort(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        new_thumbnail = MagicMock(spec=FileThumbnail)
        new_thumbnail.absolute_path = "/mnt/thumbs/new"

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.FileThumbnail",
                return_value=new_thumbnail,
            ),
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.create_thumbnail",
                new=AsyncMock(side_effect=RuntimeError("thumbnail failed")),
            ),
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await flip_file(session, user, 1, data)

        self.assertIs(result, file)
        self.assertEqual(repository.rollback.await_count, 1)
        emit_mock.assert_awaited_once_with(
            E.FILE_FLIP_COMPLETED,
            session,
            file,
        )

    async def test_restore_copy_failure_logs_flip_restore_failed(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.update.side_effect = RuntimeError("db failed")

        lock_context = self._build_lock_context()

        restore_err = OSError("restore copy failed")

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(
                    side_effect=[None, None, restore_err],
                ),
            ) as copy_mock,
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await flip_file(session, user, 1, data)

        self.assertEqual(cm.exception.args[0], "db failed")

        self.assertEqual(
            copy_mock.await_args_list,
            [
                call("/mnt/files/folder/image.png", "/mnt/revisions/rev-1"),
                call("/tmp/flipped", "/mnt/files/folder/image.png"),
                call("/mnt/revisions/rev-1", "/mnt/files/folder/image.png"),
            ],
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_awaited_once_with("/tmp/flipped")
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_old_thumbnail_delete_failure_logs_and_skips_new_thumbnail(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        old_thumbnail = MagicMock(spec=FileThumbnail)
        old_thumbnail.absolute_path = "/mnt/thumbs/old"

        repository = AsyncMock()
        repository.select.side_effect = [file, old_thumbnail]
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.delete.side_effect = RuntimeError(
            "delete thumbnail row failed",
        )

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.create_thumbnail",
                new=AsyncMock(),
            ) as create_thumbnail_mock,
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await flip_file(session, user, 1, data)

        self.assertIs(result, file)
        repository.rollback.assert_awaited_once()
        create_thumbnail_mock.assert_not_awaited()
        emit_mock.assert_awaited_once_with(
            E.FILE_FLIP_COMPLETED,
            session,
            file,
        )

    async def test_cleanup_path_delete_failure_logs_cleanup_failed(self):
        with patch(
            "app.services.file_flip.delete",
            new=AsyncMock(side_effect=OSError("unlink failed")),
        ):
            await _cleanup_path("/mnt/ephemeral/stale")

        file_flip.log.exception.assert_called()
        self.assertIn(
            E.FILE_FLIP_CLEANUP_FAILED,
            file_flip.log.exception.call_args[0],
        )

    async def test_error_before_revision_path_set_skips_restore_if_block(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileFlipRequest(axis="horizontal")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_flip.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_flip.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_flip.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_flip.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.file_flip.get_tmp_path",
                return_value="/tmp/flipped",
            ),
            patch(
                "app.services.file_flip.flip_image",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_flip.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_flip.get_mimetype",
                new=AsyncMock(return_value="image/png"),
            ),
            patch(
                "app.services.file_flip.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_flip.FileRevision",
                return_value=revision,
            ),
            patch(
                "app.services.file_flip.copy",
                new=AsyncMock(
                    side_effect=RuntimeError("revision copy failed")
                ),
            ) as copy_mock,
            patch(
                "app.services.file_flip.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_flip.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_flip.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await flip_file(session, user, 1, data)

        self.assertEqual(cm.exception.args[0], "revision copy failed")

        copy_mock.assert_awaited_once_with(
            "/mnt/files/folder/image.png",
            "/mnt/revisions/rev-1",
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_awaited_once_with("/tmp/flipped")
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()
