# tests/test_main.py
# SPDX-License-Identifier: SSPL-1.0

from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app import version as version_module  # noqa: E402
from app.errors import (  # noqa: E402
    InternalServerError,
    ResourceConflictError,
    ResourceForbiddenError,
    ResourceLockedError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    TooManyRequestsError,
    ValueAuthenticationError,
    ValueConflictError,
    ValueInvalidError,
    ValueNotFoundError,
)
from app.main import app, lifespan  # noqa: E402


def _methods_on_path(path: str) -> set[str]:
    collected: set[str] = set()
    for route in app.routes:
        if getattr(route, "path", None) != path:
            continue
        methods = getattr(route, "methods", None)
        if methods:
            collected |= set(methods)
    return collected


# Full paths under API_PREFIX; methods must be a subset of registered verbs
# (Starlette may add HEAD for GET routes).
_EXPECTED_API_ROUTES: tuple[tuple[str, frozenset[str]], ...] = (
    ("/api/v1/init/cipherdir", frozenset({"POST"})),
    ("/api/v1/init/cipherdir/mount", frozenset({"POST"})),
    ("/api/v1/init/cipherdir/unmount", frozenset({"POST"})),
    ("/api/v1/init/cipherdir/password", frozenset({"PATCH"})),
    ("/api/v1/init/lockdown/enable", frozenset({"POST"})),
    ("/api/v1/init/lockdown/disable", frozenset({"POST"})),
    ("/api/v1/init/health", frozenset({"GET"})),
    ("/api/v1/auth/register", frozenset({"POST"})),
    ("/api/v1/auth/login", frozenset({"POST"})),
    ("/api/v1/auth/token", frozenset({"POST", "DELETE"})),
    ("/api/v1/auth/totp", frozenset({"POST"})),
    ("/api/v1/user/{user_id}", frozenset({"GET"})),
    ("/api/v1/user", frozenset({"PATCH"})),
    ("/api/v1/user/password", frozenset({"PATCH"})),
    ("/api/v1/user/recovery", frozenset({"PATCH"})),
    ("/api/v1/user/{user_id}/role", frozenset({"PATCH"})),
    ("/api/v1/users", frozenset({"GET"})),
    ("/api/v1/folder", frozenset({"POST"})),
    ("/api/v1/folder/{folder_id}", frozenset({"GET", "PATCH", "DELETE"})),
    ("/api/v1/folder/{folder_id}/protected", frozenset({"PATCH"})),
    ("/api/v1/folders", frozenset({"GET"})),
    ("/api/v1/folder/{folder_id}/file", frozenset({"POST"})),
    ("/api/v1/file/{file_id}", frozenset({"GET", "PATCH"})),
    ("/api/v1/file/{file_id}/revision/{revision_number}", frozenset({"GET"})),
    ("/api/v1/file/{file_id}/starred", frozenset({"PATCH"})),
    ("/api/v1/file/{file_id}/move", frozenset({"POST"})),
    ("/api/v1/file/{file_id}/rotate", frozenset({"POST"})),
    ("/api/v1/file/{file_id}/flip", frozenset({"POST"})),
    ("/api/v1/file/{file_id}/edit", frozenset({"POST"})),
    ("/api/v1/file/{file_id}/thumbnail", frozenset({"GET"})),
    ("/api/v1/file/{file_id}/tag", frozenset({"POST"})),
    ("/api/v1/file/{file_id}/tag/{tag}", frozenset({"DELETE"})),
    ("/api/v1/files", frozenset({"GET"})),
    ("/api/v1/file/{file_id}/comment", frozenset({"POST"})),
    ("/api/v1/comment/{comment_id}", frozenset({"PATCH", "DELETE"})),
    (
        "/api/v1/variable/{namespace}/{variable_key}",
        frozenset({"PUT", "GET", "DELETE"}),
    ),
    ("/api/v1/variables/{namespace}", frozenset({"GET"})),
    ("/api/v1/metrics", frozenset({"GET"})),
    ("/api/v1/audit", frozenset({"GET"})),
)


class TestMainApp(IsolatedAsyncioTestCase):
    """Wiring checks for ``app.main`` (no real DB, network, or filesystem)."""

    _API = "/api/v1"

    def _route_methods(self, path: str) -> set[str]:
        """
        Return HTTP methods for all routes matching ``path``.

        FastAPI registers separate route objects per method; the same
        OpenAPI path (e.g. ``/api/v1/file/{file_id}``) may have both GET
        and PATCH handlers.
        """
        collected = _methods_on_path(path)
        if not collected:
            self.fail(f"Route was not registered: {path}")
        return collected

    def test_expected_api_surface_registered(self) -> None:
        for path, required in _EXPECTED_API_ROUTES:
            with self.subTest(path=path):
                registered = self._route_methods(path)
                self.assertTrue(
                    required <= registered,
                    msg=f"{path}: expected {required!r}, got {registered!r}",
                )

    def test_registers_file_update_route(self) -> None:
        methods = self._route_methods(f"{self._API}/file/{{file_id}}")

        self.assertIn("PATCH", methods)

    def test_registers_file_select_route(self) -> None:
        methods = self._route_methods(f"{self._API}/file/{{file_id}}")

        self.assertIn("GET", methods)

    def test_registers_file_starred_change_route(self) -> None:
        methods = self._route_methods(
            f"{self._API}/file/{{file_id}}/starred",
        )

        self.assertIn("PATCH", methods)

    def test_registers_file_edit_route(self) -> None:
        methods = self._route_methods(
            f"{self._API}/file/{{file_id}}/edit",
        )

        self.assertIn("POST", methods)

    def test_registers_file_list_route(self) -> None:
        methods = self._route_methods(f"{self._API}/files")

        self.assertIn("GET", methods)

    def test_registers_user_select_route(self) -> None:
        methods = self._route_methods(f"{self._API}/user/{{user_id}}")

        self.assertIn("GET", methods)

    def test_registers_init_health_route(self) -> None:
        methods = self._route_methods(f"{self._API}/init/health")

        self.assertIn("GET", methods)

    def test_openapi_and_docs_routes_exist(self) -> None:
        self.assertNotEqual(_methods_on_path("/openapi.json"), set())
        self.assertNotEqual(_methods_on_path("/docs"), set())

    def test_app_title_version_and_swagger_options(self) -> None:
        self.assertEqual(app.title, "Hidden — encrypted file storage")
        self.assertEqual(app.version, version_module.__version__)
        params = app.swagger_ui_parameters
        self.assertTrue(params.get("persistAuthorization"))
        self.assertTrue(params.get("displayRequestDuration"))
        self.assertTrue(params.get("tryItOutEnabled"))

    async def test_lifespan_startup_invokes_bootstrap_without_side_effects(
        self,
    ) -> None:
        fake_app = MagicMock()
        with (
            patch("app.main.init_logging") as mock_log,
            patch("app.main.load_all_models") as mock_models,
            patch("app.main.hooks.load_extensions") as mock_ext,
        ):
            async with lifespan(fake_app):
                mock_log.assert_called_once_with()
                mock_models.assert_called_once_with()
                mock_ext.assert_called_once_with()

    def test_domain_exception_handlers_registered(self) -> None:
        expected = (
            InternalServerError,
            ServiceUnavailableError,
            TooManyRequestsError,
            ResourceNotFoundError,
            ResourceForbiddenError,
            ResourceConflictError,
            ResourceLockedError,
            ValueInvalidError,
            ValueConflictError,
            ValueNotFoundError,
            ValueAuthenticationError,
        )
        for exc_type in expected:
            with self.subTest(exc=exc_type.__name__):
                self.assertIn(exc_type, app.exception_handlers)

    def test_gzip_and_cors_middleware_registered(self) -> None:
        classes = [m.cls for m in app.user_middleware]
        self.assertIn(GZipMiddleware, classes)
        self.assertIn(CORSMiddleware, classes)

    def test_http_middleware_layers_count(self) -> None:
        from starlette.middleware.base import BaseHTTPMiddleware

        base_http = sum(
            1 for m in app.user_middleware if m.cls is BaseHTTPMiddleware
        )
        self.assertGreaterEqual(base_http, 5)
