# tests/schemas/test_audit_select.py
# SPDX-License-Identifier: SSPL-1.0

import logging
import unittest
from types import SimpleNamespace

from pydantic import ValidationError

from app.schemas.audit_select import AuditSelectResponse

_LOG = logging.getLogger(__name__)


class TestAuditSelectResponse(unittest.TestCase):
    def test_maps_id_alias_to_audit_id(self):
        row = SimpleNamespace(
            id=99,
            created_at=1_700_000_000,
            created_by=2,
            event="cipherdir_mount:succeeded",
            request_uuid="r1",
            resource_type="cipherdir",
            resource_id=3,
        )
        with self.assertLogs(_LOG.name, level="INFO") as cm:
            out = AuditSelectResponse.model_validate(row)
            _LOG.info(
                "event=%s audit_id=%s",
                "audit_select_schema:from_attributes_ok",
                out.audit_id,
            )

        self.assertTrue(
            any(
                "audit_select_schema:from_attributes_ok" in line
                for line in cm.output
            ),
            msg=cm.output,
        )
        self.assertEqual(out.audit_id, 99)
        self.assertEqual(out.created_at, 1_700_000_000)
        self.assertEqual(out.created_by, 2)
        self.assertEqual(out.event, "cipherdir_mount:succeeded")
        self.assertEqual(out.request_uuid, "r1")
        self.assertEqual(out.resource_type, "cipherdir")
        self.assertEqual(out.resource_id, 3)

    def test_optional_fields_default_to_none(self):
        row = SimpleNamespace(
            id=1,
            created_at=1,
            created_by=None,
            event="e",
            request_uuid=None,
            resource_type=None,
            resource_id=None,
        )
        with self.assertLogs(_LOG.name, level="INFO") as cm:
            out = AuditSelectResponse.model_validate(row)
            _LOG.info("event=%s", "audit_select_schema:optional_ok")

        self.assertTrue(
            any("audit_select_schema:optional_ok" in line for line in cm.output),  # noqa: E501
            msg=cm.output,
        )
        self.assertIsNone(out.created_by)
        self.assertIsNone(out.request_uuid)
        self.assertIsNone(out.resource_type)
        self.assertIsNone(out.resource_id)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            AuditSelectResponse(
                audit_id=1,
                created_at=1,
                event="e",
                other=1,
            )
