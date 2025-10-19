# app.addons package

## app.addons.example_addon module

Example addon for handling hook functions triggered by corresponding
events within the app. Each function is associated with a specific event
and is designed to be executed when that event occurs. Functions may
include additional logic such as event logging, updating the database,
managing the cache, performing file or network operations, interacting
with third-party apps, and other actions.

### *async* app.addons.example_addon.after_file_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file_id: int)

Executes after a file is deleted.

### *async* app.addons.example_addon.after_file_download(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File), revision_number: int)

Executes after a file is downloaded.

### *async* app.addons.example_addon.after_file_list(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), files: List[[File](app.models.md#app.models.file.File)], files_count: int)

Executes after a file list is retrieved.

### *async* app.addons.example_addon.after_file_select(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File))

Executes after a file is retrieved.

### *async* app.addons.example_addon.after_file_update(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File))

Executes after a file is updated.

### *async* app.addons.example_addon.after_file_upload(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File))

Executes after a file is uploaded.

### *async* app.addons.example_addon.after_folder_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), folder_id: int)

Executes after a folder is deleted.

### *async* app.addons.example_addon.after_folder_insert(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), folder: [Folder](app.models.md#app.models.folder.Folder))

Executes after a folder is created.

### *async* app.addons.example_addon.after_folder_list(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), folders: List[[Folder](app.models.md#app.models.folder.Folder)], folders_count: int)

Executes after a folder list is retrieved.

### *async* app.addons.example_addon.after_folder_select(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), folder: [Folder](app.models.md#app.models.folder.Folder))

Executes after a folder is retrieved.

### *async* app.addons.example_addon.after_folder_update(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), folder: [Folder](app.models.md#app.models.folder.Folder))

Executes after a folder is updated.

### *async* app.addons.example_addon.after_tag_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File), tag_value: str)

Executes after a tag is deleted.

### *async* app.addons.example_addon.after_tag_insert(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File), tag_value: str)

Executes after a file tag is added.

### *async* app.addons.example_addon.after_telemetry_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), telemetry: dict)

Executes after telemetry is retrieved.

### *async* app.addons.example_addon.after_thumbnail_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), file: [File](app.models.md#app.models.file.File))

Executes after a file thumbnail is retrieved.

### *async* app.addons.example_addon.after_token_invalidate(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a token is invalidated (logout).

### *async* app.addons.example_addon.after_token_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a token is retrieved (issued).

### *async* app.addons.example_addon.after_user_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), user: [User](app.models.md#app.models.user.User))

Executes after a user is deleted.

### *async* app.addons.example_addon.after_user_list(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), users: List[[User](app.models.md#app.models.user.User)], users_count: int)

Executes after a list of users is retrieved.

### *async* app.addons.example_addon.after_user_login(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a user logs in.

### *async* app.addons.example_addon.after_user_password(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a user password is changed.

### *async* app.addons.example_addon.after_user_register(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a user is registered.

### *async* app.addons.example_addon.after_user_role(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), user: [User](app.models.md#app.models.user.User))

Executes after a user role or active status is changed.

### *async* app.addons.example_addon.after_user_select(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), user: [User](app.models.md#app.models.user.User))

Executes after a user is retrieved.

### *async* app.addons.example_addon.after_user_update(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a user is updated.

### *async* app.addons.example_addon.after_userpic_delete(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a userpic is deleted.

### *async* app.addons.example_addon.after_userpic_retrieve(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User), user: [User](app.models.md#app.models.user.User))

Executes after a userpic is retrieved.

### *async* app.addons.example_addon.after_userpic_upload(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Executes after a userpic is uploaded.

## Module contents
