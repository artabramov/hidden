import unittest
from app.context import get_context


class ContextTestCase(unittest.TestCase):

    def test_set_and_get_context_variable(self):
        """Test setting and getting a context variable."""
        ctx = get_context()
        ctx.some_key = "some_value"
        self.assertEqual(ctx.some_key, "some_value")

    def test_get_missing_context_variable(self):
        """Test retrieving a context variable that was not set."""
        ctx = get_context()
        self.assertIsNone(ctx.some_non_existent_key)

    def test_set_multiple_context_variables(self):
        """Test setting and retrieving multiple context variables."""
        ctx = get_context()
        ctx.var_one = "value_one"
        ctx.var_two = "value_two"
        self.assertEqual(ctx.var_one, "value_one")
        self.assertEqual(ctx.var_two, "value_two")

    async def test_context_isolation_within_tasks(self):
        """Test that context is isolated within different async tasks."""
        import asyncio

        async def task1():
            ctx = get_context()
            ctx.task_key = "task1_value"
            return ctx.task_key

        async def task2():
            ctx = get_context()
            ctx.task_key = "task2_value"
            return ctx.task_key

        # Run tasks concurrently and assert that context is isolated
        loop = asyncio.get_event_loop()
        task1_result = await loop.create_task(task1())
        task2_result = await loop.create_task(task2())

        self.assertEqual(task1_result, "task1_value")
        self.assertEqual(task2_result, "task2_value")

    def test_update_existing_context_variable(self):
        """Test updating the value of an existing context variable."""
        ctx = get_context()
        ctx.existing_key = "initial_value"
        self.assertEqual(ctx.existing_key, "initial_value")

        # Update value
        ctx.existing_key = "updated_value"
        self.assertEqual(ctx.existing_key, "updated_value")


if __name__ == "__main__":
    unittest.main()
