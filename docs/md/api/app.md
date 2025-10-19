# app package

## Subpackages

* [app.addons package](app.addons.md)
  * [app.addons.example_addon module](app.addons.md#module-app.addons.example_addon)
    * [`after_file_delete()`](app.addons.md#app.addons.example_addon.after_file_delete)
    * [`after_file_download()`](app.addons.md#app.addons.example_addon.after_file_download)
    * [`after_file_list()`](app.addons.md#app.addons.example_addon.after_file_list)
    * [`after_file_select()`](app.addons.md#app.addons.example_addon.after_file_select)
    * [`after_file_update()`](app.addons.md#app.addons.example_addon.after_file_update)
    * [`after_file_upload()`](app.addons.md#app.addons.example_addon.after_file_upload)
    * [`after_folder_delete()`](app.addons.md#app.addons.example_addon.after_folder_delete)
    * [`after_folder_insert()`](app.addons.md#app.addons.example_addon.after_folder_insert)
    * [`after_folder_list()`](app.addons.md#app.addons.example_addon.after_folder_list)
    * [`after_folder_select()`](app.addons.md#app.addons.example_addon.after_folder_select)
    * [`after_folder_update()`](app.addons.md#app.addons.example_addon.after_folder_update)
    * [`after_tag_delete()`](app.addons.md#app.addons.example_addon.after_tag_delete)
    * [`after_tag_insert()`](app.addons.md#app.addons.example_addon.after_tag_insert)
    * [`after_telemetry_retrieve()`](app.addons.md#app.addons.example_addon.after_telemetry_retrieve)
    * [`after_thumbnail_retrieve()`](app.addons.md#app.addons.example_addon.after_thumbnail_retrieve)
    * [`after_token_invalidate()`](app.addons.md#app.addons.example_addon.after_token_invalidate)
    * [`after_token_retrieve()`](app.addons.md#app.addons.example_addon.after_token_retrieve)
    * [`after_user_delete()`](app.addons.md#app.addons.example_addon.after_user_delete)
    * [`after_user_list()`](app.addons.md#app.addons.example_addon.after_user_list)
    * [`after_user_login()`](app.addons.md#app.addons.example_addon.after_user_login)
    * [`after_user_password()`](app.addons.md#app.addons.example_addon.after_user_password)
    * [`after_user_register()`](app.addons.md#app.addons.example_addon.after_user_register)
    * [`after_user_role()`](app.addons.md#app.addons.example_addon.after_user_role)
    * [`after_user_select()`](app.addons.md#app.addons.example_addon.after_user_select)
    * [`after_user_update()`](app.addons.md#app.addons.example_addon.after_user_update)
    * [`after_userpic_delete()`](app.addons.md#app.addons.example_addon.after_userpic_delete)
    * [`after_userpic_retrieve()`](app.addons.md#app.addons.example_addon.after_userpic_retrieve)
    * [`after_userpic_upload()`](app.addons.md#app.addons.example_addon.after_userpic_upload)
  * [Module contents](app.addons.md#module-app.addons)
* [app.helpers package](app.helpers.md)
  * [app.helpers.image_helper module](app.helpers.md#module-app.helpers.image_helper)
    * [`image_resize()`](app.helpers.md#app.helpers.image_helper.image_resize)
  * [app.helpers.jwt_helper module](app.helpers.md#module-app.helpers.jwt_helper)
    * [`create_payload()`](app.helpers.md#app.helpers.jwt_helper.create_payload)
    * [`decode_jwt()`](app.helpers.md#app.helpers.jwt_helper.decode_jwt)
    * [`encode_jwt()`](app.helpers.md#app.helpers.jwt_helper.encode_jwt)
    * [`generate_jti()`](app.helpers.md#app.helpers.jwt_helper.generate_jti)
  * [app.helpers.mfa_helper module](app.helpers.md#module-app.helpers.mfa_helper)
    * [`calculate_totp()`](app.helpers.md#app.helpers.mfa_helper.calculate_totp)
    * [`generate_mfa_secret()`](app.helpers.md#app.helpers.mfa_helper.generate_mfa_secret)
  * [app.helpers.thumbnail_mixin module](app.helpers.md#module-app.helpers.thumbnail_mixin)
    * [`ThumbnailMixin`](app.helpers.md#app.helpers.thumbnail_mixin.ThumbnailMixin)
      * [`ThumbnailMixin.path()`](app.helpers.md#app.helpers.thumbnail_mixin.ThumbnailMixin.path)
      * [`ThumbnailMixin.path_for_uuid()`](app.helpers.md#app.helpers.thumbnail_mixin.ThumbnailMixin.path_for_uuid)
  * [Module contents](app.helpers.md#module-app.helpers)
* [app.managers package](app.managers.md)
  * [app.managers.cache_manager module](app.managers.md#module-app.managers.cache_manager)
    * [`CacheManager`](app.managers.md#app.managers.cache_manager.CacheManager)
      * [`CacheManager.delete()`](app.managers.md#app.managers.cache_manager.CacheManager.delete)
      * [`CacheManager.delete_all()`](app.managers.md#app.managers.cache_manager.CacheManager.delete_all)
      * [`CacheManager.erase()`](app.managers.md#app.managers.cache_manager.CacheManager.erase)
      * [`CacheManager.get()`](app.managers.md#app.managers.cache_manager.CacheManager.get)
      * [`CacheManager.set()`](app.managers.md#app.managers.cache_manager.CacheManager.set)
  * [app.managers.encryption_manager module](app.managers.md#module-app.managers.encryption_manager)
    * [`EncryptionManager`](app.managers.md#app.managers.encryption_manager.EncryptionManager)
      * [`EncryptionManager.decrypt_bool()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.decrypt_bool)
      * [`EncryptionManager.decrypt_bytes()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.decrypt_bytes)
      * [`EncryptionManager.decrypt_int()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.decrypt_int)
      * [`EncryptionManager.decrypt_str()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.decrypt_str)
      * [`EncryptionManager.encrypt_bool()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.encrypt_bool)
      * [`EncryptionManager.encrypt_bytes()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.encrypt_bytes)
      * [`EncryptionManager.encrypt_int()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.encrypt_int)
      * [`EncryptionManager.encrypt_str()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.encrypt_str)
      * [`EncryptionManager.get_hash()`](app.managers.md#app.managers.encryption_manager.EncryptionManager.get_hash)
  * [app.managers.entity_manager module](app.managers.md#module-app.managers.entity_manager)
    * [`EntityManager`](app.managers.md#app.managers.entity_manager.EntityManager)
      * [`EntityManager.commit()`](app.managers.md#app.managers.entity_manager.EntityManager.commit)
      * [`EntityManager.count_all()`](app.managers.md#app.managers.entity_manager.EntityManager.count_all)
      * [`EntityManager.delete()`](app.managers.md#app.managers.entity_manager.EntityManager.delete)
      * [`EntityManager.delete_all()`](app.managers.md#app.managers.entity_manager.EntityManager.delete_all)
      * [`EntityManager.exists()`](app.managers.md#app.managers.entity_manager.EntityManager.exists)
      * [`EntityManager.flush()`](app.managers.md#app.managers.entity_manager.EntityManager.flush)
      * [`EntityManager.insert()`](app.managers.md#app.managers.entity_manager.EntityManager.insert)
      * [`EntityManager.rollback()`](app.managers.md#app.managers.entity_manager.EntityManager.rollback)
      * [`EntityManager.select()`](app.managers.md#app.managers.entity_manager.EntityManager.select)
      * [`EntityManager.select_all()`](app.managers.md#app.managers.entity_manager.EntityManager.select_all)
      * [`EntityManager.select_by()`](app.managers.md#app.managers.entity_manager.EntityManager.select_by)
      * [`EntityManager.select_rows()`](app.managers.md#app.managers.entity_manager.EntityManager.select_rows)
      * [`EntityManager.subquery()`](app.managers.md#app.managers.entity_manager.EntityManager.subquery)
      * [`EntityManager.sum_all()`](app.managers.md#app.managers.entity_manager.EntityManager.sum_all)
      * [`EntityManager.update()`](app.managers.md#app.managers.entity_manager.EntityManager.update)
  * [app.managers.file_manager module](app.managers.md#module-app.managers.file_manager)
    * [`FileManager`](app.managers.md#app.managers.file_manager.FileManager)
      * [`FileManager.checksum()`](app.managers.md#app.managers.file_manager.FileManager.checksum)
      * [`FileManager.copy()`](app.managers.md#app.managers.file_manager.FileManager.copy)
      * [`FileManager.delete()`](app.managers.md#app.managers.file_manager.FileManager.delete)
      * [`FileManager.filesize()`](app.managers.md#app.managers.file_manager.FileManager.filesize)
      * [`FileManager.isdir()`](app.managers.md#app.managers.file_manager.FileManager.isdir)
      * [`FileManager.isfile()`](app.managers.md#app.managers.file_manager.FileManager.isfile)
      * [`FileManager.mimetype()`](app.managers.md#app.managers.file_manager.FileManager.mimetype)
      * [`FileManager.mkdir()`](app.managers.md#app.managers.file_manager.FileManager.mkdir)
      * [`FileManager.read()`](app.managers.md#app.managers.file_manager.FileManager.read)
      * [`FileManager.rename()`](app.managers.md#app.managers.file_manager.FileManager.rename)
      * [`FileManager.rmdir()`](app.managers.md#app.managers.file_manager.FileManager.rmdir)
      * [`FileManager.upload()`](app.managers.md#app.managers.file_manager.FileManager.upload)
      * [`FileManager.write()`](app.managers.md#app.managers.file_manager.FileManager.write)
  * [Module contents](app.managers.md#module-app.managers)
* [app.models package](app.models.md)
  * [app.models.file module](app.models.md#module-app.models.file)
    * [`File`](app.models.md#app.models.file.File)
      * [`File.checksum`](app.models.md#app.models.file.File.checksum)
      * [`File.created_date`](app.models.md#app.models.file.File.created_date)
      * [`File.file_folder`](app.models.md#app.models.file.File.file_folder)
      * [`File.file_meta`](app.models.md#app.models.file.File.file_meta)
      * [`File.file_revisions`](app.models.md#app.models.file.File.file_revisions)
      * [`File.file_tags`](app.models.md#app.models.file.File.file_tags)
      * [`File.file_thumbnail`](app.models.md#app.models.file.File.file_thumbnail)
      * [`File.file_user`](app.models.md#app.models.file.File.file_user)
      * [`File.filename`](app.models.md#app.models.file.File.filename)
      * [`File.filesize`](app.models.md#app.models.file.File.filesize)
      * [`File.flagged`](app.models.md#app.models.file.File.flagged)
      * [`File.folder_id`](app.models.md#app.models.file.File.folder_id)
      * [`File.has_revisions`](app.models.md#app.models.file.File.has_revisions)
      * [`File.has_thumbnail`](app.models.md#app.models.file.File.has_thumbnail)
      * [`File.id`](app.models.md#app.models.file.File.id)
      * [`File.latest_revision_number`](app.models.md#app.models.file.File.latest_revision_number)
      * [`File.mimetype`](app.models.md#app.models.file.File.mimetype)
      * [`File.path()`](app.models.md#app.models.file.File.path)
      * [`File.path_for_filename()`](app.models.md#app.models.file.File.path_for_filename)
      * [`File.summary`](app.models.md#app.models.file.File.summary)
      * [`File.to_dict()`](app.models.md#app.models.file.File.to_dict)
      * [`File.updated_date`](app.models.md#app.models.file.File.updated_date)
      * [`File.user_id`](app.models.md#app.models.file.File.user_id)
  * [app.models.file_meta module](app.models.md#module-app.models.file_meta)
    * [`FileMeta`](app.models.md#app.models.file_meta.FileMeta)
      * [`FileMeta.created_date`](app.models.md#app.models.file_meta.FileMeta.created_date)
      * [`FileMeta.file_id`](app.models.md#app.models.file_meta.FileMeta.file_id)
      * [`FileMeta.id`](app.models.md#app.models.file_meta.FileMeta.id)
      * [`FileMeta.meta_file`](app.models.md#app.models.file_meta.FileMeta.meta_file)
      * [`FileMeta.meta_key`](app.models.md#app.models.file_meta.FileMeta.meta_key)
      * [`FileMeta.meta_value`](app.models.md#app.models.file_meta.FileMeta.meta_value)
      * [`FileMeta.updated_date`](app.models.md#app.models.file_meta.FileMeta.updated_date)
  * [app.models.file_revision module](app.models.md#module-app.models.file_revision)
    * [`FileRevision`](app.models.md#app.models.file_revision.FileRevision)
      * [`FileRevision.checksum`](app.models.md#app.models.file_revision.FileRevision.checksum)
      * [`FileRevision.created_date`](app.models.md#app.models.file_revision.FileRevision.created_date)
      * [`FileRevision.file_id`](app.models.md#app.models.file_revision.FileRevision.file_id)
      * [`FileRevision.filesize`](app.models.md#app.models.file_revision.FileRevision.filesize)
      * [`FileRevision.id`](app.models.md#app.models.file_revision.FileRevision.id)
      * [`FileRevision.path()`](app.models.md#app.models.file_revision.FileRevision.path)
      * [`FileRevision.path_for_uuid()`](app.models.md#app.models.file_revision.FileRevision.path_for_uuid)
      * [`FileRevision.revision_file`](app.models.md#app.models.file_revision.FileRevision.revision_file)
      * [`FileRevision.revision_number`](app.models.md#app.models.file_revision.FileRevision.revision_number)
      * [`FileRevision.revision_user`](app.models.md#app.models.file_revision.FileRevision.revision_user)
      * [`FileRevision.to_dict()`](app.models.md#app.models.file_revision.FileRevision.to_dict)
      * [`FileRevision.user_id`](app.models.md#app.models.file_revision.FileRevision.user_id)
      * [`FileRevision.uuid`](app.models.md#app.models.file_revision.FileRevision.uuid)
  * [app.models.file_tag module](app.models.md#module-app.models.file_tag)
    * [`FileTag`](app.models.md#app.models.file_tag.FileTag)
      * [`FileTag.created_date`](app.models.md#app.models.file_tag.FileTag.created_date)
      * [`FileTag.file_id`](app.models.md#app.models.file_tag.FileTag.file_id)
      * [`FileTag.id`](app.models.md#app.models.file_tag.FileTag.id)
      * [`FileTag.tag_file`](app.models.md#app.models.file_tag.FileTag.tag_file)
      * [`FileTag.value`](app.models.md#app.models.file_tag.FileTag.value)
  * [app.models.file_thumbnail module](app.models.md#module-app.models.file_thumbnail)
    * [`FileThumbnail`](app.models.md#app.models.file_thumbnail.FileThumbnail)
      * [`FileThumbnail.checksum`](app.models.md#app.models.file_thumbnail.FileThumbnail.checksum)
      * [`FileThumbnail.created_date`](app.models.md#app.models.file_thumbnail.FileThumbnail.created_date)
      * [`FileThumbnail.file_id`](app.models.md#app.models.file_thumbnail.FileThumbnail.file_id)
      * [`FileThumbnail.filesize`](app.models.md#app.models.file_thumbnail.FileThumbnail.filesize)
      * [`FileThumbnail.id`](app.models.md#app.models.file_thumbnail.FileThumbnail.id)
      * [`FileThumbnail.thumbnail_file`](app.models.md#app.models.file_thumbnail.FileThumbnail.thumbnail_file)
      * [`FileThumbnail.updated_date`](app.models.md#app.models.file_thumbnail.FileThumbnail.updated_date)
      * [`FileThumbnail.uuid`](app.models.md#app.models.file_thumbnail.FileThumbnail.uuid)
  * [app.models.folder module](app.models.md#module-app.models.folder)
    * [`Folder`](app.models.md#app.models.folder.Folder)
      * [`Folder.created_date`](app.models.md#app.models.folder.Folder.created_date)
      * [`Folder.folder_files`](app.models.md#app.models.folder.Folder.folder_files)
      * [`Folder.folder_meta`](app.models.md#app.models.folder.Folder.folder_meta)
      * [`Folder.folder_user`](app.models.md#app.models.folder.Folder.folder_user)
      * [`Folder.id`](app.models.md#app.models.folder.Folder.id)
      * [`Folder.name`](app.models.md#app.models.folder.Folder.name)
      * [`Folder.path()`](app.models.md#app.models.folder.Folder.path)
      * [`Folder.path_for_dir()`](app.models.md#app.models.folder.Folder.path_for_dir)
      * [`Folder.readonly`](app.models.md#app.models.folder.Folder.readonly)
      * [`Folder.summary`](app.models.md#app.models.folder.Folder.summary)
      * [`Folder.to_dict()`](app.models.md#app.models.folder.Folder.to_dict)
      * [`Folder.updated_date`](app.models.md#app.models.folder.Folder.updated_date)
      * [`Folder.user_id`](app.models.md#app.models.folder.Folder.user_id)
  * [app.models.folder_meta module](app.models.md#module-app.models.folder_meta)
    * [`FolderMeta`](app.models.md#app.models.folder_meta.FolderMeta)
      * [`FolderMeta.created_date`](app.models.md#app.models.folder_meta.FolderMeta.created_date)
      * [`FolderMeta.folder_id`](app.models.md#app.models.folder_meta.FolderMeta.folder_id)
      * [`FolderMeta.id`](app.models.md#app.models.folder_meta.FolderMeta.id)
      * [`FolderMeta.meta_folder`](app.models.md#app.models.folder_meta.FolderMeta.meta_folder)
      * [`FolderMeta.meta_key`](app.models.md#app.models.folder_meta.FolderMeta.meta_key)
      * [`FolderMeta.meta_value`](app.models.md#app.models.folder_meta.FolderMeta.meta_value)
      * [`FolderMeta.updated_date`](app.models.md#app.models.folder_meta.FolderMeta.updated_date)
  * [app.models.user module](app.models.md#module-app.models.user)
    * [`User`](app.models.md#app.models.user.User)
      * [`User.active`](app.models.md#app.models.user.User.active)
      * [`User.can_admin`](app.models.md#app.models.user.User.can_admin)
      * [`User.can_edit`](app.models.md#app.models.user.User.can_edit)
      * [`User.can_read`](app.models.md#app.models.user.User.can_read)
      * [`User.can_write`](app.models.md#app.models.user.User.can_write)
      * [`User.created_date`](app.models.md#app.models.user.User.created_date)
      * [`User.first_name`](app.models.md#app.models.user.User.first_name)
      * [`User.full_name`](app.models.md#app.models.user.User.full_name)
      * [`User.has_thumbnail`](app.models.md#app.models.user.User.has_thumbnail)
      * [`User.id`](app.models.md#app.models.user.User.id)
      * [`User.jti_encrypted`](app.models.md#app.models.user.User.jti_encrypted)
      * [`User.last_login_date`](app.models.md#app.models.user.User.last_login_date)
      * [`User.last_name`](app.models.md#app.models.user.User.last_name)
      * [`User.mfa_attempts`](app.models.md#app.models.user.User.mfa_attempts)
      * [`User.mfa_secret_encrypted`](app.models.md#app.models.user.User.mfa_secret_encrypted)
      * [`User.password_accepted`](app.models.md#app.models.user.User.password_accepted)
      * [`User.password_attempts`](app.models.md#app.models.user.User.password_attempts)
      * [`User.password_hash`](app.models.md#app.models.user.User.password_hash)
      * [`User.role`](app.models.md#app.models.user.User.role)
      * [`User.summary`](app.models.md#app.models.user.User.summary)
      * [`User.suspended_until_date`](app.models.md#app.models.user.User.suspended_until_date)
      * [`User.to_dict()`](app.models.md#app.models.user.User.to_dict)
      * [`User.updated_date`](app.models.md#app.models.user.User.updated_date)
      * [`User.user_files`](app.models.md#app.models.user.User.user_files)
      * [`User.user_folders`](app.models.md#app.models.user.User.user_folders)
      * [`User.user_meta`](app.models.md#app.models.user.User.user_meta)
      * [`User.user_revisions`](app.models.md#app.models.user.User.user_revisions)
      * [`User.user_thumbnail`](app.models.md#app.models.user.User.user_thumbnail)
      * [`User.username`](app.models.md#app.models.user.User.username)
    * [`UserRole`](app.models.md#app.models.user.UserRole)
      * [`UserRole.admin`](app.models.md#app.models.user.UserRole.admin)
      * [`UserRole.editor`](app.models.md#app.models.user.UserRole.editor)
      * [`UserRole.reader`](app.models.md#app.models.user.UserRole.reader)
      * [`UserRole.writer`](app.models.md#app.models.user.UserRole.writer)
  * [app.models.user_meta module](app.models.md#module-app.models.user_meta)
    * [`UserMeta`](app.models.md#app.models.user_meta.UserMeta)
      * [`UserMeta.created_date`](app.models.md#app.models.user_meta.UserMeta.created_date)
      * [`UserMeta.id`](app.models.md#app.models.user_meta.UserMeta.id)
      * [`UserMeta.meta_key`](app.models.md#app.models.user_meta.UserMeta.meta_key)
      * [`UserMeta.meta_user`](app.models.md#app.models.user_meta.UserMeta.meta_user)
      * [`UserMeta.meta_value`](app.models.md#app.models.user_meta.UserMeta.meta_value)
      * [`UserMeta.updated_date`](app.models.md#app.models.user_meta.UserMeta.updated_date)
      * [`UserMeta.user_id`](app.models.md#app.models.user_meta.UserMeta.user_id)
  * [app.models.user_thumbnail module](app.models.md#module-app.models.user_thumbnail)
    * [`UserThumbnail`](app.models.md#app.models.user_thumbnail.UserThumbnail)
      * [`UserThumbnail.checksum`](app.models.md#app.models.user_thumbnail.UserThumbnail.checksum)
      * [`UserThumbnail.created_date`](app.models.md#app.models.user_thumbnail.UserThumbnail.created_date)
      * [`UserThumbnail.filesize`](app.models.md#app.models.user_thumbnail.UserThumbnail.filesize)
      * [`UserThumbnail.id`](app.models.md#app.models.user_thumbnail.UserThumbnail.id)
      * [`UserThumbnail.thumbnail_user`](app.models.md#app.models.user_thumbnail.UserThumbnail.thumbnail_user)
      * [`UserThumbnail.updated_date`](app.models.md#app.models.user_thumbnail.UserThumbnail.updated_date)
      * [`UserThumbnail.user_id`](app.models.md#app.models.user_thumbnail.UserThumbnail.user_id)
      * [`UserThumbnail.uuid`](app.models.md#app.models.user_thumbnail.UserThumbnail.uuid)
  * [Module contents](app.models.md#module-app.models)
* [app.routers package](app.routers.md)
  * [app.routers.file_delete module](app.routers.md#module-app.routers.file_delete)
    * [`file_delete()`](app.routers.md#app.routers.file_delete.file_delete)
  * [app.routers.file_download module](app.routers.md#module-app.routers.file_download)
    * [`file_download()`](app.routers.md#app.routers.file_download.file_download)
  * [app.routers.file_list module](app.routers.md#module-app.routers.file_list)
    * [`file_list()`](app.routers.md#app.routers.file_list.file_list)
  * [app.routers.file_select module](app.routers.md#module-app.routers.file_select)
    * [`file_select()`](app.routers.md#app.routers.file_select.file_select)
  * [app.routers.file_update module](app.routers.md#module-app.routers.file_update)
    * [`file_update()`](app.routers.md#app.routers.file_update.file_update)
  * [app.routers.file_upload module](app.routers.md#module-app.routers.file_upload)
    * [`file_upload()`](app.routers.md#app.routers.file_upload.file_upload)
  * [app.routers.folder_delete module](app.routers.md#module-app.routers.folder_delete)
    * [`folder_delete()`](app.routers.md#app.routers.folder_delete.folder_delete)
  * [app.routers.folder_insert module](app.routers.md#module-app.routers.folder_insert)
    * [`folder_insert()`](app.routers.md#app.routers.folder_insert.folder_insert)
  * [app.routers.folder_list module](app.routers.md#module-app.routers.folder_list)
    * [`folder_list()`](app.routers.md#app.routers.folder_list.folder_list)
  * [app.routers.folder_select module](app.routers.md#module-app.routers.folder_select)
    * [`folder_select()`](app.routers.md#app.routers.folder_select.folder_select)
  * [app.routers.folder_update module](app.routers.md#module-app.routers.folder_update)
    * [`folder_update()`](app.routers.md#app.routers.folder_update.folder_update)
  * [app.routers.tag_delete module](app.routers.md#module-app.routers.tag_delete)
    * [`tag_delete()`](app.routers.md#app.routers.tag_delete.tag_delete)
  * [app.routers.tag_insert module](app.routers.md#module-app.routers.tag_insert)
    * [`tag_insert()`](app.routers.md#app.routers.tag_insert.tag_insert)
  * [app.routers.telemetry_retrieve module](app.routers.md#module-app.routers.telemetry_retrieve)
    * [`telemetry_retrieve()`](app.routers.md#app.routers.telemetry_retrieve.telemetry_retrieve)
  * [app.routers.thumbnail_retrieve module](app.routers.md#module-app.routers.thumbnail_retrieve)
    * [`thumbnail_retrieve()`](app.routers.md#app.routers.thumbnail_retrieve.thumbnail_retrieve)
  * [app.routers.token_invalidate module](app.routers.md#module-app.routers.token_invalidate)
    * [`token_invalidate()`](app.routers.md#app.routers.token_invalidate.token_invalidate)
  * [app.routers.token_retrieve module](app.routers.md#module-app.routers.token_retrieve)
    * [`token_retrieve()`](app.routers.md#app.routers.token_retrieve.token_retrieve)
  * [app.routers.user_delete module](app.routers.md#module-app.routers.user_delete)
    * [`user_delete()`](app.routers.md#app.routers.user_delete.user_delete)
  * [app.routers.user_list module](app.routers.md#module-app.routers.user_list)
    * [`user_list()`](app.routers.md#app.routers.user_list.user_list)
  * [app.routers.user_login module](app.routers.md#module-app.routers.user_login)
    * [`user_login()`](app.routers.md#app.routers.user_login.user_login)
  * [app.routers.user_password module](app.routers.md#module-app.routers.user_password)
    * [`user_password()`](app.routers.md#app.routers.user_password.user_password)
  * [app.routers.user_register module](app.routers.md#module-app.routers.user_register)
    * [`user_register()`](app.routers.md#app.routers.user_register.user_register)
  * [app.routers.user_role module](app.routers.md#module-app.routers.user_role)
    * [`user_role()`](app.routers.md#app.routers.user_role.user_role)
  * [app.routers.user_select module](app.routers.md#module-app.routers.user_select)
    * [`user_select()`](app.routers.md#app.routers.user_select.user_select)
  * [app.routers.user_update module](app.routers.md#module-app.routers.user_update)
    * [`user_update()`](app.routers.md#app.routers.user_update.user_update)
  * [app.routers.userpic_delete module](app.routers.md#module-app.routers.userpic_delete)
    * [`userpic_delete()`](app.routers.md#app.routers.userpic_delete.userpic_delete)
  * [app.routers.userpic_retrieve module](app.routers.md#module-app.routers.userpic_retrieve)
    * [`userpic_retrieve()`](app.routers.md#app.routers.userpic_retrieve.userpic_retrieve)
  * [app.routers.userpic_upload module](app.routers.md#module-app.routers.userpic_upload)
    * [`userpic_upload()`](app.routers.md#app.routers.userpic_upload.userpic_upload)
  * [Module contents](app.routers.md#module-app.routers)
* [app.schemas package](app.schemas.md)
  * [app.schemas.file_delete module](app.schemas.md#module-app.schemas.file_delete)
    * [`FileDeleteResponse`](app.schemas.md#app.schemas.file_delete.FileDeleteResponse)
      * [`FileDeleteResponse.file_id`](app.schemas.md#app.schemas.file_delete.FileDeleteResponse.file_id)
      * [`FileDeleteResponse.latest_revision_number`](app.schemas.md#app.schemas.file_delete.FileDeleteResponse.latest_revision_number)
      * [`FileDeleteResponse.model_config`](app.schemas.md#app.schemas.file_delete.FileDeleteResponse.model_config)
  * [app.schemas.file_list module](app.schemas.md#module-app.schemas.file_list)
    * [`FileListRequest`](app.schemas.md#app.schemas.file_list.FileListRequest)
      * [`FileListRequest.created_date__ge`](app.schemas.md#app.schemas.file_list.FileListRequest.created_date__ge)
      * [`FileListRequest.created_date__le`](app.schemas.md#app.schemas.file_list.FileListRequest.created_date__le)
      * [`FileListRequest.filename__ilike`](app.schemas.md#app.schemas.file_list.FileListRequest.filename__ilike)
      * [`FileListRequest.filesize__ge`](app.schemas.md#app.schemas.file_list.FileListRequest.filesize__ge)
      * [`FileListRequest.filesize__le`](app.schemas.md#app.schemas.file_list.FileListRequest.filesize__le)
      * [`FileListRequest.flagged__eq`](app.schemas.md#app.schemas.file_list.FileListRequest.flagged__eq)
      * [`FileListRequest.folder_id__eq`](app.schemas.md#app.schemas.file_list.FileListRequest.folder_id__eq)
      * [`FileListRequest.limit`](app.schemas.md#app.schemas.file_list.FileListRequest.limit)
      * [`FileListRequest.mimetype__ilike`](app.schemas.md#app.schemas.file_list.FileListRequest.mimetype__ilike)
      * [`FileListRequest.model_config`](app.schemas.md#app.schemas.file_list.FileListRequest.model_config)
      * [`FileListRequest.offset`](app.schemas.md#app.schemas.file_list.FileListRequest.offset)
      * [`FileListRequest.order`](app.schemas.md#app.schemas.file_list.FileListRequest.order)
      * [`FileListRequest.order_by`](app.schemas.md#app.schemas.file_list.FileListRequest.order_by)
      * [`FileListRequest.tag_value__eq`](app.schemas.md#app.schemas.file_list.FileListRequest.tag_value__eq)
      * [`FileListRequest.updated_date__ge`](app.schemas.md#app.schemas.file_list.FileListRequest.updated_date__ge)
      * [`FileListRequest.updated_date__le`](app.schemas.md#app.schemas.file_list.FileListRequest.updated_date__le)
      * [`FileListRequest.user_id__eq`](app.schemas.md#app.schemas.file_list.FileListRequest.user_id__eq)
    * [`FileListResponse`](app.schemas.md#app.schemas.file_list.FileListResponse)
      * [`FileListResponse.files`](app.schemas.md#app.schemas.file_list.FileListResponse.files)
      * [`FileListResponse.files_count`](app.schemas.md#app.schemas.file_list.FileListResponse.files_count)
      * [`FileListResponse.model_config`](app.schemas.md#app.schemas.file_list.FileListResponse.model_config)
  * [app.schemas.file_select module](app.schemas.md#module-app.schemas.file_select)
    * [`FileSelectResponse`](app.schemas.md#app.schemas.file_select.FileSelectResponse)
      * [`FileSelectResponse.checksum`](app.schemas.md#app.schemas.file_select.FileSelectResponse.checksum)
      * [`FileSelectResponse.created_date`](app.schemas.md#app.schemas.file_select.FileSelectResponse.created_date)
      * [`FileSelectResponse.file_revisions`](app.schemas.md#app.schemas.file_select.FileSelectResponse.file_revisions)
      * [`FileSelectResponse.file_tags`](app.schemas.md#app.schemas.file_select.FileSelectResponse.file_tags)
      * [`FileSelectResponse.filename`](app.schemas.md#app.schemas.file_select.FileSelectResponse.filename)
      * [`FileSelectResponse.filesize`](app.schemas.md#app.schemas.file_select.FileSelectResponse.filesize)
      * [`FileSelectResponse.flagged`](app.schemas.md#app.schemas.file_select.FileSelectResponse.flagged)
      * [`FileSelectResponse.folder`](app.schemas.md#app.schemas.file_select.FileSelectResponse.folder)
      * [`FileSelectResponse.id`](app.schemas.md#app.schemas.file_select.FileSelectResponse.id)
      * [`FileSelectResponse.latest_revision_number`](app.schemas.md#app.schemas.file_select.FileSelectResponse.latest_revision_number)
      * [`FileSelectResponse.mimetype`](app.schemas.md#app.schemas.file_select.FileSelectResponse.mimetype)
      * [`FileSelectResponse.model_config`](app.schemas.md#app.schemas.file_select.FileSelectResponse.model_config)
      * [`FileSelectResponse.summary`](app.schemas.md#app.schemas.file_select.FileSelectResponse.summary)
      * [`FileSelectResponse.updated_date`](app.schemas.md#app.schemas.file_select.FileSelectResponse.updated_date)
      * [`FileSelectResponse.user`](app.schemas.md#app.schemas.file_select.FileSelectResponse.user)
  * [app.schemas.file_update module](app.schemas.md#module-app.schemas.file_update)
    * [`FileUpdateRequest`](app.schemas.md#app.schemas.file_update.FileUpdateRequest)
      * [`FileUpdateRequest.filename`](app.schemas.md#app.schemas.file_update.FileUpdateRequest.filename)
      * [`FileUpdateRequest.folder_id`](app.schemas.md#app.schemas.file_update.FileUpdateRequest.folder_id)
      * [`FileUpdateRequest.model_config`](app.schemas.md#app.schemas.file_update.FileUpdateRequest.model_config)
      * [`FileUpdateRequest.summary`](app.schemas.md#app.schemas.file_update.FileUpdateRequest.summary)
    * [`FileUpdateResponse`](app.schemas.md#app.schemas.file_update.FileUpdateResponse)
      * [`FileUpdateResponse.file_id`](app.schemas.md#app.schemas.file_update.FileUpdateResponse.file_id)
      * [`FileUpdateResponse.latest_revision_number`](app.schemas.md#app.schemas.file_update.FileUpdateResponse.latest_revision_number)
      * [`FileUpdateResponse.model_config`](app.schemas.md#app.schemas.file_update.FileUpdateResponse.model_config)
  * [app.schemas.file_upload module](app.schemas.md#module-app.schemas.file_upload)
    * [`FileUploadResponse`](app.schemas.md#app.schemas.file_upload.FileUploadResponse)
      * [`FileUploadResponse.file_id`](app.schemas.md#app.schemas.file_upload.FileUploadResponse.file_id)
      * [`FileUploadResponse.latest_revision_number`](app.schemas.md#app.schemas.file_upload.FileUploadResponse.latest_revision_number)
      * [`FileUploadResponse.model_config`](app.schemas.md#app.schemas.file_upload.FileUploadResponse.model_config)
  * [app.schemas.folder_delete module](app.schemas.md#module-app.schemas.folder_delete)
    * [`FolderDeleteResponse`](app.schemas.md#app.schemas.folder_delete.FolderDeleteResponse)
      * [`FolderDeleteResponse.folder_id`](app.schemas.md#app.schemas.folder_delete.FolderDeleteResponse.folder_id)
      * [`FolderDeleteResponse.model_config`](app.schemas.md#app.schemas.folder_delete.FolderDeleteResponse.model_config)
  * [app.schemas.folder_insert module](app.schemas.md#module-app.schemas.folder_insert)
    * [`FolderInsertRequest`](app.schemas.md#app.schemas.folder_insert.FolderInsertRequest)
      * [`FolderInsertRequest.model_config`](app.schemas.md#app.schemas.folder_insert.FolderInsertRequest.model_config)
      * [`FolderInsertRequest.name`](app.schemas.md#app.schemas.folder_insert.FolderInsertRequest.name)
      * [`FolderInsertRequest.readonly`](app.schemas.md#app.schemas.folder_insert.FolderInsertRequest.readonly)
      * [`FolderInsertRequest.summary`](app.schemas.md#app.schemas.folder_insert.FolderInsertRequest.summary)
    * [`FolderInsertResponse`](app.schemas.md#app.schemas.folder_insert.FolderInsertResponse)
      * [`FolderInsertResponse.folder_id`](app.schemas.md#app.schemas.folder_insert.FolderInsertResponse.folder_id)
      * [`FolderInsertResponse.model_config`](app.schemas.md#app.schemas.folder_insert.FolderInsertResponse.model_config)
  * [app.schemas.folder_list module](app.schemas.md#module-app.schemas.folder_list)
    * [`FolderListRequest`](app.schemas.md#app.schemas.folder_list.FolderListRequest)
      * [`FolderListRequest.created_date__ge`](app.schemas.md#app.schemas.folder_list.FolderListRequest.created_date__ge)
      * [`FolderListRequest.created_date__le`](app.schemas.md#app.schemas.folder_list.FolderListRequest.created_date__le)
      * [`FolderListRequest.limit`](app.schemas.md#app.schemas.folder_list.FolderListRequest.limit)
      * [`FolderListRequest.model_config`](app.schemas.md#app.schemas.folder_list.FolderListRequest.model_config)
      * [`FolderListRequest.name__ilike`](app.schemas.md#app.schemas.folder_list.FolderListRequest.name__ilike)
      * [`FolderListRequest.offset`](app.schemas.md#app.schemas.folder_list.FolderListRequest.offset)
      * [`FolderListRequest.order`](app.schemas.md#app.schemas.folder_list.FolderListRequest.order)
      * [`FolderListRequest.order_by`](app.schemas.md#app.schemas.folder_list.FolderListRequest.order_by)
      * [`FolderListRequest.readonly__eq`](app.schemas.md#app.schemas.folder_list.FolderListRequest.readonly__eq)
      * [`FolderListRequest.updated_date__ge`](app.schemas.md#app.schemas.folder_list.FolderListRequest.updated_date__ge)
      * [`FolderListRequest.updated_date__le`](app.schemas.md#app.schemas.folder_list.FolderListRequest.updated_date__le)
      * [`FolderListRequest.user_id__eq`](app.schemas.md#app.schemas.folder_list.FolderListRequest.user_id__eq)
    * [`FolderListResponse`](app.schemas.md#app.schemas.folder_list.FolderListResponse)
      * [`FolderListResponse.folders`](app.schemas.md#app.schemas.folder_list.FolderListResponse.folders)
      * [`FolderListResponse.folders_count`](app.schemas.md#app.schemas.folder_list.FolderListResponse.folders_count)
      * [`FolderListResponse.model_config`](app.schemas.md#app.schemas.folder_list.FolderListResponse.model_config)
  * [app.schemas.folder_select module](app.schemas.md#module-app.schemas.folder_select)
    * [`FolderSelectResponse`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse)
      * [`FolderSelectResponse.created_date`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.created_date)
      * [`FolderSelectResponse.id`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.id)
      * [`FolderSelectResponse.model_config`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.model_config)
      * [`FolderSelectResponse.name`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.name)
      * [`FolderSelectResponse.readonly`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.readonly)
      * [`FolderSelectResponse.summary`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.summary)
      * [`FolderSelectResponse.updated_date`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.updated_date)
      * [`FolderSelectResponse.user`](app.schemas.md#app.schemas.folder_select.FolderSelectResponse.user)
  * [app.schemas.folder_update module](app.schemas.md#module-app.schemas.folder_update)
    * [`FolderUpdateRequest`](app.schemas.md#app.schemas.folder_update.FolderUpdateRequest)
      * [`FolderUpdateRequest.model_config`](app.schemas.md#app.schemas.folder_update.FolderUpdateRequest.model_config)
      * [`FolderUpdateRequest.name`](app.schemas.md#app.schemas.folder_update.FolderUpdateRequest.name)
      * [`FolderUpdateRequest.readonly`](app.schemas.md#app.schemas.folder_update.FolderUpdateRequest.readonly)
      * [`FolderUpdateRequest.summary`](app.schemas.md#app.schemas.folder_update.FolderUpdateRequest.summary)
    * [`FolderUpdateResponse`](app.schemas.md#app.schemas.folder_update.FolderUpdateResponse)
      * [`FolderUpdateResponse.folder_id`](app.schemas.md#app.schemas.folder_update.FolderUpdateResponse.folder_id)
      * [`FolderUpdateResponse.model_config`](app.schemas.md#app.schemas.folder_update.FolderUpdateResponse.model_config)
  * [app.schemas.revision_select module](app.schemas.md#module-app.schemas.revision_select)
    * [`RevisionSelectResponse`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse)
      * [`RevisionSelectResponse.checksum`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.checksum)
      * [`RevisionSelectResponse.created_date`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.created_date)
      * [`RevisionSelectResponse.file_id`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.file_id)
      * [`RevisionSelectResponse.filesize`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.filesize)
      * [`RevisionSelectResponse.id`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.id)
      * [`RevisionSelectResponse.model_config`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.model_config)
      * [`RevisionSelectResponse.revision_number`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.revision_number)
      * [`RevisionSelectResponse.user`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.user)
      * [`RevisionSelectResponse.uuid`](app.schemas.md#app.schemas.revision_select.RevisionSelectResponse.uuid)
  * [app.schemas.tag_delete module](app.schemas.md#module-app.schemas.tag_delete)
    * [`TagDeleteResponse`](app.schemas.md#app.schemas.tag_delete.TagDeleteResponse)
      * [`TagDeleteResponse.file_id`](app.schemas.md#app.schemas.tag_delete.TagDeleteResponse.file_id)
      * [`TagDeleteResponse.latest_revision_number`](app.schemas.md#app.schemas.tag_delete.TagDeleteResponse.latest_revision_number)
      * [`TagDeleteResponse.model_config`](app.schemas.md#app.schemas.tag_delete.TagDeleteResponse.model_config)
  * [app.schemas.tag_insert module](app.schemas.md#module-app.schemas.tag_insert)
    * [`TagInsertRequest`](app.schemas.md#app.schemas.tag_insert.TagInsertRequest)
      * [`TagInsertRequest.model_config`](app.schemas.md#app.schemas.tag_insert.TagInsertRequest.model_config)
      * [`TagInsertRequest.validate_value()`](app.schemas.md#app.schemas.tag_insert.TagInsertRequest.validate_value)
      * [`TagInsertRequest.value`](app.schemas.md#app.schemas.tag_insert.TagInsertRequest.value)
    * [`TagInsertResponse`](app.schemas.md#app.schemas.tag_insert.TagInsertResponse)
      * [`TagInsertResponse.file_id`](app.schemas.md#app.schemas.tag_insert.TagInsertResponse.file_id)
      * [`TagInsertResponse.latest_revision_number`](app.schemas.md#app.schemas.tag_insert.TagInsertResponse.latest_revision_number)
      * [`TagInsertResponse.model_config`](app.schemas.md#app.schemas.tag_insert.TagInsertResponse.model_config)
  * [app.schemas.telemetry_retrieve module](app.schemas.md#module-app.schemas.telemetry_retrieve)
    * [`TelemetryRetrieveResponse`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse)
      * [`TelemetryRetrieveResponse.app_version`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.app_version)
      * [`TelemetryRetrieveResponse.cpu_core_count`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.cpu_core_count)
      * [`TelemetryRetrieveResponse.cpu_frequency`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.cpu_frequency)
      * [`TelemetryRetrieveResponse.cpu_usage_percent`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.cpu_usage_percent)
      * [`TelemetryRetrieveResponse.disk_free`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.disk_free)
      * [`TelemetryRetrieveResponse.disk_total`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.disk_total)
      * [`TelemetryRetrieveResponse.disk_used`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.disk_used)
      * [`TelemetryRetrieveResponse.memory_free`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.memory_free)
      * [`TelemetryRetrieveResponse.memory_total`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.memory_total)
      * [`TelemetryRetrieveResponse.memory_used`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.memory_used)
      * [`TelemetryRetrieveResponse.model_config`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.model_config)
      * [`TelemetryRetrieveResponse.os_name`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.os_name)
      * [`TelemetryRetrieveResponse.os_release`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.os_release)
      * [`TelemetryRetrieveResponse.os_version`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.os_version)
      * [`TelemetryRetrieveResponse.platform_alias`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.platform_alias)
      * [`TelemetryRetrieveResponse.platform_architecture`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.platform_architecture)
      * [`TelemetryRetrieveResponse.platform_processor`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.platform_processor)
      * [`TelemetryRetrieveResponse.python_compiler`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.python_compiler)
      * [`TelemetryRetrieveResponse.python_implementation`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.python_implementation)
      * [`TelemetryRetrieveResponse.python_version`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.python_version)
      * [`TelemetryRetrieveResponse.redis_memory`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.redis_memory)
      * [`TelemetryRetrieveResponse.redis_version`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.redis_version)
      * [`TelemetryRetrieveResponse.sqlite_size`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.sqlite_size)
      * [`TelemetryRetrieveResponse.sqlite_version`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.sqlite_version)
      * [`TelemetryRetrieveResponse.timezone_name`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.timezone_name)
      * [`TelemetryRetrieveResponse.timezone_offset`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.timezone_offset)
      * [`TelemetryRetrieveResponse.unix_timestamp`](app.schemas.md#app.schemas.telemetry_retrieve.TelemetryRetrieveResponse.unix_timestamp)
  * [app.schemas.token_invalidate module](app.schemas.md#module-app.schemas.token_invalidate)
    * [`TokenInvalidateResponse`](app.schemas.md#app.schemas.token_invalidate.TokenInvalidateResponse)
      * [`TokenInvalidateResponse.model_config`](app.schemas.md#app.schemas.token_invalidate.TokenInvalidateResponse.model_config)
      * [`TokenInvalidateResponse.user_id`](app.schemas.md#app.schemas.token_invalidate.TokenInvalidateResponse.user_id)
  * [app.schemas.token_retrieve module](app.schemas.md#module-app.schemas.token_retrieve)
    * [`TokenRetrieveRequest`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveRequest)
      * [`TokenRetrieveRequest.exp`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveRequest.exp)
      * [`TokenRetrieveRequest.model_config`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveRequest.model_config)
      * [`TokenRetrieveRequest.totp`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveRequest.totp)
      * [`TokenRetrieveRequest.username`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveRequest.username)
    * [`TokenRetrieveResponse`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveResponse)
      * [`TokenRetrieveResponse.model_config`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveResponse.model_config)
      * [`TokenRetrieveResponse.user_id`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveResponse.user_id)
      * [`TokenRetrieveResponse.user_token`](app.schemas.md#app.schemas.token_retrieve.TokenRetrieveResponse.user_token)
  * [app.schemas.user_delete module](app.schemas.md#module-app.schemas.user_delete)
    * [`UserDeleteResponse`](app.schemas.md#app.schemas.user_delete.UserDeleteResponse)
      * [`UserDeleteResponse.model_config`](app.schemas.md#app.schemas.user_delete.UserDeleteResponse.model_config)
      * [`UserDeleteResponse.user_id`](app.schemas.md#app.schemas.user_delete.UserDeleteResponse.user_id)
  * [app.schemas.user_list module](app.schemas.md#module-app.schemas.user_list)
    * [`UserListRequest`](app.schemas.md#app.schemas.user_list.UserListRequest)
      * [`UserListRequest.active__eq`](app.schemas.md#app.schemas.user_list.UserListRequest.active__eq)
      * [`UserListRequest.created_date__ge`](app.schemas.md#app.schemas.user_list.UserListRequest.created_date__ge)
      * [`UserListRequest.created_date__le`](app.schemas.md#app.schemas.user_list.UserListRequest.created_date__le)
      * [`UserListRequest.first_name__ilike`](app.schemas.md#app.schemas.user_list.UserListRequest.first_name__ilike)
      * [`UserListRequest.full_name__ilike`](app.schemas.md#app.schemas.user_list.UserListRequest.full_name__ilike)
      * [`UserListRequest.last_login_date__ge`](app.schemas.md#app.schemas.user_list.UserListRequest.last_login_date__ge)
      * [`UserListRequest.last_login_date__le`](app.schemas.md#app.schemas.user_list.UserListRequest.last_login_date__le)
      * [`UserListRequest.last_name__ilike`](app.schemas.md#app.schemas.user_list.UserListRequest.last_name__ilike)
      * [`UserListRequest.limit`](app.schemas.md#app.schemas.user_list.UserListRequest.limit)
      * [`UserListRequest.model_config`](app.schemas.md#app.schemas.user_list.UserListRequest.model_config)
      * [`UserListRequest.offset`](app.schemas.md#app.schemas.user_list.UserListRequest.offset)
      * [`UserListRequest.order`](app.schemas.md#app.schemas.user_list.UserListRequest.order)
      * [`UserListRequest.order_by`](app.schemas.md#app.schemas.user_list.UserListRequest.order_by)
      * [`UserListRequest.role__eq`](app.schemas.md#app.schemas.user_list.UserListRequest.role__eq)
      * [`UserListRequest.username__ilike`](app.schemas.md#app.schemas.user_list.UserListRequest.username__ilike)
    * [`UserListResponse`](app.schemas.md#app.schemas.user_list.UserListResponse)
      * [`UserListResponse.model_config`](app.schemas.md#app.schemas.user_list.UserListResponse.model_config)
      * [`UserListResponse.users`](app.schemas.md#app.schemas.user_list.UserListResponse.users)
      * [`UserListResponse.users_count`](app.schemas.md#app.schemas.user_list.UserListResponse.users_count)
  * [app.schemas.user_login module](app.schemas.md#module-app.schemas.user_login)
    * [`UserLoginRequest`](app.schemas.md#app.schemas.user_login.UserLoginRequest)
      * [`UserLoginRequest.model_config`](app.schemas.md#app.schemas.user_login.UserLoginRequest.model_config)
      * [`UserLoginRequest.password`](app.schemas.md#app.schemas.user_login.UserLoginRequest.password)
      * [`UserLoginRequest.username`](app.schemas.md#app.schemas.user_login.UserLoginRequest.username)
    * [`UserLoginResponse`](app.schemas.md#app.schemas.user_login.UserLoginResponse)
      * [`UserLoginResponse.model_config`](app.schemas.md#app.schemas.user_login.UserLoginResponse.model_config)
      * [`UserLoginResponse.password_accepted`](app.schemas.md#app.schemas.user_login.UserLoginResponse.password_accepted)
      * [`UserLoginResponse.user_id`](app.schemas.md#app.schemas.user_login.UserLoginResponse.user_id)
  * [app.schemas.user_password module](app.schemas.md#module-app.schemas.user_password)
    * [`UserPasswordRequest`](app.schemas.md#app.schemas.user_password.UserPasswordRequest)
      * [`UserPasswordRequest.current_password`](app.schemas.md#app.schemas.user_password.UserPasswordRequest.current_password)
      * [`UserPasswordRequest.model_config`](app.schemas.md#app.schemas.user_password.UserPasswordRequest.model_config)
      * [`UserPasswordRequest.updated_password`](app.schemas.md#app.schemas.user_password.UserPasswordRequest.updated_password)
    * [`UserPasswordResponse`](app.schemas.md#app.schemas.user_password.UserPasswordResponse)
      * [`UserPasswordResponse.model_config`](app.schemas.md#app.schemas.user_password.UserPasswordResponse.model_config)
      * [`UserPasswordResponse.user_id`](app.schemas.md#app.schemas.user_password.UserPasswordResponse.user_id)
  * [app.schemas.user_register module](app.schemas.md#module-app.schemas.user_register)
    * [`UserRegisterRequest`](app.schemas.md#app.schemas.user_register.UserRegisterRequest)
      * [`UserRegisterRequest.first_name`](app.schemas.md#app.schemas.user_register.UserRegisterRequest.first_name)
      * [`UserRegisterRequest.last_name`](app.schemas.md#app.schemas.user_register.UserRegisterRequest.last_name)
      * [`UserRegisterRequest.model_config`](app.schemas.md#app.schemas.user_register.UserRegisterRequest.model_config)
      * [`UserRegisterRequest.password`](app.schemas.md#app.schemas.user_register.UserRegisterRequest.password)
      * [`UserRegisterRequest.summary`](app.schemas.md#app.schemas.user_register.UserRegisterRequest.summary)
      * [`UserRegisterRequest.username`](app.schemas.md#app.schemas.user_register.UserRegisterRequest.username)
    * [`UserRegisterResponse`](app.schemas.md#app.schemas.user_register.UserRegisterResponse)
      * [`UserRegisterResponse.mfa_secret`](app.schemas.md#app.schemas.user_register.UserRegisterResponse.mfa_secret)
      * [`UserRegisterResponse.model_config`](app.schemas.md#app.schemas.user_register.UserRegisterResponse.model_config)
      * [`UserRegisterResponse.user_id`](app.schemas.md#app.schemas.user_register.UserRegisterResponse.user_id)
  * [app.schemas.user_role module](app.schemas.md#module-app.schemas.user_role)
    * [`UserRoleRequest`](app.schemas.md#app.schemas.user_role.UserRoleRequest)
      * [`UserRoleRequest.active`](app.schemas.md#app.schemas.user_role.UserRoleRequest.active)
      * [`UserRoleRequest.model_config`](app.schemas.md#app.schemas.user_role.UserRoleRequest.model_config)
      * [`UserRoleRequest.role`](app.schemas.md#app.schemas.user_role.UserRoleRequest.role)
      * [`UserRoleRequest.validate_role()`](app.schemas.md#app.schemas.user_role.UserRoleRequest.validate_role)
    * [`UserRoleResponse`](app.schemas.md#app.schemas.user_role.UserRoleResponse)
      * [`UserRoleResponse.model_config`](app.schemas.md#app.schemas.user_role.UserRoleResponse.model_config)
      * [`UserRoleResponse.user_id`](app.schemas.md#app.schemas.user_role.UserRoleResponse.user_id)
  * [app.schemas.user_select module](app.schemas.md#module-app.schemas.user_select)
    * [`UserSelectResponse`](app.schemas.md#app.schemas.user_select.UserSelectResponse)
      * [`UserSelectResponse.active`](app.schemas.md#app.schemas.user_select.UserSelectResponse.active)
      * [`UserSelectResponse.created_date`](app.schemas.md#app.schemas.user_select.UserSelectResponse.created_date)
      * [`UserSelectResponse.first_name`](app.schemas.md#app.schemas.user_select.UserSelectResponse.first_name)
      * [`UserSelectResponse.has_thumbnail`](app.schemas.md#app.schemas.user_select.UserSelectResponse.has_thumbnail)
      * [`UserSelectResponse.id`](app.schemas.md#app.schemas.user_select.UserSelectResponse.id)
      * [`UserSelectResponse.last_login_date`](app.schemas.md#app.schemas.user_select.UserSelectResponse.last_login_date)
      * [`UserSelectResponse.last_name`](app.schemas.md#app.schemas.user_select.UserSelectResponse.last_name)
      * [`UserSelectResponse.model_config`](app.schemas.md#app.schemas.user_select.UserSelectResponse.model_config)
      * [`UserSelectResponse.role`](app.schemas.md#app.schemas.user_select.UserSelectResponse.role)
      * [`UserSelectResponse.summary`](app.schemas.md#app.schemas.user_select.UserSelectResponse.summary)
      * [`UserSelectResponse.username`](app.schemas.md#app.schemas.user_select.UserSelectResponse.username)
  * [app.schemas.user_update module](app.schemas.md#module-app.schemas.user_update)
    * [`UserUpdateRequest`](app.schemas.md#app.schemas.user_update.UserUpdateRequest)
      * [`UserUpdateRequest.first_name`](app.schemas.md#app.schemas.user_update.UserUpdateRequest.first_name)
      * [`UserUpdateRequest.last_name`](app.schemas.md#app.schemas.user_update.UserUpdateRequest.last_name)
      * [`UserUpdateRequest.model_config`](app.schemas.md#app.schemas.user_update.UserUpdateRequest.model_config)
      * [`UserUpdateRequest.summary`](app.schemas.md#app.schemas.user_update.UserUpdateRequest.summary)
    * [`UserUpdateResponse`](app.schemas.md#app.schemas.user_update.UserUpdateResponse)
      * [`UserUpdateResponse.model_config`](app.schemas.md#app.schemas.user_update.UserUpdateResponse.model_config)
      * [`UserUpdateResponse.user_id`](app.schemas.md#app.schemas.user_update.UserUpdateResponse.user_id)
  * [app.schemas.userpic_delete module](app.schemas.md#module-app.schemas.userpic_delete)
    * [`UserpicDeleteResponse`](app.schemas.md#app.schemas.userpic_delete.UserpicDeleteResponse)
      * [`UserpicDeleteResponse.model_config`](app.schemas.md#app.schemas.userpic_delete.UserpicDeleteResponse.model_config)
      * [`UserpicDeleteResponse.user_id`](app.schemas.md#app.schemas.userpic_delete.UserpicDeleteResponse.user_id)
  * [app.schemas.userpic_upload module](app.schemas.md#module-app.schemas.userpic_upload)
    * [`UserpicUploadResponse`](app.schemas.md#app.schemas.userpic_upload.UserpicUploadResponse)
      * [`UserpicUploadResponse.model_config`](app.schemas.md#app.schemas.userpic_upload.UserpicUploadResponse.model_config)
      * [`UserpicUploadResponse.user_id`](app.schemas.md#app.schemas.userpic_upload.UserpicUploadResponse.user_id)
  * [Module contents](app.schemas.md#module-app.schemas)
* [app.validators package](app.validators.md)
  * [app.validators.file_validators module](app.validators.md#module-app.validators.file_validators)
    * [`name_validate()`](app.validators.md#app.validators.file_validators.name_validate)
    * [`summary_validate()`](app.validators.md#app.validators.file_validators.summary_validate)
  * [app.validators.folder_validators module](app.validators.md#module-app.validators.folder_validators)
    * [`summary_validate()`](app.validators.md#app.validators.folder_validators.summary_validate)
  * [app.validators.tag_validators module](app.validators.md#module-app.validators.tag_validators)
    * [`value_validate()`](app.validators.md#app.validators.tag_validators.value_validate)
  * [app.validators.user_validators module](app.validators.md#module-app.validators.user_validators)
    * [`password_validate()`](app.validators.md#app.validators.user_validators.password_validate)
    * [`role_validate()`](app.validators.md#app.validators.user_validators.role_validate)
    * [`summary_validate()`](app.validators.md#app.validators.user_validators.summary_validate)
    * [`totp_validate()`](app.validators.md#app.validators.user_validators.totp_validate)
    * [`username_validate()`](app.validators.md#app.validators.user_validators.username_validate)
  * [Module contents](app.validators.md#module-app.validators)

## app.app module

Hidden — main application module.

This module assembles the FastAPI application, connects core services,
mounts all routers, and defines global behavior. On startup, it loads
configuration, opens database and cache connections, and places shared
components into the application state. If lockdown mode is enabled, it
is forcibly disabled. On shutdown, all resources are released cleanly.

For every request, assign a UUID, measure and log duration, check the
lockdown state, and validate the gocryptfs key. Request logging is
enabled at DEBUG level.

Errors are handled centrally to produce consistent JSON. Returns 422 for
validation; 498/499 for gocryptfs-key issues; 423 for lockdown mode; 409
for file conflicts; 401/403 for auth errors. All other exceptions become
500. Every non-validation issue is logged with elapsed time and a stack
trace, and the response includes the request UUID (X-Request-ID). Error
logging is enabled at ERROR level.

### app.app.add_cors_headers(response: JSONResponse) → JSONResponse

Add headers to the response to allow cross-origin requests from any
source. This ensures that the response can be accessed by clients
from different domains, supports all HTTP methods and headers.

### *async* app.app.catch_all(full_path: str, request: Request)

Serves static files. Returns the main HTML file if no specific
path is provided, or serves the requested file if it exists.

### *async* app.app.exception_handler(request: Request, e: Exception)

Handles exceptions and returns consistent JSON errors; logs elapsed
time (with stack trace for server errors) and appends X-Request-ID.

### app.app.lifespan(app: FastAPI)

Initializes core services and a shared file manager on startup. On
shutdown, disposes database resources and closes cache connections.

### *async* app.app.middleware_handler(request: Request, call_next)

Binds a request-scoped logger, logs request timing, checks lockdown
state, reads the gocryptfs key, appends X-Request-ID to the response.

## app.auth module

Provides authentication and permission checks based on JWT tokens,
mapping user roles to functions that validate their access rights
and raising detailed errors on invalid or expired tokens.

### app.auth.auth(user_role: [UserRole](app.models.md#app.models.user.UserRole)) → Callable

Returns a FastAPI dependency enforcing permissions for the specified
role by mapping application roles to permission-check functions that
gate access to protected routes.

## app.config module

Defines the application configuration as a dataclass and loads values
from an .env file using the python-dotenv library, converting them
to the appropriate types; uses lru_cache to memoize the resulting
configuration object for efficient reuse.

### *class* app.config.Config(GOCRYPTFS_PASSPHRASE_PATH: str, GOCRYPTFS_PASSPHRASE_LENGTH: int, GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS: int, GOCRYPTFS_DATA_MOUNTPOINT: str, GOCRYPTFS_DATA_CIPHER_DIR: str, CRYPTO_KEY_LENGTH: int, CRYPTO_NONCE_LENGTH: int, CRYPTO_HKDF_INFO: bytes, CRYPTO_HKDF_SALT_B64: str, CRYPTO_DERIVE_WITH_HKDF: bool, CRYPTO_DEFAULT_ENCODING: str, CRYPTO_AAD_DEFAULT: bytes, LOCK_FILE_PATH: str, LOG_LEVEL: str, LOG_NAME: str, LOG_FORMAT: str, LOG_FILENAME: str, LOG_FILESIZE: int, LOG_FILES_LIMIT: int, UVICORN_HOST: str, UVICORN_PORT: int, UVICORN_WORKERS: int, SQLITE_PATH: str, SQLITE_POOL_SIZE: int, SQLITE_POOL_OVERFLOW: int, SQLITE_SQL_ECHO: bool, REDIS_ENABLED: bool, REDIS_HOST: str, REDIS_PORT: int, REDIS_DECODE_RESPONSES: bool, REDIS_EXPIRE: int, LRU_TOTAL_SIZE_BYTES: int, LRU_ITEM_SIZE_LIMIT_BYTES: int, FILE_CHUNK_SIZE: int, FILE_SHRED_CYCLES: int, FILE_DEFAULT_MIMETYPE: str, JTI_LENGTH: int, JWT_ALGORITHMS: list, JWT_SECRET: str, ADDONS_PATH: str, ADDONS_LIST: list, AUTH_PASSWORD_ATTEMPTS: int, AUTH_TOTP_ATTEMPTS: int, AUTH_SUSPENDED_TIME: int, FILES_DIR: str, REVISIONS_DIR: str, TEMPORARY_DIR: str, THUMBNAILS_DIR: str, THUMBNAILS_WIDTH: int, THUMBNAILS_HEIGHT: int, THUMBNAILS_QUALITY: int, HTML_PATH: str, HTML_FILE: str)

Bases: `object`

Strongly typed configuration where field names must match keys
in the .env file; values are trimmed and converted according to
their annotated types.

#### ADDONS_LIST *: list*

#### ADDONS_PATH *: str*

#### AUTH_PASSWORD_ATTEMPTS *: int*

#### AUTH_SUSPENDED_TIME *: int*

#### AUTH_TOTP_ATTEMPTS *: int*

#### CRYPTO_AAD_DEFAULT *: bytes*

#### CRYPTO_DEFAULT_ENCODING *: str*

#### CRYPTO_DERIVE_WITH_HKDF *: bool*

#### CRYPTO_HKDF_INFO *: bytes*

#### CRYPTO_HKDF_SALT_B64 *: str*

#### CRYPTO_KEY_LENGTH *: int*

#### CRYPTO_NONCE_LENGTH *: int*

#### FILES_DIR *: str*

#### FILE_CHUNK_SIZE *: int*

#### FILE_DEFAULT_MIMETYPE *: str*

#### FILE_SHRED_CYCLES *: int*

#### GOCRYPTFS_DATA_CIPHER_DIR *: str*

#### GOCRYPTFS_DATA_MOUNTPOINT *: str*

#### GOCRYPTFS_PASSPHRASE_LENGTH *: int*

#### GOCRYPTFS_PASSPHRASE_PATH *: str*

#### GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS *: int*

#### HTML_FILE *: str*

#### HTML_PATH *: str*

#### JTI_LENGTH *: int*

#### JWT_ALGORITHMS *: list*

#### JWT_SECRET *: str*

#### LOCK_FILE_PATH *: str*

#### LOG_FILENAME *: str*

#### LOG_FILESIZE *: int*

#### LOG_FILES_LIMIT *: int*

#### LOG_FORMAT *: str*

#### LOG_LEVEL *: str*

#### LOG_NAME *: str*

#### LRU_ITEM_SIZE_LIMIT_BYTES *: int*

#### LRU_TOTAL_SIZE_BYTES *: int*

#### REDIS_DECODE_RESPONSES *: bool*

#### REDIS_ENABLED *: bool*

#### REDIS_EXPIRE *: int*

#### REDIS_HOST *: str*

#### REDIS_PORT *: int*

#### REVISIONS_DIR *: str*

#### SQLITE_PATH *: str*

#### SQLITE_POOL_OVERFLOW *: int*

#### SQLITE_POOL_SIZE *: int*

#### SQLITE_SQL_ECHO *: bool*

#### TEMPORARY_DIR *: str*

#### THUMBNAILS_DIR *: str*

#### THUMBNAILS_HEIGHT *: int*

#### THUMBNAILS_QUALITY *: int*

#### THUMBNAILS_WIDTH *: int*

#### UVICORN_HOST *: str*

#### UVICORN_PORT *: int*

#### UVICORN_WORKERS *: int*

### app.config.get_config() → [Config](#app.config.Config)

Loads configuration settings from an .env file and returns them as
a Config dataclass instance. The function uses type annotations to
convert the environment variable values to their appropriate types,
such as bool, int, list, str or bytes.

## app.constants module

## app.error module

Centralized error definitions and HTTPException wrapper ensuring
consistent error codes and unified response format across the API.

### *exception* app.error.E(loc: list, error_input: str, error_type: str, status_code: int)

Bases: `HTTPException`

Unified HTTPException wrapper that produces error details in the
same shape as Pydantic validation errors.

## app.hook module

Provides an application hook system: loads add-on modules listed in the
config, discovers async handlers named after known hooks, and registers
them for post-event execution.

### *class* app.hook.Hook(request: Request, session: AsyncSession, cache: Redis, current_user: [User](app.models.md#app.models.user.User))

Bases: `object`

Executes registered hook handlers from app state, passing the
request session, Redis cache, the current user, and any extra
arguments.

#### *async* call(hook: str, \*args, \*\*kwargs)

Runs all handlers registered for the given hook in order,
passing session, cache, current user, and provided args/kwargs.

### app.hook.init_hooks(app: FastAPI) → None

Builds the hook registry by importing add-on modules from the
configured path and registering async functions whose names match
constants in enabled hooks.

## app.log module

Initializes application logging with a concurrent-safe rotating file
handler. Applies formatter and level from the app, attaches the handler
only once, disables propagation to prevent duplicate output, stores the
logger on app state, and returns the ready-to-use instance.

### app.log.init_logger(app: FastAPI) → Logger

Creates a logger from config, attaches a rotating handler,
sets level, stores it in app state, and returns it.

## app.lru module

Byte-oriented LRU cache keyed by strings. Enforces a global capacity
with an optional per-item cap, promotes entries on access, and evicts
the least-recently used until within budget. Supports insert/update,
fetch with recency bump, removal, and full clear, and exposes live
size and item count properties.

### *class* app.lru.LRU(cache_size_bytes: int, item_size_bytes: int | None = None)

Bases: `object`

LRU cache that stores bytes under string keys.
Limited both by total size in bytes and optional per-item size.

#### clear() → None

Clear cache completely.

#### *property* count *: int*

Number of cached entries.

#### delete(path: str) → None

Remove a key if present.

#### load(path: str) → bytes | None

Return cached value or None if not found.

#### save(path: str, value: bytes) → None

Insert or update a key, enforcing size limits.

#### *property* size *: int*

Total size of all cached entries in bytes.

## app.redis module

Provides an asynchronous Redis client managed via FastAPI lifespan:
the client is created from runtime settings, stored in app.state for
reuse, exposed through a request-scoped dependency, and optionally
initialized on startup.

### *class* app.redis.RedisClient(, host: str, port: int, decode_responses: bool = True)

Bases: `object`

Holds a shared asyncio Redis client built from configuration and
intended to be instantiated during application startup and reused
across requests via app.state.

#### *async* close() → None

Close the underlying connection pool on application shutdown.

### *async* app.redis.get_cache(request: Request) → AsyncGenerator[Redis, None]

Yield the shared Redis client from app.state without closing it per
request so the connection pool can be reused efficiently across the
application.

### *async* app.redis.init_cache(client: [RedisClient](#app.redis.RedisClient)) → None

Optionally initialize the cache by checking connectivity and
performing startup tasks like a database flush if desired.

## app.repository module

Defines a repository class that manages CRUD operations and caching for
SQLAlchemy models using an asynchronous session for database operations
and Redis for cache storage. Provides methods for existence checks,
insertion, selection, updating, deletion, counting, summation, and
transaction management with commit and rollback.

### *class* app.repository.Repository(session: AsyncSession, cache: Redis, entity_class: Type[DeclarativeBase], config: [Config](#app.config.Config))

Bases: `object`

Provides a unified interface for performing CRUD operations on
SQLAlchemy models with integrated Redis caching.

#### *async* commit()

Commits the current transaction for pending changes in the
database.

#### *async* count_all(\*\*kwargs) → int

Counts the number of SQLAlchemy models that match the given
criteria.

#### *async* delete(entity: DeclarativeBase, commit: bool = True)

Deletes an entity from the database and removes its entry from
the cache if caching is enabled.

#### *async* delete_all(commit: bool = False, \*\*kwargs)

Deletes all SQLAlchemy models from the database  and cache that
match the given criteria.

#### *async* delete_all_from_cache()

Deletes all entities of the managed SQLAlchemy model matching
the criteria from the database and clears them from the cache.

#### *async* delete_from_cache(entity: DeclarativeBase)

Deletes an entity of the managed SQLAlchemy model from the cache
without affecting the database.

#### *async* exists(\*\*kwargs) → bool

Checks if a SQLAlchemy model matching the given criteria exists
in the database.

#### *async* insert(entity: DeclarativeBase, commit: bool = True)

Inserts a new entity of the managed SQLAlchemy model into the
database.

#### *async* rollback()

Rolls back the current transaction, discarding pending changes
in case of errors or inconsistencies.

#### *async* select(\*\*kwargs) → DeclarativeBase | None

Retrieves a SQLAlchemy model based on the provided criteria
or its ID.

#### *async* select_all(\*\*kwargs) → List[DeclarativeBase]

Retrieves all SQLAlchemy models from the database that match
the given criteria.

#### *async* sum_all(column_name: str, \*\*kwargs) → int

Calculates the sum of a specific column for all SQLAlchemy
models matching the criteria.

#### *async* update(entity: DeclarativeBase, commit: bool = True)

Updates an existing SQLAlchemy model in the database and
deletes from cache.

## app.rwlock module

Async reader-writer synchronization primitive with writer preference for
asyncio-based code. Allows concurrent shared access for multiple readers
while ensuring writers acquire exclusive access and preventing new
readers from entering when a writer is active or queued. Designed to be
cancellation-safe, non-reentrant, and process-local, exposing context
managers for explicit read and write critical sections.

### *class* app.rwlock.RWLock

Bases: `object`

Asyncio-friendly readers-writer lock with writer preference:
multiple readers may proceed concurrently, writers acquire
exclusive access, and new readers are blocked while any writer
is active or waiting. Non-reentrant and in-process only;
cancellation-safe.

#### read()

Acquire a shared read lock: waits while a writer is active or
queued, then yields; releases on exit and wakes waiters when
the last reader leaves.

#### write()

Acquire an exclusive write lock: announces writer intent to
block new readers, waits for current readers to drain, then
yields; releases on exit and wakes pending readers/writers.

## app.sqlite module

Sets up async SQLite engine and sessions for SQLAlchemy. The engine
and session factory are created from a Config instance and should be
constructed in FastAPI lifespan and stored in app.state.

### *class* app.sqlite.Base(\*\*kwargs: Any)

Bases: `DeclarativeBase`

#### metadata *: ClassVar[MetaData]* *= MetaData()*

Refers to the `_schema.MetaData` collection that will be used
for new `_schema.Table` objects.

#### SEE ALSO
orm_declarative_metadata

#### registry *: ClassVar[\_RegistryType]* *= <sqlalchemy.orm.decl_api.registry object>*

Refers to the `_orm.registry` in use where new
`_orm.Mapper` objects will be associated.

### *class* app.sqlite.SessionManager(, sqlite_path: str, sql_echo: bool = False)

Bases: `object`

Creates and manages the SQLite async engine and session factory
derived from runtime settings, intended to be instantiated during
application startup and reused via app.state for handling database
access.

#### *property* connection_string *: str*

Return the SQLAlchemy async URL for aiosqlite that points
at the resolved database file path.

#### *property* db_path *: str*

Return the absolute filesystem path to the database file with
user home expansion and normalization applied.

#### get_session() → AsyncSession

Return a task-scoped AsyncSession so that concurrent coroutines
receive isolated sessions bound to their current asyncio task.

### *async* app.sqlite.get_session(request: Request) → AsyncGenerator[AsyncSession, None]

Yield an AsyncSession obtained from the SessionManager stored in
app.state and wrap it in a simple unit-of-work pattern that commits
on success, rolls back on error, and always closes the session.

### *async* app.sqlite.init_database(session_manager: [SessionManager](#app.sqlite.SessionManager)) → None

Create the database schema for all mapped models by running
create_all against the async engine at application startup.

## app.version module

## Module contents
