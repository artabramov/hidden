# app/events.py
# SPDX-License-Identifier: SSPL-1.0


# NOTE (ADR-25): Logging and audit are correlated using request UUID.
# Events are the single source of truth for both logging and audit.
# Audit trail is implemented as a subset of these events and is
# correlated with logs via request UUID. Logs capture all significant
# events (including failures and intermediate states), while the audit
# trail includes successful domain mutations and file download
# (security-sensitive read).

class Events:
    """
    Events define a stable, machine-readable contract for all
    significant actions and states. They are emitted from service
    and dependency layers and included in structured logs and audit.
    """
    REQUEST_STARTED = "request:started"
    REQUEST_FAILED = "request:failed"
    REQUEST_COMPLETED = "request:completed"

    CIPHERDIR_CREATE_STARTED = "cipherdir_create:started"
    CIPHERDIR_CREATE_ALREADY_CREATED = "cipherdir_create:already_created"
    CIPHERDIR_CREATE_PASSPHRASE_EXISTS = "cipherdir_create:passphrase_exists"
    CIPHERDIR_CREATE_JWT_KEY_EXISTS = "cipherdir_create:jwt_key_exists"
    CIPHERDIR_CREATE_FERNET_KEY_EXISTS = "cipherdir_create:fernet_key_exists"
    CIPHERDIR_CREATE_FAILED = "cipherdir_create:failed"
    CIPHERDIR_CREATE_COMPLETED = "cipherdir_create:completed"

    CIPHERDIR_MOUNT_STARTED = "cipherdir_mount:started"
    CIPHERDIR_MOUNT_CIPHERDIR_NOT_CREATED = "cipherdir_mount:cipherdir_not_created"  # noqa: E501
    CIPHERDIR_MOUNT_PASSPHRASE_MISSING = "cipherdir_mount:passphrase_missing"
    CIPHERDIR_MOUNT_ALREADY_MOUNTED = "cipherdir_mount:already_mounted"
    CIPHERDIR_MOUNT_PASSPHRASE_INVALID = "cipherdir_mount:passphrase_invalid"
    CIPHERDIR_MOUNT_ROLLBACK_FAILED = "cipherdir_mount:rollback_failed"
    CIPHERDIR_MOUNT_ROLLBACK_COMPLETED = "cipherdir_mount:rollback_completed"
    CIPHERDIR_MOUNT_FAILED = "cipherdir_mount:failed"
    CIPHERDIR_MOUNT_COMPLETED = "cipherdir_mount:completed"

    CIPHERDIR_UNMOUNT_STARTED = "cipherdir_unmount:started"
    CIPHERDIR_UNMOUNT_CIPHERDIR_NOT_CREATED = "cipherdir_unmount:cipherdir_not_created"  # noqa: E501
    CIPHERDIR_UNMOUNT_PASSPHRASE_MISSING = "cipherdir_unmount:passphrase_missing"  # noqa: E501
    CIPHERDIR_UNMOUNT_ALREADY_UNMOUNTED = "cipherdir_unmount:already_unmounted"
    CIPHERDIR_UNMOUNT_PASSPHRASE_INVALID = "cipherdir_unmount:passphrase_invalid"  # noqa: E501
    CIPHERDIR_UNMOUNT_COMPLETED = "cipherdir_unmount:completed"

    CIPHERDIR_PASSWORD_CHANGE_STARTED = "cipherdir_password_change:started"
    CIPHERDIR_PASSWORD_CHANGE_CIPHERDIR_NOT_CREATED = "cipherdir_password_change:cipherdir_not_created"  # noqa: E501
    CIPHERDIR_PASSWORD_CHANGE_PASSPHRASE_MISSING = "cipherdir_password_change:passphrase_missing"  # noqa: E501
    CIPHERDIR_PASSWORD_CHANGE_PASSPHRASE_INVALID = "cipherdir_password_change:passphrase_invalid"  # noqa: E501
    CIPHERDIR_PASSWORD_CHANGE_COMPLETED = "cipherdir_password_change:completed"

    LOCKDOWN_ENABLE_STARTED = "lockdown_enable:started"
    LOCKDOWN_ENABLE_ALREADY_ENABLED = "lockdown_enable:already_enabled"
    LOCKDOWN_ENABLE_PASSPHRASE_MISSING = "lockdown_enable:passphrase_missing"
    LOCKDOWN_ENABLE_PASSPHRASE_INVALID = "lockdown_enable:passphrase_invalid"
    LOCKDOWN_ENABLE_COMPLETED = "lockdown_enable:completed"

    LOCKDOWN_DISABLE_STARTED = "lockdown_disable:started"
    LOCKDOWN_DISABLE_ALREADY_DISABLED = "lockdown_disable:already_disabled"
    LOCKDOWN_DISABLE_PASSPHRASE_MISSING = "lockdown_disable:passphrase_missing"
    LOCKDOWN_DISABLE_PASSPHRASE_INVALID = "lockdown_disable:passphrase_invalid"
    LOCKDOWN_DISABLE_COMPLETED = "lockdown_disable:completed"

    USER_REGISTER_STARTED = "user_register:started"
    USER_REGISTER_USERNAME_EXISTS = "user_register:username_exists"
    USER_REGISTER_ATTEMPTS_LIMITED = "user_register:attempts_limited"
    USER_REGISTER_COMPLETED = "user_register:completed"

    USER_LOGIN_STARTED = "user_login:started"
    USER_LOGIN_USERNAME_NOT_FOUND = "user_login:username_not_found"
    USER_LOGIN_USER_INACTIVE = "user_login:user_inactive"
    USER_LOGIN_USER_SUSPENDED = "user_login:user_suspended"
    USER_LOGIN_PASSWORD_INVALID = "user_login:password_invalid"
    USER_LOGIN_COMPLETED = "user_login:completed"

    USER_TOKEN_ISSUE_STARTED = "user_token_issue:started"
    USER_TOKEN_ISSUE_USER_NOT_FOUND = "user_token_issue:user_not_found"
    USER_TOKEN_ISSUE_USER_INACTIVE = "user_token_issue:user_inactive"
    USER_TOKEN_ISSUE_USER_SUSPENDED = "user_token_issue:user_suspended"
    USER_TOKEN_ISSUE_PASSWORD_NOT_VERIFIED = "user_token_issue:password_not_verified"  # noqa: E501
    USER_TOKEN_ISSUE_TOTP_INVALID = "user_token_issue:totp_invalid"
    USER_TOKEN_ISSUE_COMPLETED = "user_token_issue:completed"

    USER_TOTP_RECOVER_STARTED = "user_totp_recover:started"
    USER_TOTP_RECOVER_USER_NOT_FOUND = "user_totp_recover:user_not_found"
    USER_TOTP_RECOVER_USER_INACTIVE = "user_totp_recover:user_inactive"
    USER_TOTP_RECOVER_USER_SUSPENDED = "user_totp_recover:user_suspended"
    USER_TOTP_RECOVER_PASSWORD_NOT_VERIFIED = "user_totp_recover:password_not_verified"  # noqa: E501
    USER_TOTP_RECOVER_RECOVERY_CODE_INVALID = "user_totp_recover:recovery_code_invalid"  # noqa: E501
    USER_TOTP_RECOVER_COMPLETED = "user_totp_recover:completed"

    USER_TOKEN_INVALIDATE_STARTED = "user_token_invalidate:started"
    USER_TOKEN_INVALIDATE_COMPLETED = "user_token_invalidate:completed"

    USER_PASSWORD_CHANGE_STARTED = "user_password_change:started"
    USER_PASSWORD_CHANGE_PASSWORD_INVALID = "user_password_change:password_invalid"  # noqa: E501
    USER_PASSWORD_CHANGE_COMPLETED = "user_password_change:completed"

    USER_RECOVERY_CODE_ROTATE_STARTED = "user_recovery_code_rotate:started"
    USER_RECOVERY_CODE_ROTATE_RECOVERY_CODE_INVALID = "user_recovery_code_rotate:recovery_code_invalid"  # noqa: E501
    USER_RECOVERY_CODE_ROTATE_COMPLETED = "user_recovery_code_rotate:completed"

    USER_ROLE_CHANGE_STARTED = "user_role_change:started"
    USER_ROLE_CHANGE_USER_NOT_FOUND = "user_role_change:user_not_found"
    USER_ROLE_CHANGE_DENIED = "user_role_change:denied"
    USER_ROLE_CHANGE_COMPLETED = "user_role_change:completed"

    USER_SELECT_STARTED = "user_select:started"
    USER_SELECT_USER_NOT_FOUND = "user_select:user_not_found"
    USER_SELECT_DENIED = "user_select:denied"
    USER_SELECT_COMPLETED = "user_select:completed"

    USER_UPDATE_STARTED = "user_update:started"
    USER_UPDATE_COMPLETED = "user_update:completed"

    USER_LIST_STARTED = "user_list:started"
    USER_LIST_COMPLETED = "user_list:completed"

    FOLDER_CREATE_STARTED = "folder_create:started"
    FOLDER_CREATE_PARENT_NOT_FOUND = "folder_create:parent_not_found"
    FOLDER_CREATE_PARENT_WRITE_PROTECTED = "folder_create:parent_write_protected"  # noqa: E501
    FOLDER_CREATE_DIRNAME_CONFLICT = "folder_create:dirname_conflict"
    FOLDER_CREATE_DEPTH_LIMIT_EXCEEDED = "folder_create:depth_limit_exceeded"
    FOLDER_CREATE_PATH_TOO_LONG = "folder_create:path_too_long"
    FOLDER_CREATE_CLEANUP_FAILED = "folder_create:cleanup_failed"
    FOLDER_CREATE_COMPLETED = "folder_create:completed"

    FOLDER_SELECT_STARTED = "folder_select:started"
    FOLDER_SELECT_FOLDER_NOT_FOUND = "folder_select:folder_not_found"
    FOLDER_SELECT_COMPLETED = "folder_select:completed"

    FOLDER_UPDATE_STARTED = "folder_update:started"
    FOLDER_UPDATE_FOLDER_NOT_FOUND = "folder_update:folder_not_found"
    FOLDER_UPDATE_WRITE_PROTECTED = "folder_update:write_protected"
    FOLDER_UPDATE_DIRNAME_CONFLICT = "folder_update:dirname_conflict"
    FOLDER_UPDATE_PATH_TOO_LONG = "folder_update:path_too_long"
    FOLDER_UPDATE_ROLLBACK_FAILED = "folder_update:rollback_failed"
    FOLDER_UPDATE_COMPLETED = "folder_update:completed"

    FOLDER_DELETE_STARTED = "folder_delete:started"
    FOLDER_DELETE_FOLDER_NOT_FOUND = "folder_delete:folder_not_found"
    FOLDER_DELETE_WRITE_PROTECTED = "folder_delete:write_protected"
    FOLDER_DELETE_HAS_FOLDERS = "folder_delete:has_folders"
    FOLDER_DELETE_HAS_FILES = "folder_delete:has_files"
    FOLDER_DELETE_FAILED = "folder_delete:failed"
    FOLDER_DELETE_INCONSISTENT = "folder_delete:inconsistent"
    FOLDER_DELETE_COMPLETED = "folder_delete:completed"

    FOLDER_WRITE_PROTECT_STARTED = "folder_write_protect:started"
    FOLDER_WRITE_PROTECT_FOLDER_NOT_FOUND = "folder_write_protect:folder_not_found"  # noqa: E501
    FOLDER_WRITE_PROTECT_COMPLETED = "folder_write_protect:completed"

    FOLDER_LIST_STARTED = "folder_list:started"
    FOLDER_LIST_PARENT_NOT_FOUND = "folder_list:parent_not_found"
    FOLDER_LIST_COMPLETED = "folder_list:completed"

    FILE_UPLOAD_STARTED = "file_upload:started"
    FILE_UPLOAD_FOLDER_NOT_FOUND = "file_upload:folder_not_found"
    FILE_UPLOAD_FOLDER_WRITE_PROTECTED = "file_upload:folder_write_protected"
    FILE_UPLOAD_FILENAME_INVALID = "file_upload:filename_invalid"
    FILE_UPLOAD_FILENAME_CONFLICT = "file_upload:filename_conflict"
    FILE_UPLOAD_PATH_TOO_LONG = "file_upload:path_too_long"
    FILE_UPLOAD_CLEANUP_COMPLETED = "file_upload:cleanup_completed"
    FILE_UPLOAD_CLEANUP_FAILED = "file_upload:cleanup_failed"
    FILE_UPLOAD_RESTORE_FAILED = "file_upload:restore_failed"
    FILE_UPLOAD_THUMBNAIL_FAILED = "file_upload:thumbnail_failed"
    FILE_UPLOAD_COMPLETED = "file_upload:completed"

    FILE_DOWNLOAD_STARTED = "file_download:started"
    FILE_DOWNLOAD_NOT_FOUND = "file_download:not_found"
    FILE_DOWNLOAD_COMPLETED = "file_download:completed"

    FILE_SELECT_STARTED = "file_select:started"
    FILE_SELECT_NOT_FOUND = "file_select:not_found"
    FILE_SELECT_COMPLETED = "file_select:completed"

    FILE_UPDATE_STARTED = "file_update:started"
    FILE_UPDATE_FILE_NOT_FOUND = "file_update:file_not_found"
    FILE_UPDATE_PARENT_WRITE_PROTECTED = "file_update:parent_write_protected"
    FILE_UPDATE_FILENAME_CONFLICT = "file_update:filename_conflict"
    FILE_UPDATE_PATH_TOO_LONG = "file_update:path_too_long"
    FILE_UPDATE_RESTORE_FAILED = "file_update:restore_failed"
    FILE_UPDATE_COMPLETED = "file_update:completed"

    FILE_STARRED_CHANGE_STARTED = "file_starred_change:started"
    FILE_STARRED_CHANGE_FILE_NOT_FOUND = "file_starred_change:file_not_found"
    FILE_STARRED_CHANGE_COMPLETED = "file_starred_change:completed"

    FILE_MOVE_STARTED = "file_move:started"
    FILE_MOVE_FILE_NOT_FOUND = "file_move:file_not_found"
    FILE_MOVE_FOLDER_NOT_FOUND = "file_move:folder_not_found"
    FILE_MOVE_SOURCE_WRITE_PROTECTED = "file_move:source_write_protected"
    FILE_MOVE_DESTINATION_WRITE_PROTECTED = "file_move:destination_write_protected"  # noqa: E501
    FILE_MOVE_FILENAME_CONFLICT = "file_move:filename_conflict"
    FILE_MOVE_PATH_TOO_LONG = "file_move:path_too_long"
    FILE_MOVE_RESTORE_FAILED = "file_move:restore_failed"
    FILE_MOVE_COMPLETED = "file_move:completed"

    FILE_ROTATE_STARTED = "file_rotate:started"
    FILE_ROTATE_FILE_NOT_FOUND = "file_rotate:file_not_found"
    FILE_ROTATE_NOT_IMAGE = "file_rotate:not_image"
    FILE_ROTATE_PARENT_WRITE_PROTECTED = "file_rotate:parent_write_protected"
    FILE_ROTATE_INCONSISTENT = "file_rotate:inconsistent"
    FILE_ROTATE_UNSUPPORTED_IMAGE = "file_rotate:unsupported_image"
    FILE_ROTATE_RESTORE_FAILED = "file_rotate:restore_failed"
    FILE_ROTATE_THUMBNAIL_FAILED = "file_rotate:thumbnail_failed"
    FILE_ROTATE_CLEANUP_COMPLETED = "file_rotate:cleanup_completed"
    FILE_ROTATE_CLEANUP_FAILED = "file_rotate:cleanup_failed"
    FILE_ROTATE_COMPLETED = "file_rotate:completed"

    FILE_FLIP_STARTED = "file_flip:started"
    FILE_FLIP_FILE_NOT_FOUND = "file_flip:file_not_found"
    FILE_FLIP_NOT_IMAGE = "file_flip:not_image"
    FILE_FLIP_PARENT_WRITE_PROTECTED = "file_flip:parent_write_protected"
    FILE_FLIP_INCONSISTENT = "file_flip:inconsistent"
    FILE_FLIP_UNSUPPORTED_IMAGE = "file_flip:unsupported_image"
    FILE_FLIP_RESTORE_FAILED = "file_flip:restore_failed"
    FILE_FLIP_THUMBNAIL_FAILED = "file_flip:thumbnail_failed"
    FILE_FLIP_CLEANUP_COMPLETED = "file_flip:cleanup_completed"
    FILE_FLIP_CLEANUP_FAILED = "file_flip:cleanup_failed"
    FILE_FLIP_COMPLETED = "file_flip:completed"

    FILE_EDIT_STARTED = "file_edit:started"
    FILE_EDIT_FILE_NOT_FOUND = "file_edit:file_not_found"
    FILE_EDIT_NOT_TEXT = "file_edit:not_text"
    FILE_EDIT_PARENT_WRITE_PROTECTED = "file_edit:parent_write_protected"
    FILE_EDIT_INCONSISTENT = "file_edit:inconsistent"
    FILE_EDIT_WRITE_FAILED = "file_edit:write_failed"
    FILE_EDIT_RESTORE_FAILED = "file_edit:restore_failed"
    FILE_EDIT_CLEANUP_COMPLETED = "file_edit:cleanup_completed"
    FILE_EDIT_CLEANUP_FAILED = "file_edit:cleanup_failed"
    FILE_EDIT_COMPLETED = "file_edit:completed"

    FILE_DELETE_STARTED = "file_delete:started"
    FILE_DELETE_NOT_FOUND = "file_delete:not_found"
    FILE_DELETE_PARENT_WRITE_PROTECTED = "file_delete:parent_write_protected"
    FILE_DELETE_RESTORE_FAILED = "file_delete:restore_failed"
    FILE_DELETE_CLEANUP_TMP_FAILED = "file_delete:cleanup_tmp_failed"
    FILE_DELETE_CLEANUP_THUMBNAIL_FAILED = "file_delete:cleanup_thumbnail_failed"  # noqa: E501
    FILE_DELETE_CLEANUP_REVISION_FAILED = "file_delete:cleanup_revision_failed"
    FILE_DELETE_COMPLETED = "file_delete:completed"

    FILE_THUMBNAIL_RETRIEVE_STARTED = "file_thumbnail_retrieve:started"
    FILE_THUMBNAIL_RETRIEVE_NOT_FOUND = "file_thumbnail_retrieve:not_found"
    FILE_THUMBNAIL_RETRIEVE_COMPLETED = "file_thumbnail_retrieve:completed"

    FILE_LIST_STARTED = "file_list:started"
    FILE_LIST_FOLDER_NOT_FOUND = "file_list:folder_not_found"
    FILE_LIST_COMPLETED = "file_list:completed"

    TAG_ADD_STARTED = "tag_add:started"
    TAG_ADD_FILE_NOT_FOUND = "tag_add:file_not_found"
    TAG_ADD_PARENT_WRITE_PROTECTED = "tag_add:parent_write_protected"
    TAG_ADD_COMPLETED = "tag_add:completed"

    TAG_DELETE_STARTED = "tag_delete:started"
    TAG_DELETE_FILE_NOT_FOUND = "tag_delete:file_not_found"
    TAG_DELETE_PARENT_WRITE_PROTECTED = "tag_delete:parent_write_protected"
    TAG_DELETE_COMPLETED = "tag_delete:completed"

    TAG_LIST_STARTED = "tag_list:started"
    TAG_LIST_COMPLETED = "tag_list:completed"

    COMMENT_CREATE_STARTED = "comment_create:started"
    COMMENT_CREATE_FILE_NOT_FOUND = "comment_create:file_not_found"
    COMMENT_CREATE_PARENT_WRITE_PROTECTED = "comment_create:parent_write_protected"  # noqa: E501
    COMMENT_CREATE_COMPLETED = "comment_create:completed"

    COMMENT_UPDATE_STARTED = "comment_update:started"
    COMMENT_UPDATE_COMMENT_NOT_FOUND = "comment_update:comment_not_found"
    COMMENT_UPDATE_FORBIDDEN = "comment_update:forbidden"
    COMMENT_UPDATE_PARENT_WRITE_PROTECTED = "comment_update:parent_write_protected"  # noqa: E501
    COMMENT_UPDATE_COMPLETED = "comment_update:completed"

    COMMENT_DELETE_STARTED = "comment_delete:started"
    COMMENT_DELETE_COMMENT_NOT_FOUND = "comment_delete:comment_not_found"
    COMMENT_DELETE_FORBIDDEN = "comment_delete:forbidden"
    COMMENT_DELETE_PARENT_WRITE_PROTECTED = "comment_delete:parent_write_protected"  # noqa: E501
    COMMENT_DELETE_COMPLETED = "comment_delete:completed"

    VARIABLE_SET_STARTED = "variable_set:started"
    VARIABLE_SET_INSERT_CONFLICT = "variable_set:insert_conflict"
    VARIABLE_SET_UPDATE_CONFLICT = "variable_set:update_conflict"
    VARIABLE_SET_COMPLETED = "variable_set:completed"

    VARIABLE_GET_STARTED = "variable_get:started"
    VARIABLE_GET_VARIABLE_NOT_FOUND = "variable_get:variable_not_found"
    VARIABLE_GET_COMPLETED = "variable_get:completed"

    VARIABLE_DELETE_STARTED = "variable_delete:started"
    VARIABLE_DELETE_VARIABLE_NOT_FOUND = "variable_delete:variable_not_found"
    VARIABLE_DELETE_COMPLETED = "variable_delete:completed"

    VARIABLE_LIST_STARTED = "variable_list:started"
    VARIABLE_LIST_COMPLETED = "variable_list:completed"

    AUTH_STARTED = "auth:started"
    AUTH_TOKEN_MISSING = "auth:token_missing"
    AUTH_TOKEN_INVALID = "auth:token_invalid"
    AUTH_TOKEN_JTI_MISSING = "auth:token_jti_missing"
    AUTH_TOKEN_JTI_MISMATCH = "auth:token_jti_mismatch"
    AUTH_USER_ID_MISSING = "auth:user_id_missing"
    AUTH_USER_ID_INVALID = "auth:user_id_invalid"
    AUTH_USER_NOT_FOUND = "auth:user_not_found"
    AUTH_USER_JTI_MISSING = "auth:user_jti_missing"
    AUTH_USER_JTI_INVALID = "auth:user_jti_invalid"
    AUTH_USER_INACTIVE = "auth:user_inactive"
    AUTH_USER_SUSPENDED = "auth:user_suspended"
    AUTH_USER_ROLE_INSUFFICIENT = "auth:user_role_insufficient"
    AUTH_COMPLETED = "auth:completed"

    AUDIT_LIST_STARTED = "audit_list:started"
    AUDIT_LIST_COMPLETED = "audit_list:completed"
