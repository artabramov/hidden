import time
import json
import aiohttp
import requests
from redis import Redis
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from app.models.user_model import User
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.setting_model import Setting
from app.repository import Repository
from app.error import LOC_BODY, ERR_VALUE_EMPTY, ERR_VALUE_ERROR
from app.error import E
from app.config import get_config
from app.helpers.encrypt_helper import hash_str
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.helpers.lock_helper import lock_enable, lock_disable
from app.lru import LRU

cfg = get_config()
lru = LRU(cfg.DOCUMENTS_LRU_SIZE)


class Dropbox:
    """Dropbox client to interact with the Dropbox API."""

    def __init__(self, session: AsyncSession, cache: Redis, access_token: str):
        """Initializes a new instance of the Dropbox client."""
        self.session = session
        self.cache = cache
        self.access_token = access_token

    @property
    def dropbox_headers(self):
        """Returns the necessary headers for requests to the Dropbox."""
        return {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json"}

    async def oauth(self, app_key, app_secret, redirect_uri, auth_code):
        """Sets Oauth2 synchronization."""
        return requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": app_key,
                "client_secret": app_secret,
                "redirect_uri": redirect_uri,
                "code": auth_code})
    
    async def create_folder(self, folder_name: str) -> Union[str, None]:
        """Creates a new folder in Dropbox."""
        try:
            async with aiohttp.ClientSession().post(
                "https://api.dropbox.com/2/files/create_folder_v2",
                headers=self.dropbox_headers,
                json={"path": "/" + folder_name, "autorename": False}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["metadata"]["id"]

        except Exception:
            pass
    
    async def rename_folder(self, folder_uuid: str, folder_name: str) -> None:
        """Renames an existing folder in Dropbox."""
        try:
            async with aiohttp.ClientSession().post(
                "https://api.dropbox.com/2/files/move_v2",
                headers=self.dropbox_headers,
                json={"from_path": folder_uuid, "to_path": "/" + folder_name}
            ) as response:
                pass

        except Exception:
            pass
    
    async def delete_folder(self, folder_uuid: str) -> None:
        """Deletes a folder in Dropbox."""
        try:
            async with aiohttp.ClientSession().post(
                "https://api.dropbox.com/2/files/delete_v2",
                headers=self.dropbox_headers,
                json={"path": folder_uuid}
            ) as response:
                pass

        except Exception:
            pass

    async def upload_file(self, folder_uuid: str, file_name: str,
                          file_data: bytes) -> Union[str, None]:
        """Uploads a file to Dropbox to the specified folder."""
        try:
            async with aiohttp.ClientSession().post(
                "https://content.dropboxapi.com/2/files/upload",
                headers={
                    "Authorization": "Bearer " + self.access_token,
                    "Content-Type": "application/octet-stream",
                    "Dropbox-API-Arg": json.dumps({
                        "path": f"{folder_uuid}/{file_name}",
                        "mode": "add",
                        "autorename": True,
                        "mute": False})},
                data=file_data
            ) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return data["id"]
        
        except Exception:
            return None

    async def delete_file(self, file_uuid: str) -> None:
        """Deletes a file in Dropbox."""
        try:
            async with aiohttp.ClientSession().post(
                "https://api.dropbox.com/2/files/delete_v2",
                headers=self.dropbox_headers,
                json={"path": file_uuid}
            ) as response:
                pass
        
        except Exception:
            pass

    async def move_file(self, folder_uuid: str, file_uuid: str,
                        file_name: str) -> None:
        """Moves a file in Dropbox to a new folder."""
        try:
            async with aiohttp.ClientSession().post(
                "https://api.dropbox.com/2/files/move_v2",
                headers=self.dropbox_headers,
                json={
                    "from_path": file_uuid,
                    "to_path": f"{folder_uuid}/{file_name}"}
            ) as response:
                pass

        except Exception:
            pass


async def on_execute(session: AsyncSession, cache: Redis, current_user: User,
                     action: str, params: dict, response: dict):
    """Execute custom Dropbox related actions."""
    settings = await _get_settings(session, cache, [
        "dropbox_app_key", "dropbox_app_secret", "dropbox_redirect_uri",
        "dropbox_authorization_code", "dropbox_enabled"
    ])

    # Retrieves Dropbox account parameters.
    if action == "dropbox_settings":
        response.update({
            "dropbox_app_key": settings["dropbox_app_key"],
            "dropbox_app_secret": settings["dropbox_app_secret"],
            "dropbox_redirect_uri": settings["dropbox_redirect_uri"],
            "dropbox_authorization_code": settings["dropbox_authorization_code"],
            "dropbox_enabled": settings["dropbox_enabled"],
            "account_type": "",
            "display_name": "",
            "space_used": 0,
            "space_allocated": 0})        
        
        if settings["dropbox_enabled"] == "1":
            access_token = await _get_access_token(session, cache, current_user)

            dbx_response = requests.post(
                "https://api.dropboxapi.com/2/users/get_current_account",
                headers={"Authorization": "Bearer " + access_token})

            if dbx_response.status_code == 200:
                dropbox_data = dbx_response.json()
                response["account_type"] = dropbox_data["account_type"][".tag"]
                response["display_name"] = dropbox_data["name"]["display_name"]

            dbx_response = requests.post(
                "https://api.dropboxapi.com/2/users/get_space_usage",
                headers={"Authorization": "Bearer " + access_token})

            if dbx_response.status_code == 200:
                dropbox_data = dbx_response.json()
                response["space_used"] = dropbox_data["used"]
                response["space_allocated"] = dropbox_data["allocation"]["allocated"]

    # Enables Dropbox synchronization.
    elif action == "dropbox_enable":
        if not settings["dropbox_app_key"]:
            raise E([LOC_BODY, "dropbox_app_key"], "",
                    ERR_VALUE_EMPTY, status.HTTP_422_UNPROCESSABLE_ENTITY)

        elif not settings["dropbox_app_secret"]:
            raise E([LOC_BODY, "dropbox_app_secret"], "",
                    ERR_VALUE_EMPTY, status.HTTP_422_UNPROCESSABLE_ENTITY)

        elif not settings["dropbox_redirect_uri"]:
            raise E([LOC_BODY, "dropbox_redirect_uri"], "",
                    ERR_VALUE_EMPTY, status.HTTP_422_UNPROCESSABLE_ENTITY)

        elif not settings["dropbox_authorization_code"]:
            raise E([LOC_BODY, "dropbox_authorization_code"], "",
                    ERR_VALUE_EMPTY, status.HTTP_422_UNPROCESSABLE_ENTITY)

        dbx_response = requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings["dropbox_app_key"],
                "client_secret": settings["dropbox_app_secret"],
                "redirect_uri": settings["dropbox_redirect_uri"],
                "code": settings["dropbox_authorization_code"]})

        if dbx_response.status_code != 200:
            raise E([LOC_BODY, "dropbox_authorization_code"],
                    settings["dropbox_authorization_code"], ERR_VALUE_ERROR,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)
    
        dbx_data = json.loads(dbx_response.content.decode("utf-8"))

        await _set_settings(session, cache, current_user, {
            "dropbox_enabled": "1",
            "dropbox_access_token": dbx_data["access_token"],
            "dropbox_refresh_token": dbx_data["refresh_token"],
            "dropbox_expires_in": str(dbx_data["expires_in"])})

        # Synchronization process with Dropbox begins here. Lock
        # to prevent multiple simultaneous synchronization actions.
        await lock_enable()

        dropbox = Dropbox(session, cache, dbx_data["access_token"])
        entity_manager = EntityManager(session)
        cache_manager = CacheManager(cache)

        collection_repository = Repository(session, cache, Collection)
        document_repository = Repository(session, cache, Document)
        
        collections = await collection_repository.select_all()
        for collection in collections:
            collection_uuid = collection.get_meta("dropbox_uuid")
            if not collection_uuid:
                dbx_name = str(collection.id) + " " + collection.collection_name
                dropbox_uuid = await dropbox.create_folder(dbx_name)
                collection.set_meta("dropbox_uuid", dropbox_uuid)

                await entity_manager.commit()
                await cache_manager.delete(collection)

        documents = await document_repository.select_all()
        for document in documents:
            if not document.collection_id:
                continue

            collection = await collection_repository.select(
                id=document.collection_id)
            collection_uuid = collection.get_meta("dropbox_uuid")
            if not collection_uuid:
                continue

            document_uuid = document.get_meta("dropbox_uuid")
            if not document_uuid:
                document_data = await lru.load(document.document_path)
                document_name = str(document.id) + " " + document.original_filename

                dropbox_uuid = await dropbox.upload_file(
                    collection_uuid.meta_value, document_name, document_data)

                document.set_meta("dropbox_uuid", dropbox_uuid)

                await entity_manager.commit()
                await cache_manager.delete(document)

        await lock_disable()


async def _get_access_token(session: AsyncSession, cache: Redis, current_user: None):
    """Updates and returns the Dropbox access token."""
    settings = await _get_settings(session, cache, [
        "dropbox_enabled", "dropbox_expires_in", "dropbox_access_token",
        "dropbox_refresh_token", "dropbox_app_key", "dropbox_app_secret"])
    
    if settings["dropbox_enabled"] != "1":
        return

    retention_time = int(settings["dropbox_expires_in"]) + 60
    if retention_time < int(time.time()):
        return settings["dropbox_access_token"]

    response = requests.post(
        "https://api.dropbox.com/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": settings["dropbox_refresh_token"],
        "client_id": settings["dropbox_app_key"],
        "client_secret": settings["dropbox_app_secret"]})

    if response.status_code != 200:
        return
    
    response_data = json.loads(response.content.decode("utf-8"))
    await _set_settings(session, cache, current_user, {
        "dropbox_access_token": response_data["access_token"],
        "dropbox_expires_in": str(response_data["expires_in"])})
    return response_data["access_token"]


async def after_collection_insert(session: AsyncSession, cache: Redis,
                                  current_user: User, collection: Collection):
    """Creates a new collection."""
    access_token = await _get_access_token(session, cache, current_user)
    if not access_token:
        return
    dropbox = Dropbox(session, cache, access_token)

    dbx_name = str(collection.id) + " " + collection.collection_name
    dropbox_uuid = await dropbox.create_folder(dbx_name)
    collection.set_meta("dropbox_uuid", dropbox_uuid)


async def after_collection_update(session: AsyncSession, cache: Redis,
                                  current_user: User, collection: Collection):
    """Renames an existing collection."""
    access_token = await _get_access_token(session, cache, current_user)
    if not access_token:
        return
    dropbox = Dropbox(session, cache, access_token)

    collection_uuid = collection.get_meta("dropbox_uuid")
    if not collection_uuid:
        return

    dbx_name = str(collection.id) + " " + collection.collection_name
    await dropbox.rename_folder(collection_uuid.meta_value, dbx_name)

    cache_manager = CacheManager(cache)
    await cache_manager.delete(collection)


async def after_collection_delete(session: AsyncSession, cache: Redis,
                                  current_user: User, collection: Collection):
    """Deletes an existing collection."""
    access_token = await _get_access_token(session, cache, current_user)
    if not access_token:
        return
    dropbox = Dropbox(session, cache, access_token)

    collection_uuid = collection.get_meta("dropbox_uuid")
    if not collection_uuid:
        return

    await dropbox.delete_folder(collection_uuid.meta_value)


async def after_document_upload(session: AsyncSession, cache: Redis,
                                current_user: User, document: Document):
    """Uploads a new document."""
    access_token = await _get_access_token(session, cache, current_user)
    if not access_token:
        return
    dropbox = Dropbox(session, cache, access_token)

    if not document.collection_id:
        return

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=document.collection_id)
    collection_uuid = collection.get_meta("dropbox_uuid")
    if not collection_uuid:
        return

    dbx_data = await lru.load(document.document_path)
    dbx_name = str(document.id) + " " + document.original_filename

    dropbox_uuid = await dropbox.upload_file(
        collection_uuid.meta_value, dbx_name, dbx_data)

    document.set_meta("dropbox_uuid", dropbox_uuid)


async def after_document_update(session: AsyncSession, cache: Redis,
                                current_user: User, document: Document):
    """Renames an existing document."""
    access_token = await _get_access_token(session, cache, current_user)
    if not access_token:
        return
    dropbox = Dropbox(session, cache, access_token)

    if not document.collection_id:
        return

    document_uuid = document.get_meta("dropbox_uuid")
    if not document_uuid:
        return

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=document.collection_id)
    collection_uuid = collection.get_meta("dropbox_uuid")
    if not collection_uuid:
        return

    dbx_name = str(document.id) + " " + document.original_filename
    await dropbox.move_file(
        collection_uuid.meta_value, document_uuid.meta_value, dbx_name)

    cache_manager = CacheManager(cache)
    await cache_manager.delete(document)


async def after_document_delete(session: AsyncSession, cache: Redis,
                                current_user: User, document: Document):
    """Deletes an existing document."""
    access_token = await _get_access_token(session, cache, current_user)
    if not access_token:
        return
    dropbox = Dropbox(session, cache, access_token)
    
    document_uuid = document.get_meta("dropbox_uuid")
    if not document_uuid:
        return

    await dropbox.delete_file(document_uuid.meta_value)


async def _get_settings(session, cache, setting_keys: list):
    setting_repository = Repository(session, cache, Setting)
    all_settings = await setting_repository.select_all(
        order_by="id", order="asc")

    settings = {setting_key: None for setting_key in setting_keys}

    for setting in all_settings:
        if setting.setting_key in setting_keys:
            settings[setting.setting_key] = setting.setting_value

    return settings


async def _set_settings(session, cache, user: User, settings: dict):
    """Set settings in the Repository."""
    setting_repository = Repository(session, cache, Setting)
    for setting_key in settings:
        setting_key_hash = hash_str(setting_key)
        setting = await setting_repository.select(
            setting_key_hash__eq=setting_key_hash)

        if not setting:
            setting = Setting(user.id, setting_key, settings[setting_key])
            await setting_repository.insert(setting, commit=True)

        else:
            setting.setting_value = settings[setting_key]
            await setting_repository.update(setting, commit=True)
