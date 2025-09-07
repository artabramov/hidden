import unittest
from app.models.collection import Collection


class CollectionTest(unittest.IsolatedAsyncioTestCase):

    async def test_to_dict_basic(self):
        c = Collection(123, readonly=False, name="Inbox", summary=None)
        c.id = 1
        c.created_date = 111
        c.updated_date = 222

        self.assertEqual(
            await c.to_dict(),
            {
                "id": 1,
                "created_date": 111,
                "updated_date": 222,
                "readonly": False,
                "name": "Inbox",
                "summary": None,
            },
        )

    async def test_to_dict_with_summary(self):
        c = Collection(123, readonly=True, name="Projects",
                       summary="Main workspace")
        c.id = 2
        c.created_date = 1000
        c.updated_date = 2000

        self.assertEqual(
            await c.to_dict(),
            {
                "id": 2,
                "created_date": 1000,
                "updated_date": 2000,
                "readonly": True,
                "name": "Projects",
                "summary": "Main workspace",
            },
        )

    async def test_to_dict_unicode_name(self):
        c = Collection(123, readonly=False, name="коллекция📁", summary=None)
        c.id = 3
        c.created_date = 123
        c.updated_date = 456

        d = await c.to_dict()
        self.assertEqual(d["name"], "коллекция📁")
        self.assertIsNone(d["summary"])
        self.assertEqual(d["readonly"], False)
        self.assertEqual(d["id"], 3)
        self.assertEqual(d["created_date"], 123)
        self.assertEqual(d["updated_date"], 456)

    async def test_to_dict_large_summary(self):
        large = "x" * 4096
        c = Collection(123, readonly=False, name="Large", summary=large)
        c.id = 4
        c.created_date = 1
        c.updated_date = 2

        d = await c.to_dict()
        self.assertEqual(d["summary"], large)
        self.assertEqual(len(d["summary"]), 4096)

    async def test_to_dict_readonly_flag(self):
        c1 = Collection(123, readonly=False, name="A", summary=None)
        c1.id, c1.created_date, c1.updated_date = 10, 10, 10

        c2 = Collection(123, readonly=True, name="B", summary=None)
        c2.id, c2.created_date, c2.updated_date = 20, 20, 20

        self.assertFalse((await c1.to_dict())["readonly"])
        self.assertTrue((await c2.to_dict())["readonly"])
