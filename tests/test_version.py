# tests/test_version.py
# SPDX-License-Identifier: Apache-2.0

import unittest

from app.version import __version__


class TestVersion(unittest.TestCase):
    def test_reports_current_version(self):
        self.assertEqual(__version__, "0.6.0")
