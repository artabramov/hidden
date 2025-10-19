# app.models package

## app.models.file module

SQLAlchemy model for files.

### *class* app.models.file.File(user_id, folder_id, filename, filesize, checksum, mimetype=None, flagged=False, summary=None, latest_revision_number=0)

Bases: [`Base`](app.md#app.sqlite.Base)

#### checksum

#### created_date

#### file_folder

#### file_meta

#### file_revisions

#### file_tags

#### file_thumbnail

#### file_user

#### filename

#### filesize

#### flagged

#### folder_id

#### *property* has_revisions *: bool*

#### *property* has_thumbnail *: bool*

#### id

#### latest_revision_number

#### mimetype

#### path(config: Any) → str

Return absolute path to the file file by config.

#### *classmethod* path_for_filename(config: Any, folder_name: str, filename: str) → str

Return absolute path to the file file by parameters.

#### summary

#### *async* to_dict() → dict

Returns a dictionary representation of the file.

#### updated_date

#### user_id

## app.models.file_meta module

SQLAlchemy model for file metadata.

### *class* app.models.file_meta.FileMeta(\*\*kwargs)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for file metadata. Stores a key-value pair linked
to a file; keys are unique within each file.

#### created_date

#### file_id

#### id

#### meta_file

#### meta_key

#### meta_value

#### updated_date

## app.models.file_revision module

SQLAlchemy model for file revisions.

### *class* app.models.file_revision.FileRevision(user_id, file_id, revision_number, uuid, filesize, checksum)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for file revisions. Immutable snapshots of a file.

#### checksum

#### created_date

#### file_id

#### filesize

#### id

#### path(config: Any) → str

Return absolute path to the thumbnail file by its UUID.

#### *classmethod* path_for_uuid(config: Any, uuid: str) → str

Return absolute path for a given UUID using config.

#### revision_file

#### revision_number

#### revision_user

#### *async* to_dict() → dict

Returns a dictionary representation of the revision.

#### user_id

#### uuid

## app.models.file_tag module

SQLAlchemy model for file tags.

### *class* app.models.file_tag.FileTag(file_id, value)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for file tags. Stores a tag value linked
to a file; values are unique within each file.

#### created_date

#### file_id

#### id

#### tag_file

#### value

## app.models.file_thumbnail module

SQLAlchemy model for file thumbnails.

### *class* app.models.file_thumbnail.FileThumbnail(file_id, uuid, filesize, checksum)

Bases: [`Base`](app.md#app.sqlite.Base), [`ThumbnailMixin`](app.helpers.md#app.helpers.thumbnail_mixin.ThumbnailMixin)

SQLAlchemy model for file thumbnails. One-to-one thumbnail
linked to a file; stores UUID (thumbnail file name), file
size, and checksum.

#### checksum

#### created_date

#### file_id

#### filesize

#### id

#### thumbnail_file

#### updated_date

#### uuid

## app.models.folder module

SQLAlchemy model for folders.

### *class* app.models.folder.Folder(user_id, readonly, name, summary=None)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for folders. Stores a unique name, read-only
flag, creation/update timestamps, and optional summary.

#### created_date

#### folder_files

#### folder_meta

#### folder_user

#### id

#### name

#### path(config: Any) → str

Return absolute path to the folder by config.

#### *classmethod* path_for_dir(config: Any, folder_name: str) → str

Return absolute path to the folder by parameters.

#### readonly

#### summary

#### *async* to_dict() → dict

Returns a dictionary representation of the folder.

#### updated_date

#### user_id

## app.models.folder_meta module

SQLAlchemy model for folder metadata.

### *class* app.models.folder_meta.FolderMeta(\*\*kwargs)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for folder metadata. Stores a key-value pair
linked to a folder; keys are unique within each folder.

#### created_date

#### folder_id

#### id

#### meta_folder

#### meta_key

#### meta_value

#### updated_date

## app.models.user module

SQLAlchemy model for users.

### *class* app.models.user.User(username, password_hash, first_name, last_name, role, active, mfa_secret_encrypted, jti_encrypted, summary=None)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for users. Stores authentication credentials,
access role, status flags, audit timestamps, MFA fields, and
optional profile information.

#### active

#### *property* can_admin *: bool*

#### *property* can_edit *: bool*

#### *property* can_read *: bool*

#### *property* can_write *: bool*

#### created_date

#### first_name

#### full_name

#### *property* has_thumbnail *: bool*

#### id

#### jti_encrypted

#### last_login_date

#### last_name

#### mfa_attempts

#### mfa_secret_encrypted

#### password_accepted

#### password_attempts

#### password_hash

#### role

#### summary

#### suspended_until_date

#### *async* to_dict() → dict

Returns a dictionary representation of the user.

#### updated_date

#### user_files

#### user_folders

#### user_meta

#### user_revisions

#### user_thumbnail

#### username

### *class* app.models.user.UserRole

Bases: `object`

Defines the available user roles in the application.
Each role determines a predefined set of permissions.

#### admin *= 'admin'*

#### editor *= 'editor'*

#### reader *= 'reader'*

#### writer *= 'writer'*

## app.models.user_meta module

SQLAlchemy model for user metadata.

### *class* app.models.user_meta.UserMeta(\*\*kwargs)

Bases: [`Base`](app.md#app.sqlite.Base)

SQLAlchemy model for user metadata. Stores a key-value pair
linked to a user; keys are unique within each folder.

#### created_date

#### id

#### meta_key

#### meta_user

#### meta_value

#### updated_date

#### user_id

## app.models.user_thumbnail module

SQLAlchemy model for user thumbnails.

### *class* app.models.user_thumbnail.UserThumbnail(user_id, uuid, filesize, checksum)

Bases: [`Base`](app.md#app.sqlite.Base), [`ThumbnailMixin`](app.helpers.md#app.helpers.thumbnail_mixin.ThumbnailMixin)

SQLAlchemy model for user thumbnails. One-to-one thumbnail
linked to a user; stores its UUID, size, and checksum.

#### checksum

#### created_date

#### filesize

#### id

#### thumbnail_user

#### updated_date

#### user_id

#### uuid

## Module contents
