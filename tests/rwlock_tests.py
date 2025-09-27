import asyncio
import unittest
from app.rwlock import RWLock


class RWLockTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.lock = RWLock()

    async def test_multiple_readers_allowed(self):
        started = asyncio.Event()
        both_inside = asyncio.Event()
        inside = 0

        async def reader():
            nonlocal inside
            async with self.lock.read():
                if not started.is_set():
                    started.set()
                inside += 1
                if inside == 2:
                    both_inside.set()
                await asyncio.wait_for(both_inside.wait(), timeout=1.0)

        t1 = asyncio.create_task(reader())
        t2 = asyncio.create_task(reader())

        await asyncio.wait_for(started.wait(), timeout=1.0)
        await asyncio.gather(t1, t2)

    async def test_writer_exclusive_after_readers(self):
        order = []

        async def reader():
            async with self.lock.read():
                order.append("R-in")
                await asyncio.sleep(0.05)
            order.append("R-out")

        async def writer():
            async with self.lock.write():
                order.append("W-in")
                await asyncio.sleep(0.01)
            order.append("W-out")

        r = asyncio.create_task(reader())
        await asyncio.sleep(0.005)
        w = asyncio.create_task(writer())

        await asyncio.gather(r, w)

        self.assertEqual(order[0], "R-in")
        self.assertIn("R-out", order)
        self.assertIn("W-in", order)
        self.assertLess(order.index("R-out"), order.index("W-in"))

    async def test_writer_preference_blocks_new_readers(self):
        events = {
            "r1_in": asyncio.Event(),
            "w_in": asyncio.Event(),
            "r2_in": False
        }

        async def r1():
            async with self.lock.read():
                events["r1_in"].set()
                await asyncio.sleep(0.05)

        async def w():
            await events["r1_in"].wait()
            async with self.lock.write():
                events["w_in"].set()
                await asyncio.sleep(0.01)

        async def r2():
            await events["r1_in"].wait()
            async with self.lock.read():
                events["r2_in"] = True

        t_r1 = asyncio.create_task(r1())
        await events["r1_in"].wait()

        t_w = asyncio.create_task(w())
        await asyncio.sleep(0)
        t_r2 = asyncio.create_task(r2())

        await asyncio.wait_for(events["w_in"].wait(), timeout=1.0)
        await asyncio.gather(t_r1, t_w, t_r2)
        self.assertTrue(events["r2_in"])

    async def test_readers_drain_before_writer_enters(self):
        marks = []

        async def reader(tag, delay):
            async with self.lock.read():
                marks.append(f"{tag}-in")
                await asyncio.sleep(delay)
            marks.append(f"{tag}-out")

        async def writer():
            async with self.lock.write():
                marks.append("W-in")
                await asyncio.sleep(0.005)
            marks.append("W-out")

        r1 = asyncio.create_task(reader("R1", 0.03))
        r2 = asyncio.create_task(reader("R2", 0.02))
        await asyncio.sleep(0.001)
        w = asyncio.create_task(writer())

        await asyncio.gather(r1, r2, w)

        self.assertLess(marks.index("R1-out"), marks.index("W-in"))
        self.assertLess(marks.index("R2-out"), marks.index("W-in"))

    async def test_cancellation_of_waiting_reader_leaves_lock_consistent(self):
        entered = asyncio.Event()

        async def writer():
            async with self.lock.write():
                await asyncio.sleep(0.05)

        async def reader_waiting():
            async with self.lock.read():
                entered.set()

        w_task = asyncio.create_task(writer())
        await asyncio.sleep(0.005)

        r_task = asyncio.create_task(reader_waiting())
        await asyncio.sleep(0.005)
        r_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await r_task

        await w_task
        async with self.lock.read():
            pass
        self.assertFalse(entered.is_set())

    async def test_cancellation_of_waiting_writer_leaves_lock_consistent(self):
        async def reader():
            async with self.lock.read():
                await asyncio.sleep(0.05)

        async def writer_waiting():
            async with self.lock.write():
                pass

        r_task = asyncio.create_task(reader())
        await asyncio.sleep(0.005)

        w_task = asyncio.create_task(writer_waiting())
        await asyncio.sleep(0.005)
        w_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await w_task
        await r_task

        async with self.lock.write():
            pass

    async def test_context_releases_on_exception(self):
        with self.assertRaises(RuntimeError):
            async with self.lock.read():
                raise RuntimeError("boom")

        async with self.lock.read():
            pass

        with self.assertRaises(RuntimeError):
            async with self.lock.write():
                raise RuntimeError("boom")

        async with self.lock.write():
            pass

    async def test_read_then_write_sequencing_between_tasks(self):
        timeline = []

        async def reader():
            async with self.lock.read():
                timeline.append("R-in")
                await asyncio.sleep(0.02)
            timeline.append("R-out")

        async def writer():
            async with self.lock.write():
                timeline.append("W-in")
            timeline.append("W-out")

        r = asyncio.create_task(reader())
        await asyncio.sleep(0.001)
        w = asyncio.create_task(writer())
        await asyncio.gather(r, w)

        self.assertEqual(timeline[0], "R-in")
        self.assertEqual(timeline[1], "R-out")
        self.assertEqual(timeline[2], "W-in")
        self.assertEqual(timeline[3], "W-out")
