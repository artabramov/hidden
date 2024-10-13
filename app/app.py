"""
This module sets up and configures the FastAPI application. It includes
middleware for logging HTTP requests and responses, an exception handler
for managing and responding to errors, and a lifespan context manager
for handling startup tasks such as loading extension modules,
registering hooks, and initializing the database schema. The application
also includes routes for static files and other resources, with specific
configuration for the application's title, version, and file paths.
"""

import time
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.helpers.lock_helper import remove_lock
from app.config import get_config
from app.context import get_context
from app.openapi import openapi_tags
from app.log import get_log
from app.routers import (
    token_retrieve_router, token_invalidate_router, user_register_router,
    mfa_retrieve_router, user_login_router, user_select_router,
    user_update_router, user_delete_router, role_change_router,
    password_change_router, userpic_upload_router, userpic_delete_router,
    user_list_router,

    collection_insert_router, collection_select_router,
    collection_update_router, collection_delete_router,
    collection_list_router,

    member_insert_router, member_select_router, member_update_router,
    member_delete_router, member_list_router,

    datafile_upload_router, datafile_replace_router,
    datafile_download_router, datafile_select_router,
    datafile_update_router, datafile_delete_router,
    datafile_list_router,

    comment_insert_router, comment_select_router, comment_update_router,
    comment_delete_router, comment_list_router,

    revision_select_router, revision_download_router, revision_list_router,

    favorite_insert_router, favorite_select_router, favorite_delete_router,
    favorite_list_router, download_select_router, download_list_router,

    option_insert_router, option_select_router, option_update_router,
    option_delete_router, option_list_router,

    telemetry_retrieve_router, lock_create_router, lock_delete_router,
    cache_erase_router, custom_execute_router, sphinx_router,
    heartbeat_retrieve_router)
from app.database import Base, sessionmanager
from app.constants import ERR_SERVER_ERROR
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from app.version import __version__
from app.helpers.openapi_helper import load_description
from app.helpers.uptime_helper import Uptime
from app.helpers.hook_helper import load_hooks

cfg = get_config()
ctx = get_context()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup lifecycle by removing the lock if
    it exists, initializing the database schema, and registering hooks.
    Yields control back to the application after setup is complete.
    """
    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await remove_lock()
    await load_hooks()
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=__version__,
              description=load_description(), openapi_tags=openapi_tags)

app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

uptime = Uptime()

# user routers
app.include_router(user_login_router.router, prefix=cfg.APP_PREFIX)
app.include_router(token_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(token_invalidate_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_register_router.router, prefix=cfg.APP_PREFIX)
app.include_router(mfa_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(role_change_router.router, prefix=cfg.APP_PREFIX)
app.include_router(password_change_router.router, prefix=cfg.APP_PREFIX)
app.include_router(userpic_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(userpic_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_list_router.router, prefix=cfg.APP_PREFIX)

# collection routers
app.include_router(collection_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_list_router.router, prefix=cfg.APP_PREFIX)

# member routers
app.include_router(member_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(member_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(member_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(member_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(member_list_router.router, prefix=cfg.APP_PREFIX)

# datafile routers
app.include_router(datafile_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(datafile_replace_router.router, prefix=cfg.APP_PREFIX)
app.include_router(datafile_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(datafile_download_router.router, prefix=cfg.APP_PREFIX)
app.include_router(datafile_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(datafile_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(datafile_list_router.router, prefix=cfg.APP_PREFIX)

# revision routers
app.include_router(revision_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(revision_download_router.router, prefix=cfg.APP_PREFIX)
app.include_router(revision_list_router.router, prefix=cfg.APP_PREFIX)

# download routers
app.include_router(download_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(download_list_router.router, prefix=cfg.APP_PREFIX)

# comment routers
app.include_router(comment_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_list_router.router, prefix=cfg.APP_PREFIX)

# favorite routers
app.include_router(favorite_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(favorite_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(favorite_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(favorite_list_router.router, prefix=cfg.APP_PREFIX)

# option routers
app.include_router(option_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_list_router.router, prefix=cfg.APP_PREFIX)

# service routers
app.include_router(telemetry_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_create_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(cache_erase_router.router, prefix=cfg.APP_PREFIX)
app.include_router(custom_execute_router.router, prefix=cfg.APP_PREFIX)
app.include_router(heartbeat_retrieve_router.router, prefix=cfg.APP_PREFIX)

# The router is necessary to handle the redirect from /sphinx to /sphinx/
# This ensures that requests to the endpoint with or without a trailing
# slash are properly managed.
app.include_router(sphinx_router.router)
app.mount("/sphinx",
          StaticFiles(directory="/hidden/docs/_build/html", html=True),
          name="sphinx")

app.mount(cfg.USERPIC_PREFIX,
          StaticFiles(directory=cfg.USERPIC_BASE_PATH, html=False),
          name=cfg.USERPIC_BASE_PATH)
app.mount(cfg.THUMBNAILS_PREFIX,
          StaticFiles(directory=cfg.THUMBNAILS_BASE_PATH, html=False),
          name=cfg.THUMBNAILS_BASE_PATH)
app.mount("/", StaticFiles(directory=cfg.HTML_PATH, html=True), name="/")


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    Middleware function that logs details of incoming HTTP requests and
    outgoing responses. It records the start time and a unique trace ID
    for each request, logs the request method, URL, and headers, then
    processes the request. After receiving the response, it calculates
    the elapsed time, logs the response status and headers, and returns
    the response to the client.
    """
    ctx.request_start_time = time.time()
    ctx.trace_request_uuid = str(uuid4())

    log.debug("Request received; module=app; function=middleware_handler; "
              "elapsed_time=0; method=%s; url=%s; headers=%s;" % (
                  request.method, str(request.url), str(request.headers)))

    response = await call_next(request)

    elapsed_time = time.time() - ctx.request_start_time
    log.debug("Response sent; module=app; function=middleware_handler; "
              "elapsed_time=%s; status=%s; headers=%s;" % (
                  "{0:.10f}".format(elapsed_time), response.status_code,
                  str(response.headers.raw)))

    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    """
    Handles all exceptions raised during request processing by
    calculating the elapsed time and returning a JSON response with
    an appropriate status code. If the exception is a ValidationError
    from Pydantic, it logs detailed validation error information and
    responds with 422 status code and the validation errors. For other
    exceptions, it logs an error message and responds with 500 status
    code and a generic error message.
    """
    elapsed_time = time.time() - ctx.request_start_time

    # Handle validation errors raised by Pydantic schema validators.
    if isinstance(e, ValidationError):
        log.debug("Response sent; module=app; function=exception_handler; "
                  "elapsed_time=%s; status=%s; headers=%s;" % (
                    elapsed_time, status.HTTP_422_UNPROCESSABLE_ENTITY,
                    str(e)))

        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=jsonable_encoder({"detail": e.errors()}))

    # Handle all other exceptions.
    else:
        log.error("Request failed; module=app; function=exception_handler; "
                  "elapsed_time=%s; e=%s;" % (elapsed_time, str(e)))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"detail": ERR_SERVER_ERROR}))
