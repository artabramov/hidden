# tests/schemas/test_audit_list.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import unittest

from pydantic import ValidationError

from app.schemas.audit_list import (
    AUDIT_LIST_ERRORS,
    AuditListRequest,
    AuditListResponse,
)
from app.schemas.audit_select import AuditSelectResponse

_LOG = logging.getLogger(__name__)


class TestAuditListRequest(unittest.TestCase):
    def test_accepts_valid_payload(self):
        with self.assertLogs(_LOG.name, level="INFO") as cm:
            req = AuditListRequest(
                created_at__ge=1,
                created_at__le=2,
                created_by__eq=3,
                event__ilike="token",
                request_uuid__eq="abc",
                resource_type__eq="users",
                resource_id__eq=9,
                offset=10,
                limit=100,
                order_by="event",
                order="asc",
            )
            _LOG.info(
                "event=%s order_by=%s order=%s",
                "audit_list_schema:request_ok",
                req.order_by,
                req.order,
            )

        self.assertTrue(
            any("audit_list_schema:request_ok" in line for line in cm.output),
            msg=cm.output,
        )
        self.assertEqual(req.created_at__ge, 1)
        self.assertEqual(req.created_at__le, 2)
        self.assertEqual(req.created_by__eq, 3)
        self.assertEqual(req.event__ilike, "token")
        self.assertEqual(req.request_uuid__eq, "abc")
        self.assertEqual(req.resource_type__eq, "users")
        self.assertEqual(req.resource_id__eq, 9)
        self.assertEqual(req.offset, 10)
        self.assertEqual(req.limit, 100)
        self.assertEqual(req.order_by, "event")
        self.assertEqual(req.order, "asc")

    def test_uses_defaults(self):
        with self.assertLogs(_LOG.name, level="INFO") as cm:
            req = AuditListRequest()
            _LOG.info(
                "event=%s offset=%s limit=%s order_by=%s order=%s",
                "audit_list_schema:defaults_ok",
                req.offset,
                req.limit,
                req.order_by,
                req.order,
            )

        self.assertTrue(
            any("audit_list_schema:defaults_ok" in line for line in cm.output),
            msg=cm.output,
        )
        self.assertIsNone(req.created_at__ge)
        self.assertIsNone(req.created_at__le)
        self.assertIsNone(req.created_by__eq)
        self.assertIsNone(req.event__ilike)
        self.assertIsNone(req.request_uuid__eq)
        self.assertIsNone(req.resource_type__eq)
        self.assertIsNone(req.resource_id__eq)
        self.assertEqual(req.offset, 0)
        self.assertEqual(req.limit, 50)
        self.assertEqual(req.order_by, "created_at")
        self.assertEqual(req.order, "desc")

    def test_strips_whitespace_on_string_fields(self):
        with self.assertLogs(_LOG.name, level="INFO") as cm:
            req = AuditListRequest(
                event__ilike="  token  ",
                request_uuid__eq="  uuid  ",
                resource_type__eq="  users  ",
            )
            _LOG.info("event=%s", "audit_list_schema:stripped_strings_ok")

        self.assertTrue(
            any(
                "audit_list_schema:stripped_strings_ok" in line
                for line in cm.output
            ),
            msg=cm.output,
        )
        self.assertEqual(req.event__ilike, "token")
        self.assertEqual(req.request_uuid__eq, "uuid")
        self.assertEqual(req.resource_type__eq, "users")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            AuditListRequest(other=1)

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(AUDIT_LIST_ERRORS),
            {401, 403, 422, 503},
        )


class TestAuditListResponse(unittest.TestCase):
    def test_accepts_audit_rows_and_count(self):
        rows = [
            AuditSelectResponse(
                audit_id=1,
                created_at=10,
                created_by=None,
                event="e",
                request_uuid=None,
                resource_type=None,
                resource_id=None,
            ),
        ]
        with self.assertLogs(_LOG.name, level="INFO") as cm:
            body = AuditListResponse(audit=rows, audit_count=1)
            _LOG.info(
                "event=%s audit_count=%s",
                "audit_list_schema:response_ok",
                body.audit_count,
            )

        self.assertTrue(
            any("audit_list_schema:response_ok" in line for line in cm.output),
            msg=cm.output,
        )
        self.assertEqual(body.audit_count, 1)
        self.assertEqual(len(body.audit), 1)
        self.assertEqual(body.audit[0].audit_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            AuditListResponse(
                audit=[],
                audit_count=0,
                other=1,
            )

    def test_audit_count_rejects_negative(self):
        with self.assertRaises(ValidationError) as cm:
            AuditListResponse(audit=[], audit_count=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("audit_count",))
        self.assertEqual(error["type"], "greater_than_equal")
