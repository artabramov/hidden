import unittest
from app.error import E
from fastapi import HTTPException


class ErrorTestCase(unittest.TestCase):

    def test_error_init(self):
        loc = ["loc"]
        error_input = "input"
        error_type = "type"
        status_code = 422

        e = E(loc, error_input, error_type, status_code)
        self.assertTrue(isinstance(e, HTTPException))
        self.assertEqual(e.status_code, status_code)
        self.assertEqual(e.detail[0]["loc"], loc)
        self.assertEqual(e.detail[0]["input"], error_input)
        self.assertEqual(e.detail[0]["type"], error_type)
