# app.schemas package

## app.schemas.file_delete module

Pydantic schemas for file deletion.

### *class* app.schemas.file_delete.FileDeleteResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for file deletion. Contains the deleted file ID
and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.file_list module

Pydantic schemas for listing files.

### *class* app.schemas.file_list.FileListRequest(, created_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, created_date_\_le: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_le: Annotated[int | None, Ge(ge=0)] = None, user_id_\_eq: Annotated[int | None, Ge(ge=1)] = None, folder_id_\_eq: Annotated[int | None, Ge(ge=1)] = None, flagged_\_eq: bool | None = None, filename_\_ilike: str | None = None, filesize_\_ge: Annotated[int | None, Ge(ge=0)] = None, filesize_\_le: Annotated[int | None, Ge(ge=0)] = None, mimetype_\_ilike: str | None = None, tag_value_\_eq: str | None = None, offset: Annotated[int, Ge(ge=0)] = 0, limit: Annotated[int, Ge(ge=1), Le(le=500)] = 50, order_by: Literal['id', 'created_date', 'updated_date', 'user_id', 'folder_id', 'flagged', 'filename', 'filesize', 'mimetype'] = 'id', order: Literal['asc', 'desc', 'rand'] = 'desc')

Bases: `BaseModel`

Request schema for listing files. Allows filtering by creator,
folder, filename/mimetype (case-insensitive), flagged status,
creation and update time ranges, filesize range, MIME type, tag
value. Supports pagination via offset/limit. Results can be ordered
by id, created/updated date, creator, folder, flagged, filename,
filesize, or mimetype, in ascending, descending, or random order.
Extra fields are forbidden.

#### created_date_\_ge *: int | None*

#### created_date_\_le *: int | None*

#### filename_\_ilike *: str | None*

#### filesize_\_ge *: int | None*

#### filesize_\_le *: int | None*

#### flagged_\_eq *: bool | None*

#### folder_id_\_eq *: int | None*

#### limit *: int*

#### mimetype_\_ilike *: str | None*

#### model_config *: ClassVar[ConfigDict]* *= {'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### offset *: int*

#### order *: Literal['asc', 'desc', 'rand']*

#### order_by *: Literal['id', 'created_date', 'updated_date', 'user_id', 'folder_id', 'flagged', 'filename', 'filesize', 'mimetype']*

#### tag_value_\_eq *: str | None*

#### updated_date_\_ge *: int | None*

#### updated_date_\_le *: int | None*

#### user_id_\_eq *: int | None*

### *class* app.schemas.file_list.FileListResponse(, files: List[[FileSelectResponse](#app.schemas.file_select.FileSelectResponse)], files_count: int)

Bases: `BaseModel`

Response schema for listing files. Contains the selected page
of files and the total number of matches before pagination.

#### files *: List[[FileSelectResponse](#app.schemas.file_select.FileSelectResponse)]*

#### files_count *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.file_select module

Pydantic schemas for file detail retrieval.

### *class* app.schemas.file_select.FileSelectResponse(, id: int, user: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse), folder: [FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse), created_date: int, updated_date: int, flagged: bool, filename: str, filesize: int, mimetype: str | None = None, checksum: str, summary: str | None = None, latest_revision_number: int, file_revisions: List[[RevisionSelectResponse](#app.schemas.revision_select.RevisionSelectResponse)], file_tags: list = None)

Bases: `BaseModel`

Response schema for file details. Includes identifiers, creator,
parent folder, creation/update timestamps, flagged status, filename,
filesize, mimetype, checksum, optional summary, latest revision
number, and a list of file revisions.

#### checksum *: str*

#### created_date *: int*

#### file_revisions *: List[[RevisionSelectResponse](#app.schemas.revision_select.RevisionSelectResponse)]*

#### file_tags *: list*

#### filename *: str*

#### filesize *: int*

#### flagged *: bool*

#### folder *: [FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)*

#### id *: int*

#### latest_revision_number *: int*

#### mimetype *: str | None*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### summary *: str | None*

#### updated_date *: int*

#### user *: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)*

## app.schemas.file_update module

Pydantic schemas for file update.

### *class* app.schemas.file_update.FileUpdateRequest(, folder_id: Annotated[int, Ge(ge=1)], filename: Annotated[str, MinLen(min_length=1), MaxLen(max_length=255)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for updating a file. Includes the required filename
and folder ID, plus an optional summary. Whitespace is stripped from
strings; extra fields are forbidden.

#### filename *: str*

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### summary *: str | None*

### *class* app.schemas.file_update.FileUpdateResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for file update. Contains the updated
file ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.file_upload module

Pydantic schemas for file upload.

### *class* app.schemas.file_upload.FileUploadResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for file upload. Contains the created file
ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.folder_delete module

Pydantic schemas for folder deletion.

### *class* app.schemas.folder_delete.FolderDeleteResponse(, folder_id: int)

Bases: `BaseModel`

Response schema for folder deletion. Contains the deleted
folder ID.

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.folder_insert module

Pydantic schemas for folder insertion.

### *class* app.schemas.folder_insert.FolderInsertRequest(, readonly: bool, name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=255)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for folder insertion. Includes the read-only
flag, folder name, and an optional summary. Whitespace is
stripped from strings; extra fields are forbidden.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name *: str*

#### readonly *: bool*

#### summary *: str | None*

### *class* app.schemas.folder_insert.FolderInsertResponse(, folder_id: int)

Bases: `BaseModel`

Response schema for folder insertion. Contains the created
folder ID.

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.folder_list module

Pydantic schemas for listing folders.

### *class* app.schemas.folder_list.FolderListRequest(, user_id_\_eq: Annotated[int | None, Ge(ge=1)] = None, created_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, created_date_\_le: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, updated_date_\_le: Annotated[int | None, Ge(ge=0)] = None, readonly_\_eq: bool | None = None, name_\_ilike: str | None = None, offset: Annotated[int, Ge(ge=0)] = 0, limit: Annotated[int, Ge(ge=1), Le(le=500)] = 50, order_by: Literal['id', 'created_date', 'updated_date', 'user_id', 'readonly', 'name'] = 'id', order: Literal['asc', 'desc', 'rand'] = 'desc')

Bases: `BaseModel`

Request schema for listing folders. Allows filtering by creator,
name (case-insensitive), read-only status, and creation/update time
ranges. Supports pagination via offset/limit. Results can be ordered
by id, created/updated date, creator, read-only flag, name, or
filesize, in ascending, descending, or random order. Extra fields
are forbidden.

#### created_date_\_ge *: int | None*

#### created_date_\_le *: int | None*

#### limit *: int*

#### model_config *: ClassVar[ConfigDict]* *= {'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name_\_ilike *: str | None*

#### offset *: int*

#### order *: Literal['asc', 'desc', 'rand']*

#### order_by *: Literal['id', 'created_date', 'updated_date', 'user_id', 'readonly', 'name']*

#### readonly_\_eq *: bool | None*

#### updated_date_\_ge *: int | None*

#### updated_date_\_le *: int | None*

#### user_id_\_eq *: int | None*

### *class* app.schemas.folder_list.FolderListResponse(, folders: List[[FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)], folders_count: int)

Bases: `BaseModel`

Response schema for listing folders. Contains the selected page
of folders and the total number of matches before pagination.

#### folders *: List[[FolderSelectResponse](#app.schemas.folder_select.FolderSelectResponse)]*

#### folders_count *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.folder_select module

Pydantic schemas for folder detail retrieval.

### *class* app.schemas.folder_select.FolderSelectResponse(, id: int, created_date: int, updated_date: int, readonly: bool, name: str, summary: str | None = None, user: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse))

Bases: `BaseModel`

Response schema for folder detail retrieval. Includes the
folder ID; creation and last-update timestamps (Unix seconds,
UTC); read-only flag; folder name; optional summary; and
creator details.

#### created_date *: int*

#### id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name *: str*

#### readonly *: bool*

#### summary *: str | None*

#### updated_date *: int*

#### user *: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)*

## app.schemas.folder_update module

Pydantic schemas for folder update.

### *class* app.schemas.folder_update.FolderUpdateRequest(, readonly: bool, name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=255)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for updating a folder. Includes the read-only
flag, folder name, and an optional summary. Whitespace is
stripped from strings; extra fields are forbidden.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### name *: str*

#### readonly *: bool*

#### summary *: str | None*

### *class* app.schemas.folder_update.FolderUpdateResponse(, folder_id: int)

Bases: `BaseModel`

Response schema for folder update. Contains the updated folder ID.

#### folder_id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.revision_select module

Pydantic schemas for revision detail retrieval.

### *class* app.schemas.revision_select.RevisionSelectResponse(, id: int, user: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse), file_id: int, created_date: int, revision_number: int, uuid: str, filesize: int, checksum: str)

Bases: `BaseModel`

Response schema for revision retrieval. Includes the revision ID;
creator data; parent file ID; creation timestamp (Unix seconds,
UTC); revision number; UUID (revision file name); its file size;
and content checksum.

#### checksum *: str*

#### created_date *: int*

#### file_id *: int*

#### filesize *: int*

#### id *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### revision_number *: int*

#### user *: [UserSelectResponse](#app.schemas.user_select.UserSelectResponse)*

#### uuid *: str*

## app.schemas.tag_delete module

Pydantic schemas for tag deletion.

### *class* app.schemas.tag_delete.TagDeleteResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for tag delete. Contains the related
file ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.tag_insert module

Pydantic schemas for file tag insertion.

### *class* app.schemas.tag_insert.TagInsertRequest(, value: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)])

Bases: `BaseModel`

Request schema for creating a new file tag. The tag value
is validated and cleaned before being processed.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### *classmethod* validate_value(value: str) → str

Validate and normalize tag value.

#### value *: str*

### *class* app.schemas.tag_insert.TagInsertResponse(, file_id: int, latest_revision_number: int)

Bases: `BaseModel`

Response schema for tag insert. Contains the related
file ID and the latest revision number.

#### file_id *: int*

#### latest_revision_number *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

## app.schemas.telemetry_retrieve module

Pydantic schemas for telemetry retrieve.

### *class* app.schemas.telemetry_retrieve.TelemetryRetrieveResponse(, app_version: str, unix_timestamp: int, timezone_name: str, timezone_offset: int, sqlite_version: str, sqlite_size: int, redis_version: str, redis_memory: int, platform_alias: str, platform_architecture: str, platform_processor: str, python_compiler: str, python_implementation: str, python_version: str, os_name: str, os_release: str, os_version: str, disk_total: int, disk_used: int, disk_free: int, memory_total: int, memory_used: int, memory_free: int, cpu_core_count: int, cpu_frequency: int, cpu_usage_percent: float)

Bases: `BaseModel`

Response schema for retrieving telemetry data. Contains information
operating system, database, cache, platform, Python environment,
and resource usage metrics.

#### app_version *: str*

#### cpu_core_count *: int*

#### cpu_frequency *: int*

#### cpu_usage_percent *: float*

#### disk_free *: int*

#### disk_total *: int*

#### disk_used *: int*

#### memory_free *: int*

#### memory_total *: int*

#### memory_used *: int*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### os_name *: str*

#### os_release *: str*

#### os_version *: str*

#### platform_alias *: str*

#### platform_architecture *: str*

#### platform_processor *: str*

#### python_compiler *: str*

#### python_implementation *: str*

#### python_version *: str*

#### redis_memory *: int*

#### redis_version *: str*

#### sqlite_size *: int*

#### sqlite_version *: str*

#### timezone_name *: str*

#### timezone_offset *: int*

#### unix_timestamp *: int*

## app.schemas.token_invalidate module

Pydantic schemas for token invalidation.

### *class* app.schemas.token_invalidate.TokenInvalidateResponse(, user_id: int)

Bases: `BaseModel`

Response schema for token invalidation. Confirms that the token
was invalidated for the specified user by returning the user’s
unique identifier.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.token_retrieve module

Pydantic schemas for token retrieval.

### *class* app.schemas.token_retrieve.TokenRetrieveRequest(, username: str, totp: Annotated[str, MinLen(min_length=6), MaxLen(max_length=6)], exp: Annotated[int | None, Ge(ge=1)] = None)

Bases: `BaseModel`

Request schema for token retrieval. Includes the username,
a time-based one-time password (TOTP), and an optional token
lifetime exp — absolute expiration timestamp in Unix seconds;
if omitted, the token is issued without an exp claim (non-expiring).
Extra fields are forbidden.

#### exp *: int | None*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### totp *: str*

#### username *: str*

### *class* app.schemas.token_retrieve.TokenRetrieveResponse(, user_id: int, user_token: str)

Bases: `BaseModel`

Response schema for token retrieval. Returns the user ID and
a signed JWT access token for authenticated requests.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

#### user_token *: str*

## app.schemas.user_delete module

Pydantic schemas for user deletion.

### *class* app.schemas.user_delete.UserDeleteResponse(, user_id: int)

Bases: `BaseModel`

Response schema for user deletion. Contains the deleted user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.user_list module

Pydantic schemas for listing users.

### *class* app.schemas.user_list.UserListRequest(, created_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, created_date_\_le: Annotated[int | None, Ge(ge=0)] = None, last_login_date_\_ge: Annotated[int | None, Ge(ge=0)] = None, last_login_date_\_le: Annotated[int | None, Ge(ge=0)] = None, active_\_eq: bool | None = None, role_\_eq: Literal['reader', 'writer', 'editor', 'admin'] | None = None, username_\_ilike: str | None = None, first_name_\_ilike: str | None = None, last_name_\_ilike: str | None = None, full_name_\_ilike: str | None = None, offset: Annotated[int, Ge(ge=0)] = 0, limit: Annotated[int, Ge(ge=1), Le(le=500)] = 50, order_by: Literal['id', 'created_date', 'last_login_date', 'role', 'active', 'username', 'first_name', 'last_name', 'full_name'] = 'id', order: Literal['asc', 'desc', 'rand'] = 'desc')

Bases: `BaseModel`

Request schema for listing users. Allows filtering by activity
status and role; by username (case-insensitive); by name fields:
first_name, last_name, full_name (case-insensitive); and by
creation/last-login time ranges. Supports pagination via
offset/limit. Results can be ordered by id, created_date,
last_login_date, role, active, username, first_name, last_name,
or full_name in ascending, descending, or random order.

#### active_\_eq *: bool | None*

#### created_date_\_ge *: int | None*

#### created_date_\_le *: int | None*

#### first_name_\_ilike *: str | None*

#### full_name_\_ilike *: str | None*

#### last_login_date_\_ge *: int | None*

#### last_login_date_\_le *: int | None*

#### last_name_\_ilike *: str | None*

#### limit *: int*

#### model_config *: ClassVar[ConfigDict]* *= {'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### offset *: int*

#### order *: Literal['asc', 'desc', 'rand']*

#### order_by *: Literal['id', 'created_date', 'last_login_date', 'role', 'active', 'username', 'first_name', 'last_name', 'full_name']*

#### role_\_eq *: Literal['reader', 'writer', 'editor', 'admin'] | None*

#### username_\_ilike *: str | None*

### *class* app.schemas.user_list.UserListResponse(, users: List[[UserSelectResponse](#app.schemas.user_select.UserSelectResponse)], users_count: int)

Bases: `BaseModel`

Response schema for listing users. Contains the selected page
of users and the total number of matches before pagination.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### users *: List[[UserSelectResponse](#app.schemas.user_select.UserSelectResponse)]*

#### users_count *: int*

## app.schemas.user_login module

Pydantic schemas for user login.

### *class* app.schemas.user_login.UserLoginRequest(, username: str, password: SecretStr)

Bases: `BaseModel`

Request schema for user login. Carries the username and password
used to authenticate the account; the username is trimmed and
lowercased (Latin letters, digits, underscore). Extra fields
are forbidden.

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### password *: SecretStr*

#### username *: str*

### *class* app.schemas.user_login.UserLoginResponse(, user_id: int, password_accepted: bool)

Bases: `BaseModel`

Response schema for user login. Returns the user ID and a flag
indicating that the password step was accepted and the flow may
proceed to MFA.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### password_accepted *: bool*

#### user_id *: int*

## app.schemas.user_password module

Pydantic schemas for password change.

### *class* app.schemas.user_password.UserPasswordRequest(, current_password: Annotated[str, MinLen(min_length=6)], updated_password: Annotated[str, MinLen(min_length=6)])

Bases: `BaseModel`

Request schema for changing a user’s password. Requires the current
password and a new password. Whitespace is stripped from strings;
extra fields are forbidden.

#### current_password *: str*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### updated_password *: str*

### *class* app.schemas.user_password.UserPasswordResponse(, user_id: int)

Bases: `BaseModel`

Response schema for password change. Contains the user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.user_register module

Pydantic schemas for user registration.

### *class* app.schemas.user_register.UserRegisterRequest(, username: Annotated[str, MinLen(min_length=2), MaxLen(max_length=40)], password: Annotated[SecretStr, MinLen(min_length=6)], first_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], last_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for user registration request with validation
of username, password, names, and optional profile summary.
Extra fields are forbidden.

#### first_name *: str*

#### last_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### password *: SecretStr*

#### summary *: str | None*

#### username *: str*

### *class* app.schemas.user_register.UserRegisterResponse(, user_id: int, mfa_secret: str)

Bases: `BaseModel`

Response schema for user registration response including assigned
user ID and MFA secret string.

#### mfa_secret *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.user_role module

Pydantic schemas for user role update.

### *class* app.schemas.user_role.UserRoleRequest(, role: Literal['reader', 'writer', 'editor', 'admin'], active: bool)

Bases: `BaseModel`

Request schema for updating a user’s role and active status.
Includes the new role (reader|writer|editor|admin) and an activity
status. Whitespace is stripped from strings. Extra fields are
forbidden.

#### active *: bool*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### role *: Literal['reader', 'writer', 'editor', 'admin']*

#### *classmethod* validate_role(value: str) → str

### *class* app.schemas.user_role.UserRoleResponse(, user_id: int)

Bases: `BaseModel`

Response schema for user role update. Contains the user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.user_select module

Pydantic schemas for user detail retrieval.

### *class* app.schemas.user_select.UserSelectResponse(, id: int, created_date: int, last_login_date: int, role: Literal['reader', 'writer', 'editor', 'admin'], active: bool, username: str, first_name: str, last_name: str, summary: str | None = None, has_thumbnail: bool)

Bases: `BaseModel`

Response schema for user details. Includes identifiers, creation
and last-login timestamps, role, active status, username, first/last
name, optional summary, and thumbnail presence flag.

#### active *: bool*

#### created_date *: int*

#### first_name *: str*

#### has_thumbnail *: bool*

#### id *: int*

#### last_login_date *: int*

#### last_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### role *: Literal['reader', 'writer', 'editor', 'admin']*

#### summary *: str | None*

#### username *: str*

## app.schemas.user_update module

Pydantic schemas for user update.

### *class* app.schemas.user_update.UserUpdateRequest(, first_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], last_name: Annotated[str, MinLen(min_length=1), MaxLen(max_length=40)], summary: Annotated[str | None, MaxLen(max_length=4096)] = None)

Bases: `BaseModel`

Request schema for updating a user profile. Requires first and last
name; summary is optional. Whitespace is stripped from strings;
extra fields are forbidden.

#### first_name *: str*

#### last_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {'extra': 'forbid', 'str_strip_whitespace': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### summary *: str | None*

### *class* app.schemas.user_update.UserUpdateResponse(, user_id: int)

Bases: `BaseModel`

Response schema for user update. Contains the updated user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.userpic_delete module

Pydantic schemas for userpic deletion.

### *class* app.schemas.userpic_delete.UserpicDeleteResponse(, user_id: int)

Bases: `BaseModel`

Response schema for userpic deletion. Contains the user ID.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## app.schemas.userpic_upload module

Pydantic schemas for uploading a user’s image.

### *class* app.schemas.userpic_upload.UserpicUploadResponse(, user_id: int)

Bases: `BaseModel`

Response schema confirming a successful user image upload by
returning the unique identifier of the affected user account.

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### user_id *: int*

## Module contents
