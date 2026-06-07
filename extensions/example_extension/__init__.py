# app/extensions/example_extension/__init__.py
# SPDX-License-Identifier: SSPL-1.0

from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.events import Events as E

if TYPE_CHECKING:
    from app.models.file import File
    from app.models.file_comment import FileComment
    from app.models.file_tag import FileTag
    from app.models.file_thumbnail import FileThumbnail
    from app.models.folder import Folder
    from app.models.user import User
    from app.models.variable import Variable


# NOTE (ADR-68): Extensions avoid module-level imports of app models.
# Such imports during unittest discovery trigger config initialization
# and fail when env is not set. Use TYPE_CHECKING to keep annotations
# without runtime side effects.

async def mount_cipherdir(session: None, user: None):
    ...


async def unmount_cipherdir(session: None, user: None):
    ...


async def change_cipherdir_password(session: None, user: None):
    ...


async def enable_lockdown(session: None, user: None):
    ...


async def disable_lockdown(session: None, user: None):
    ...


async def register_user(session: AsyncSession, user: User):
    ...


async def login_user(session: AsyncSession, user: User):
    ...


async def issue_token(session: AsyncSession, user: User):
    ...


async def invalidate_token(session: AsyncSession, user: User):
    ...


async def recover_totp(session: AsyncSession, user: User):
    ...


async def select_user(session: AsyncSession, user: User):
    ...


async def update_user(session: AsyncSession, user: User):
    ...


async def change_user_password(session: AsyncSession, user: User):
    ...


async def rotate_user_recovery_code(session: AsyncSession, user: User):
    ...


async def change_user_role(session: AsyncSession, user: User):
    ...


async def list_users(session: AsyncSession, users: List[User]):
    ...


async def create_folder(session: AsyncSession, folder: Folder):
    ...


async def select_folder(session: AsyncSession, folder: Folder):
    ...


async def update_folder(session: AsyncSession, folder: Folder):
    ...


async def delete_folder(session: AsyncSession, folder: Folder):
    ...


async def protect_folder(session: AsyncSession, folder: Folder):
    ...


async def list_folders(session: AsyncSession, folders: List[Folder]):
    ...


async def upload_file(session: AsyncSession, file: File):
    ...


async def download_file(session: AsyncSession, file: File):
    ...


async def select_file(session: AsyncSession, file: File):
    ...


async def update_file(session: AsyncSession, file: File):
    ...


async def star_file(session: AsyncSession, file: File):
    ...


async def delete_file(session: AsyncSession, file: File):
    ...


async def move_file(session: AsyncSession, file: File):
    ...


async def rotate_file(session: AsyncSession, file: File):
    ...


async def flip_file(session: AsyncSession, file: File):
    ...


async def edit_file(session: AsyncSession, file: File):
    ...


async def list_files(session: AsyncSession, files: List[File]):
    ...


async def retrieve_thumbnail(session: AsyncSession, thumbnail: FileThumbnail):
    ...


async def add_tag(session: AsyncSession, tag: FileTag):
    ...


async def delete_tag(session: AsyncSession, tag: FileTag):
    ...


async def list_tags(session: AsyncSession, tags: list):
    ...


async def create_comment(session: AsyncSession, comment: FileComment):
    ...


async def update_comment(session: AsyncSession, comment: FileComment):
    ...


async def delete_comment(session: AsyncSession, comment: FileComment):
    ...


async def set_variable(session: AsyncSession, variable: Variable):
    ...


async def get_variable(session: AsyncSession, variable: Variable):
    ...


async def delete_variable(session: AsyncSession, variable: Variable):
    ...


async def list_variables(session: AsyncSession, variables: List[Variable]):
    ...


def register(manager):
    manager.on(E.CIPHERDIR_MOUNT_COMPLETED, mount_cipherdir)
    manager.on(E.CIPHERDIR_UNMOUNT_COMPLETED, unmount_cipherdir)
    manager.on(E.CIPHERDIR_PASSWORD_CHANGE_COMPLETED, change_cipherdir_password)  # noqa: E501
    manager.on(E.LOCKDOWN_ENABLE_COMPLETED, enable_lockdown)
    manager.on(E.LOCKDOWN_DISABLE_COMPLETED, disable_lockdown)
    manager.on(E.USER_REGISTER_COMPLETED, register_user)
    manager.on(E.USER_LOGIN_COMPLETED, login_user)
    manager.on(E.USER_TOKEN_ISSUE_COMPLETED, issue_token)
    manager.on(E.USER_TOKEN_INVALIDATE_COMPLETED, invalidate_token)
    manager.on(E.USER_TOTP_RECOVER_COMPLETED, recover_totp)
    manager.on(E.USER_SELECT_COMPLETED, select_user)
    manager.on(E.USER_UPDATE_COMPLETED, update_user)
    manager.on(E.USER_PASSWORD_CHANGE_COMPLETED, change_user_password)
    manager.on(E.USER_RECOVERY_CODE_ROTATE_COMPLETED, rotate_user_recovery_code)  # noqa: E501
    manager.on(E.USER_ROLE_CHANGE_COMPLETED, change_user_role)
    manager.on(E.USER_LIST_COMPLETED, list_users)
    manager.on(E.FOLDER_CREATE_COMPLETED, create_folder)
    manager.on(E.FOLDER_SELECT_COMPLETED, select_folder)
    manager.on(E.FOLDER_UPDATE_COMPLETED, update_folder)
    manager.on(E.FOLDER_DELETE_COMPLETED, delete_folder)
    manager.on(E.FOLDER_LIST_COMPLETED, list_folders)
    manager.on(E.FOLDER_WRITE_PROTECT_COMPLETED, protect_folder)
    manager.on(E.FILE_UPLOAD_COMPLETED, upload_file)
    manager.on(E.FILE_DOWNLOAD_COMPLETED, download_file)
    manager.on(E.FILE_SELECT_COMPLETED, select_file)
    manager.on(E.FILE_UPDATE_COMPLETED, update_file)
    manager.on(E.FILE_STARRED_CHANGE_COMPLETED, star_file)
    manager.on(E.FILE_MOVE_COMPLETED, move_file)
    manager.on(E.FILE_ROTATE_COMPLETED, rotate_file)
    manager.on(E.FILE_FLIP_COMPLETED, flip_file)
    manager.on(E.FILE_EDIT_COMPLETED, edit_file)
    manager.on(E.FILE_DELETE_COMPLETED, delete_file)
    manager.on(E.FILE_LIST_COMPLETED, list_files)
    manager.on(E.FILE_THUMBNAIL_RETRIEVE_COMPLETED, retrieve_thumbnail)
    manager.on(E.TAG_ADD_COMPLETED, add_tag)
    manager.on(E.TAG_DELETE_COMPLETED, delete_tag)
    manager.on(E.TAG_LIST_COMPLETED, list_tags)
    manager.on(E.COMMENT_CREATE_COMPLETED, create_comment)
    manager.on(E.COMMENT_UPDATE_COMPLETED, update_comment)
    manager.on(E.COMMENT_DELETE_COMPLETED, delete_comment)
    manager.on(E.VARIABLE_SET_COMPLETED, set_variable)
    manager.on(E.VARIABLE_GET_COMPLETED, get_variable)
    manager.on(E.VARIABLE_DELETE_COMPLETED, delete_variable)
    manager.on(E.VARIABLE_LIST_COMPLETED, list_variables)
