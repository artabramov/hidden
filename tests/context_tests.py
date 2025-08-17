import unittest
from app.context import get_context


class ContextTest(unittest.IsolatedAsyncioTestCase):

    def test_context_set_get_variable(self):
        ctx = get_context()
        ctx.key = "value"
        self.assertEqual(ctx.key, "value")

    def test_context_get_missing_variable(self):
        ctx = get_context()
        self.assertIsNone(ctx.some_non_existent_key)

    def test_context_set_multiple_variables(self):
        ctx = get_context()
        ctx.one = "one"
        ctx.two = "two"
        self.assertEqual(ctx.one, "one")
        self.assertEqual(ctx.two, "two")

    async def test_context_isolation_within_tasks(self):
        import asyncio

        async def task1():
            ctx = get_context()
            ctx.task_key = "task1_value"
            return ctx.task_key

        async def task2():
            ctx = get_context()
            ctx.task_key = "task2_value"
            return ctx.task_key

        loop = asyncio.get_event_loop()
        task1_result = await loop.create_task(task1())
        task2_result = await loop.create_task(task2())

        self.assertEqual(task1_result, "task1_value")
        self.assertEqual(task2_result, "task2_value")

    def test_context_update_variable(self):
        ctx = get_context()
        ctx.key = "initial_value"
        self.assertEqual(ctx.key, "initial_value")

        ctx.key = "updated_value"
        self.assertEqual(ctx.key, "updated_value")


if __name__ == "__main__":
    unittest.main()
