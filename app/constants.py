"""
This module defines various constants and hook types used throughout the
application to handle error locations, error types, and hook actions. It
serves as a key component for managing errors, monitoring system status,
and triggering events in the application.
"""

SPHINX_COPYRIGHT = "2024, Artem Abramov"
SPHINX_PROJECT = "Hidden"
SPHINX_AUTHOR = "Artem Abramov"

# Error location is the request headers.
LOC_HEADER = "header"

# Error location is the cookie values.
LOC_COOKIE = "cookie"

# Error location is the URL path.
LOC_PATH = "path"

# Error location is the query parameters.
LOC_QUERY = "query"

# Error location is the request body.
LOC_BODY = "body"

# The token has expired and is no longer valid (401).
ERR_TOKEN_EXPIRED = "token_expired"

# The token is invalid and cannot be processed (401).
ERR_TOKEN_INVALID = "token_invalid"

# The token contains an invalid token identifier (401).
ERR_TOKEN_REJECTED = "token_rejected"

# The user is deleted or could not be found (401).
ERR_TOKEN_ORPHANED = "token_orphaned"

# The user is inactive and cannot access the resource (401).
ERR_USER_INACTIVE = "user_inactive"

# The user is temporarily suspended; try again later (401).
ERR_USER_SUSPENDED = "user_suspended"

# The user role is insufficient for this action (401).
ERR_USER_ROLE_REJECTED = "user_role_rejected"

# The user password is not accepted (HTTP 401).
ERR_USER_PASSWORD_NOT_ACCEPTED = "password_not_accepted"

# The user cannot perform this action on the resource (403).
ERR_RESOURCE_FORBIDDEN = "resource_forbidden"

# The requested resource could not be found (404).
ERR_RESOURCE_NOT_FOUND = "resource_not_found"

# The value provided is empty (422).
ERR_VALUE_EMPTY = "value_empty"

# The value provided is invalid (422).
ERR_VALUE_INVALID = "value_invalid"

# The value provided already exists (422).
ERR_VALUE_DUPLICATED = "value_duplicated"

# The file MIME type is not supported for the operation (422).
ERR_MIMETYPE_UNSUPPORTED = "mimetype_unsupported"

# The resource that is being accessed is locked (423).
ERR_RESOURCE_LOCKED = "resource_locked"

# Internal server error (500).
ERR_SERVER_ERROR = "internal_server_error"

# Hook types used to manage various pre-event and post-event actions
# within the app. These hooks are used to trigger corresponding funcs
# that handle tasks related to app, users management, collections,
# documents, comments, revisions, etc.

# user hooks
HOOK_BEFORE_USER_REGISTER = "before_user_register"
HOOK_AFTER_USER_REGISTER = "after_user_register"
HOOK_BEFORE_USER_LOGIN = "before_user_login"
HOOK_AFTER_USER_LOGIN = "after_user_login"
HOOK_BEFORE_USER_DELETE = "before_user_delete"
HOOK_AFTER_USER_DELETE = "after_user_delete"
HOOK_BEFORE_TOKEN_RETRIEVE = "before_token_retrieve"
HOOK_AFTER_TOKEN_RETRIEVE = "after_token_retrieve"
HOOK_BEFORE_TOKEN_INVALIDATE = "before_token_invalidate"
HOOK_AFTER_TOKEN_INVALIDATE = "after_token_invalidate"
HOOK_BEFORE_MFA_SELECT = "before_mfa_select"
HOOK_AFTER_MFA_SELECT = "after_mfa_select"
HOOK_AFTER_USER_SELECT = "after_user_select"
HOOK_BEFORE_USER_UPDATE = "before_user_update"
HOOK_AFTER_USER_UPDATE = "after_user_update"
HOOK_BEFORE_ROLE_CHANGE = "before_role_change"
HOOK_AFTER_ROLE_CHANGE = "after_role_change"
HOOK_BEFORE_PASSWORD_CHANGE = "before_password_change"
HOOK_AFTER_PASSWORD_CHANGE = "after_password_change"
HOOK_BEFORE_USERPIC_UPLOAD = "before_userpic_upload"
HOOK_AFTER_USERPIC_UPLOAD = "after_userpic_upload"
HOOK_BEFORE_USERPIC_DELETE = "before_userpic_delete"
HOOK_AFTER_USERPIC_DELETE = "after_userpic_delete"
HOOK_AFTER_USER_LIST = "after_user_list"

# collection hooks
HOOK_BEFORE_COLLECTION_INSERT = "before_collection_insert"
HOOK_AFTER_COLLECTION_INSERT = "after_collection_insert"
HOOK_AFTER_COLLECTION_SELECT = "after_collection_select"
HOOK_BEFORE_COLLECTION_UPDATE = "before_collection_update"
HOOK_AFTER_COLLECTION_UPDATE = "after_collection_update"
HOOK_BEFORE_COLLECTION_DELETE = "before_collection_delete"
HOOK_AFTER_COLLECTION_DELETE = "after_collection_delete"
HOOK_AFTER_COLLECTION_LIST = "after_collection_list"

# partner hooks
HOOK_BEFORE_PARTNER_INSERT = "before_partner_insert"
HOOK_AFTER_PARTNER_INSERT = "after_partner_insert"
HOOK_AFTER_PARTNER_SELECT = "after_partner_select"
HOOK_BEFORE_PARTNER_UPDATE = "before_partner_update"
HOOK_AFTER_PARTNER_UPDATE = "after_partner_update"
HOOK_BEFORE_PARTNER_DELETE = "before_partner_delete"
HOOK_AFTER_PARTNER_DELETE = "after_partner_delete"
HOOK_AFTER_PARTNER_LIST = "after_partner_list"
HOOK_BEFORE_PARTNERPIC_UPLOAD = "before_partnerpic_upload"
HOOK_AFTER_PARTNERPIC_UPLOAD = "after_partnerpic_upload"
HOOK_BEFORE_PARTNERPIC_DELETE = "before_partnerpic_delete"
HOOK_AFTER_PARTNERPIC_DELETE = "after_partnerpic_delete"

# document hooks
HOOK_BEFORE_DOCUMENT_UPLOAD = "before_document_upload"
HOOK_AFTER_DOCUMENT_UPLOAD = "after_document_upload"
HOOK_BEFORE_DOCUMENT_REPLACE = "before_document_replace"
HOOK_AFTER_DOCUMENT_REPLACE = "after_document_replace"
HOOK_AFTER_DOCUMENT_SELECT = "after_document_select"
HOOK_BEFORE_DOCUMENT_UPDATE = "before_document_update"
HOOK_AFTER_DOCUMENT_UPDATE = "after_document_update"
HOOK_BEFORE_DOCUMENT_DELETE = "before_document_delete"
HOOK_AFTER_DOCUMENT_DELETE = "after_document_delete"
HOOK_AFTER_DOCUMENT_LIST = "after_document_list"

# comment hooks
HOOK_BEFORE_COMMENT_INSERT = "before_comment_insert"
HOOK_AFTER_COMMENT_INSERT = "after_comment_insert"
HOOK_AFTER_COMMENT_SELECT = "after_comment_select"
HOOK_BEFORE_COMMENT_UPDATE = "before_comment_update"
HOOK_AFTER_COMMENT_UPDATE = "after_comment_update"
HOOK_BEFORE_COMMENT_DELETE = "before_comment_delete"
HOOK_AFTER_COMMENT_DELETE = "after_comment_delete"
HOOK_AFTER_COMMENT_LIST = "after_comment_list"

# revision hooks
HOOK_BEFORE_REVISION_DOWNLOAD = "before_revision_download"
HOOK_AFTER_REVISION_LIST = "after_revision_list"

# download hooks
HOOK_AFTER_DOWNLOAD_LIST = "after_download_list"

# Option hooks
HOOK_AFTER_OPTION_SELECT = "after_option_select"
HOOK_BEFORE_OPTION_UPDATE = "before_option_update"
HOOK_AFTER_OPTION_UPDATE = "after_option_update"
HOOK_BEFORE_OPTION_DELETE = "before_option_delete"
HOOK_AFTER_OPTION_DELETE = "after_option_delete"
HOOK_AFTER_OPTION_LIST = "after_option_list"

# service hooks
HOOK_ON_TELEMETRY_RETRIEVE = "on_telemetry_retrieve"
HOOK_ON_LOCK_CHANGE = "on_lock_change"
HOOK_ON_LOCK_RETRIEVE = "on_lock_retrieve"
HOOK_ON_EXECUTE = "on_execute"
HOOK_ON_SCHEDULE = "on_schedule"
