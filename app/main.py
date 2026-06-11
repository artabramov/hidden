# app/main.py
# SPDX-License-Identifier: GPL-3.0-only

from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware

from app.config import get_config
from app.log import init_logging
from app.hooks import hooks
from app.version import __version__
from app.openapi import TAGS_METADATA
from app.db.engine import load_all_models

from app.errors import (
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

from app.middleware.cors_setup import cors_setup_middleware
from app.middleware.request_context import request_context_middleware
from app.middleware.request_logging import request_logging_middleware
from app.middleware.lockdown_mode import lockdown_mode_middleware
from app.middleware.mountpoint_check import mountpoint_check_middleware
from app.middleware.security_headers import security_headers_middleware

from app.handlers.internal_server_error import internal_server_error_handler
from app.handlers.service_unavailable import service_unavailable_handler
from app.handlers.too_many_requests import too_many_requests_handler
from app.handlers.resource_not_found import resource_not_found_handler
from app.handlers.resource_forbidden import resource_forbidden_handler
from app.handlers.resource_conflict import resource_conflict_handler
from app.handlers.resource_locked import resource_locked_handler
from app.handlers.value_invalid import value_invalid_handler
from app.handlers.value_conflict import value_conflict_handler
from app.handlers.value_not_found import value_not_found_handler
from app.handlers.value_authentication import value_authentication_handler

# NOTE (ADR-13): TLS termination is handled by the external gateway.
# Backend should not terminate TLS directly if it is deployed behind a
# dedicated entrypoint container. HTTPS should be handled only at the
# external gateway, while backend traffic remains internal-only.

from app.routers.cipherdir_create import router as create_cipherdir_router
from app.routers.cipherdir_mount import router as mount_cipherdir_router
from app.routers.cipherdir_unmount import router as unmount_cipherdir_router
from app.routers.cipherdir_password_change import router as change_cipherdir_password_router  # noqa E501
from app.routers.lockdown_enable import router as enable_lockdown_router
from app.routers.lockdown_disable import router as disable_lockdown_router
from app.routers.health_check import router as health_check_router
from app.routers.user_register import router as register_user_router
from app.routers.user_login import router as login_user_router
from app.routers.user_token_issue import router as issue_token_router
from app.routers.user_totp_recover import router as user_totp_recover_router
from app.routers.user_token_invalidate import router as invalidate_token_router
from app.routers.user_select import router as select_user_router
from app.routers.user_update import router as update_user_router
from app.routers.user_password_change import router as change_user_password_router  # noqa E501
from app.routers.user_recovery_code_rotate import router as rotate_user_recovery_code_router  # noqa E501
from app.routers.user_role_change import router as change_user_role_router
from app.routers.user_list import router as list_users_router
from app.routers.folder_create import router as folder_create_router
from app.routers.folder_select import router as folder_select_router
from app.routers.folder_update import router as folder_update_router
from app.routers.folder_delete import router as folder_delete_router
from app.routers.folder_write_protect import router as folder_write_protect_router  # noqa: E501
from app.routers.folder_list import router as folder_list_router
from app.routers.file_upload import router as file_upload_router
from app.routers.file_download import router as file_download_router
from app.routers.file_select import router as file_select_router
from app.routers.file_update import router as file_update_router
from app.routers.file_starred_change import router as file_starred_change_router  # noqa: E501
from app.routers.file_delete import router as file_delete_router
from app.routers.file_move import router as file_move_router
from app.routers.file_rotate import router as file_rotate_router
from app.routers.file_flip import router as file_flip_router
from app.routers.file_edit import router as file_edit_router
from app.routers.file_list import router as file_list_router
from app.routers.file_thumbnail_retrieve import router as thumbnail_retrieve_router  # noqa: E501
from app.routers.file_tag_add import router as file_tag_add_router
from app.routers.file_tag_delete import router as file_tag_delete_router
from app.routers.file_tag_list import router as file_tag_list_router
from app.routers.comment_create import router as comment_create_router
from app.routers.comment_update import router as comment_update_router
from app.routers.comment_delete import router as comment_delete_router
from app.routers.variable_set import router as variable_set_router
from app.routers.variable_get import router as variable_get_router
from app.routers.variable_delete import router as variable_delete_router
from app.routers.variable_list import router as variable_list_router
from app.routers.metrics_retrieve import router as metrics_retrieve_router
from app.routers.audit_list import router as audit_list_router

config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging()
    load_all_models()
    hooks.load_extensions()
    yield


app = FastAPI(
    title="Hidden — encrypted file storage",
    version=__version__,
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    }
)

# NOTE (ADR-29): Middleware order is intentionally fixed.
# The order is intentional and must not be changed. Request context
# is initialized before other middleware and reset only after the full
# request lifecycle completes. Downstream middleware (e.g. request
# logging) depends on this. This is an architectural constraint, not
# an implementation detail.

# NOTE (ADR-14): Network-layer attack mitigation is externalized.
# Volumetric DDoS, connection floods, and similar network- or edge-layer
# attacks are not mitigated inside this application. Deployments are
# expected to address them at the reverse proxy, load balancer, firewall,
# upstream provider or cloud mitigation, or equivalent.

app.middleware("http")(lockdown_mode_middleware)
app.middleware("http")(mountpoint_check_middleware)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(request_context_middleware)
app.middleware("http")(security_headers_middleware)
cors_setup_middleware(app)
app.add_middleware(GZipMiddleware)

app.add_exception_handler(InternalServerError, internal_server_error_handler)
app.add_exception_handler(ServiceUnavailableError, service_unavailable_handler)
app.add_exception_handler(TooManyRequestsError, too_many_requests_handler)
app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
app.add_exception_handler(ResourceForbiddenError, resource_forbidden_handler)
app.add_exception_handler(ResourceConflictError, resource_conflict_handler)
app.add_exception_handler(ResourceLockedError, resource_locked_handler)
app.add_exception_handler(ValueInvalidError, value_invalid_handler)
app.add_exception_handler(ValueConflictError, value_conflict_handler)
app.add_exception_handler(ValueNotFoundError, value_not_found_handler)
app.add_exception_handler(ValueAuthenticationError, value_authentication_handler)  # noqa E501

app.include_router(create_cipherdir_router, prefix=config.API_PREFIX)
app.include_router(mount_cipherdir_router, prefix=config.API_PREFIX)
app.include_router(unmount_cipherdir_router, prefix=config.API_PREFIX)
app.include_router(change_cipherdir_password_router, prefix=config.API_PREFIX)
app.include_router(enable_lockdown_router, prefix=config.API_PREFIX)
app.include_router(disable_lockdown_router, prefix=config.API_PREFIX)
app.include_router(health_check_router, prefix=config.API_PREFIX)
app.include_router(register_user_router, prefix=config.API_PREFIX)
app.include_router(login_user_router, prefix=config.API_PREFIX)
app.include_router(issue_token_router, prefix=config.API_PREFIX)
app.include_router(user_totp_recover_router, prefix=config.API_PREFIX)
app.include_router(invalidate_token_router, prefix=config.API_PREFIX)
app.include_router(select_user_router, prefix=config.API_PREFIX)
app.include_router(update_user_router, prefix=config.API_PREFIX)
app.include_router(change_user_password_router, prefix=config.API_PREFIX)
app.include_router(rotate_user_recovery_code_router, prefix=config.API_PREFIX)
app.include_router(change_user_role_router, prefix=config.API_PREFIX)
app.include_router(list_users_router, prefix=config.API_PREFIX)
app.include_router(folder_create_router, prefix=config.API_PREFIX)
app.include_router(folder_select_router, prefix=config.API_PREFIX)
app.include_router(folder_update_router, prefix=config.API_PREFIX)
app.include_router(folder_delete_router, prefix=config.API_PREFIX)
app.include_router(folder_write_protect_router, prefix=config.API_PREFIX)
app.include_router(folder_list_router, prefix=config.API_PREFIX)
app.include_router(file_upload_router, prefix=config.API_PREFIX)
app.include_router(file_download_router, prefix=config.API_PREFIX)
app.include_router(file_select_router, prefix=config.API_PREFIX)
app.include_router(file_update_router, prefix=config.API_PREFIX)
app.include_router(file_starred_change_router, prefix=config.API_PREFIX)
app.include_router(file_delete_router, prefix=config.API_PREFIX)
app.include_router(file_move_router, prefix=config.API_PREFIX)
app.include_router(file_rotate_router, prefix=config.API_PREFIX)
app.include_router(file_flip_router, prefix=config.API_PREFIX)
app.include_router(file_edit_router, prefix=config.API_PREFIX)
app.include_router(file_list_router, prefix=config.API_PREFIX)
app.include_router(file_tag_add_router, prefix=config.API_PREFIX)
app.include_router(file_tag_delete_router, prefix=config.API_PREFIX)
app.include_router(file_tag_list_router, prefix=config.API_PREFIX)
app.include_router(thumbnail_retrieve_router, prefix=config.API_PREFIX)
app.include_router(comment_create_router, prefix=config.API_PREFIX)
app.include_router(comment_update_router, prefix=config.API_PREFIX)
app.include_router(comment_delete_router, prefix=config.API_PREFIX)
app.include_router(variable_set_router, prefix=config.API_PREFIX)
app.include_router(variable_get_router, prefix=config.API_PREFIX)
app.include_router(variable_delete_router, prefix=config.API_PREFIX)
app.include_router(variable_list_router, prefix=config.API_PREFIX)
app.include_router(metrics_retrieve_router, prefix=config.API_PREFIX)
app.include_router(audit_list_router, prefix=config.API_PREFIX)
