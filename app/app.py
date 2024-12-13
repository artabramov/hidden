"""
The module sets up and configures the FastAPI application. It includes
middleware for logging HTTP requests and responses, an exception handler
for managing and responding to errors, and a lifespan context manager
for handling startup tasks such as loading plugin modules, registering
hooks, and initializing the database schema. The application also
includes routes for static files and other resources, with specific
configuration for the application's title, version, and file paths.
Additionally, the application manages scheduling background tasks,
handles CORS for cross-origin requests, and initializes necessary
triggers during startup. Configuration settings such as the application
title, version, and API prefixes are loaded from the configuration file.
"""

import time
import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy import text
from app.version import __version__
from app.config import get_config
from app.constants import ERR_SERVER_ERROR
from app.openapi import openapi_tags
from app.database import Base, sessionmanager
from app.cache import get_cache
from app.context import get_context
from app.log import get_log
from app.scheduler import scheduler
from app.triggers.document_triggers import DOCUMENT_TRIGGERS
from app.triggers.comment_triggers import COMMENT_TRIGGERS
from app.triggers.revision_triggers import REVISION_TRIGGERS
from app.triggers.download_triggers import DOWNLOAD_TRIGGERS
from app.routers import (
    token_retrieve_router,
    token_invalidate_router,
    user_register_router,
    user_login_router,
    user_mfa_router,
    user_select_router,
    user_update_router,
    user_delete_router,
    user_role_router,
    user_password_router,
    userpic_upload_router,
    userpic_delete_router,
    user_list_router,
    partner_insert_router,
    partner_select_router,
    partner_update_router,
    partner_delete_router,
    partner_list_router,
    partnerpic_upload_router,
    partnerpic_delete_router,
    collection_insert_router,
    collection_select_router,
    collection_update_router,
    collection_lock_router,
    collection_delete_router,
    collection_list_router,
    document_upload_router,
    document_select_router,
    document_update_router,
    document_delete_router,
    document_list_router,
    document_move_router,
    document_flag_router,
    document_replace_router,
    document_download_router,
    document_revisions_router,
    document_downloads_router,
    comment_insert_router,
    comment_select_router,
    comment_update_router,
    comment_delete_router,
    comment_list_router,
    option_select_router,
    option_update_router,
    option_delete_router,
    option_list_router,
    lock_change_router,
    lock_retrieve_router,
    telemetry_retrieve_router,
    execute_router,
    sphinx_router)
from app.helpers.uptime_helper import Uptime
from app.helpers.lock_helper import lock_disable
from app.helpers.hook_helper import load_hooks

cfg = get_config()
ctx = get_context()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The lifespan context manager handles the application startup
    lifecycle. It disables any existing locks, loads hooks, initializes
    the database schema, and registers necessary database triggers for
    documents, comments, revisions, and downloads. The function ensures
    that the Redis cache is flushed to clear any existing data and
    schedules background tasks to run asynchronously. Once all setup
    tasks are completed, control is yielded back to the FastAPI
    application for normal operation. This function is designed to
    be used with FastAPI's lifespan parameter to manage initialization
    tasks during the application's startup process.
    """
    await lock_disable()
    await load_hooks()

    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        triggers = (DOCUMENT_TRIGGERS + COMMENT_TRIGGERS +
                    REVISION_TRIGGERS + DOWNLOAD_TRIGGERS)
        for trigger in triggers:
            await conn.execute(text(trigger))

    cache_gen = get_cache()
    async for cache in cache_gen:
        await cache.flushdb()

    asyncio.create_task(scheduler())
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=__version__,
              openapi_tags=openapi_tags)

app.add_middleware(
    CORSMiddleware, allow_origins=[
        cfg.APP_BASE_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

uptime = Uptime()

app.include_router(token_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(token_invalidate_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_register_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_login_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_mfa_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_role_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_password_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_list_router.router, prefix=cfg.APP_PREFIX)
app.include_router(userpic_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(userpic_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_lock_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_list_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partner_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partner_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partner_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partner_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partner_list_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partnerpic_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(partnerpic_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_list_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_replace_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_move_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_flag_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_download_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_revisions_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_downloads_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_list_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_list_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_change_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(telemetry_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(execute_router.router, prefix=cfg.APP_PREFIX)

# The router is necessary to handle the redirect from /sphinx to /sphinx/
# This ensures that requests to the endpoint with or without a trailing
# slash are properly managed.
app.include_router(sphinx_router.router)
app.mount(
    "/sphinx", StaticFiles(directory="/hidden/docs/_build/html", html=True),
    name="sphinx")

app.mount(cfg.USERPIC_PREFIX,
          StaticFiles(directory=cfg.USERPIC_BASE_PATH, html=False),
          name=cfg.USERPIC_BASE_PATH)

app.mount(cfg.THUMBNAILS_PREFIX,
          StaticFiles(directory=cfg.THUMBNAILS_BASE_PATH, html=False),
          name=cfg.THUMBNAILS_BASE_PATH)

app.mount(cfg.PARTNERPIC_PREFIX,
          StaticFiles(directory=cfg.PARTNERPIC_BASE_PATH, html=False),
          name=cfg.PARTNERPIC_BASE_PATH)

app.mount("/", StaticFiles(directory=cfg.APP_HTML_PATH, html=True), name="/")


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    The middleware_handler is an HTTP middleware that logs details of
    incoming requests and outgoing responses. It records the start time,
    generates a unique trace ID for each request, and logs the HTTP
    method, URL, and headers. After processing the request, it
    calculates the elapsed time, logs the response status, headers, and
    the time taken to handle the request. This middleware is used to
    monitor and log the performance of requests and responses, providing
    insight into request processing times and system behavior.
    """
    ctx.request_start_time = time.time()
    ctx.trace_request_uuid = str(uuid4())
    ctx.request = request

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
    The exception_handler is responsible for handling all exceptions
    raised during request processing. It calculates the elapsed time for
    processing the request and returns an appropriate JSON response based
    on the type of exception. If the exception is a ValidationError from
    Pydantic, it logs detailed validation error information and returns
    a 422 status code with the validation errors in the response. For
    other exceptions, it logs an error message and responds with
    a 500 status code and a generic server error message. This handler
    ensures that exceptions are properly managed and meaningful error
    responses are provided to the client.
    """
    elapsed_time = time.time() - ctx.request_start_time

    if isinstance(e, ValidationError):
        log.debug("Response sent; module=app; function=exception_handler; "
                  "elapsed_time=%s; status=%s; headers=%s;" % (
                    elapsed_time, status.HTTP_422_UNPROCESSABLE_ENTITY,
                    str(e)))

        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=jsonable_encoder({"detail": e.errors()}))

    else:
        log.error("Request failed; module=app; function=exception_handler; "
                  "elapsed_time=%s; e=%s;" % (elapsed_time, str(e)))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"detail": ERR_SERVER_ERROR}))
