# tests/test_locks.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import os
import unittest
from unittest.mock import patch

from app.locks import LockManager, LockResource, LockType


class TestLockManagerResources(unittest.TestCase):

    def setUp(self):
        self.manager = LockManager()

    def test_build_directory_resource_normalizes_path(self):
        resource = self.manager._build_directory_resource("/tmp/a/../b")

        self.assertEqual(
            resource,
            LockResource(directory=os.path.abspath("/tmp/b")),
        )

    def test_build_file_resource_normalizes_path(self):
        resource = self.manager._build_file_resource("/tmp/a/../b/file.txt")

        self.assertEqual(
            resource,
            LockResource(
                directory=os.path.abspath("/tmp/b"),
                filename="file.txt",
            ),
        )

    def test_build_file_resource_bare_filename_relative_to_cwd(self):
        """Single-segment path: dirname normalizes to '.', basename kept."""
        resource = self.manager._build_file_resource("solo.txt")

        self.assertEqual(resource.filename, "solo.txt")
        self.assertEqual(
            resource.directory,
            os.path.normpath(os.path.dirname(os.path.abspath("solo.txt"))),
        )

    def test_build_file_resource_rejects_path_without_filename(self):
        with self.assertRaises(ValueError):
            self.manager._build_file_resource("/")


class TestLockManagerOverlap(unittest.TestCase):

    def setUp(self):
        self.manager = LockManager()

    def test_same_directory_overlaps(self):
        left = LockResource(directory="/tmp/a")
        right = LockResource(directory="/tmp/a")

        self.assertTrue(self.manager._resources_overlap(left, right))

    def test_parent_and_child_directory_overlap(self):
        parent = LockResource(directory="/tmp/a")
        child = LockResource(directory="/tmp/a/b")

        self.assertTrue(self.manager._resources_overlap(parent, child))
        self.assertTrue(self.manager._resources_overlap(child, parent))

    def test_sibling_directories_do_not_overlap(self):
        left = LockResource(directory="/tmp/a")
        right = LockResource(directory="/tmp/ab")

        self.assertFalse(self.manager._resources_overlap(left, right))

    def test_directory_overlaps_file_inside_subtree(self):
        directory = LockResource(directory="/tmp/a")
        file = LockResource(directory="/tmp/a/b", filename="file.txt")

        self.assertTrue(self.manager._resources_overlap(directory, file))
        self.assertTrue(self.manager._resources_overlap(file, directory))

    def test_directory_does_not_overlap_file_outside_subtree(self):
        directory = LockResource(directory="/tmp/a")
        file = LockResource(directory="/tmp/b", filename="file.txt")

        self.assertFalse(self.manager._resources_overlap(directory, file))

    def test_same_file_overlaps(self):
        left = LockResource(directory="/tmp/a", filename="file.txt")
        right = LockResource(directory="/tmp/a", filename="file.txt")

        self.assertTrue(self.manager._resources_overlap(left, right))

    def test_different_files_do_not_overlap(self):
        left = LockResource(directory="/tmp/a", filename="one.txt")
        right = LockResource(directory="/tmp/a", filename="two.txt")

        self.assertFalse(self.manager._resources_overlap(left, right))

    def test_directory_contains_file_false_when_filename_none(self):
        pseudo_file = LockResource(directory="/tmp/a", filename=None)

        self.assertFalse(
            self.manager._directory_contains_file(
                directory="/tmp/a",
                file_resource=pseudo_file,
            ),
        )

    def test_is_same_or_descendant_path_false_when_commonpath_value_error(
        self,
    ):
        with patch(
            "app.locks.os.path.commonpath",
            side_effect=ValueError("paths incompatible"),
        ):
            self.assertFalse(
                self.manager._is_same_or_descendant_path(
                    "/tmp/a",
                    "/tmp/a/b",
                ),
            )


class TestLockManagerConflicts(unittest.TestCase):

    def setUp(self):
        self.manager = LockManager()

    def test_read_read_on_overlapping_resources_is_compatible(self):
        resource = LockResource(directory="/tmp/a")

        self.assertFalse(
            self.manager._conflicts(
                requested_resource=resource,
                requested_lock_type=LockType.READ,
                held_resource=resource,
                held_lock_type=LockType.READ,
            )
        )

    def test_read_write_on_overlapping_resources_conflicts(self):
        resource = LockResource(directory="/tmp/a")

        self.assertTrue(
            self.manager._conflicts(
                requested_resource=resource,
                requested_lock_type=LockType.READ,
                held_resource=resource,
                held_lock_type=LockType.WRITE,
            )
        )

    def test_write_read_on_overlapping_resources_conflicts(self):
        resource = LockResource(directory="/tmp/a")

        self.assertTrue(
            self.manager._conflicts(
                requested_resource=resource,
                requested_lock_type=LockType.WRITE,
                held_resource=resource,
                held_lock_type=LockType.READ,
            )
        )

    def test_write_write_on_overlapping_resources_conflicts(self):
        resource = LockResource(directory="/tmp/a")

        self.assertTrue(
            self.manager._conflicts(
                requested_resource=resource,
                requested_lock_type=LockType.WRITE,
                held_resource=resource,
                held_lock_type=LockType.WRITE,
            )
        )

    def test_non_overlapping_resources_do_not_conflict(self):
        requested = LockResource(directory="/tmp/a")
        held = LockResource(directory="/tmp/b")

        self.assertFalse(
            self.manager._conflicts(
                requested_resource=requested,
                requested_lock_type=LockType.WRITE,
                held_resource=held,
                held_lock_type=LockType.WRITE,
            )
        )


class TestLockManagerAsync(unittest.IsolatedAsyncioTestCase):

    async def test_allows_concurrent_read_locks_on_same_directory(self):
        manager = LockManager()

        async with manager.lock_directory("/tmp/a", LockType.READ):
            async with manager.lock_directory("/tmp/a", LockType.READ):
                self.assertEqual(len(manager._holders), 2)

        self.assertEqual(manager._holders, [])

    async def test_write_lock_waits_for_read_lock_on_same_directory(self):
        manager = LockManager()
        acquired = asyncio.Event()
        release_read = asyncio.Event()

        async def reader():
            async with manager.lock_directory("/tmp/a", LockType.READ):
                acquired.set()
                await release_read.wait()

        async def writer():
            async with manager.lock_directory("/tmp/a", LockType.WRITE):
                return "done"

        reader_task = asyncio.create_task(reader())
        await acquired.wait()

        writer_task = asyncio.create_task(writer())
        await asyncio.sleep(0)

        self.assertFalse(writer_task.done())

        release_read.set()

        self.assertEqual(await writer_task, "done")
        await reader_task
        self.assertEqual(manager._holders, [])

    async def test_file_write_waits_for_parent_directory_read(self):
        manager = LockManager()
        acquired = asyncio.Event()
        release_read = asyncio.Event()

        async def reader():
            async with manager.lock_directory("/tmp/a", LockType.READ):
                acquired.set()
                await release_read.wait()

        async def writer():
            async with manager.lock_file("/tmp/a/file.txt", LockType.WRITE):
                return "done"

        reader_task = asyncio.create_task(reader())
        await acquired.wait()

        writer_task = asyncio.create_task(writer())
        await asyncio.sleep(0)

        self.assertFalse(writer_task.done())

        release_read.set()

        self.assertEqual(await writer_task, "done")
        await reader_task
        self.assertEqual(manager._holders, [])

    async def test_file_write_does_not_wait_for_different_file(self):
        manager = LockManager()

        async with manager.lock_file("/tmp/a/one.txt", LockType.WRITE):
            async with manager.lock_file("/tmp/a/two.txt", LockType.WRITE):
                self.assertEqual(len(manager._holders), 2)

        self.assertEqual(manager._holders, [])

    async def test_lock_is_released_when_context_raises(self):
        manager = LockManager()

        with self.assertRaises(RuntimeError):
            async with manager.lock_directory("/tmp/a", LockType.WRITE):
                raise RuntimeError("boom")

        self.assertEqual(manager._holders, [])

    async def test_release_unknown_lock_raises_runtime_error(self):
        manager = LockManager()
        resource = LockResource(directory="/tmp/a")

        with self.assertRaises(RuntimeError):
            await manager._release(resource, LockType.WRITE)
