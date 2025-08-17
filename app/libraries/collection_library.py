import os
import uuid
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.managers.file_manager import FileManager
from app.repository import Repository
from app.lru import LRU
from app.config import get_config
from app.helpers.image_helper import images_merge
from app.helpers.encrypt_helper import encrypt_bytes, decrypt_bytes

cfg = get_config()
lru = LRU(cfg.THUMBNAILS_LRU_SIZE)


class CollectionLibrary:
    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def create_thumbnail(self, collection_id: int):
        """
        Generates a new thumbnail for a collection by selecting first
        two documents with existing thumbnails, merging their images
        into a single composite, and saving the result as the
        collection's new encrypted thumbnail. If the collection
        already has a thumbnail, it is removed before updating. The
        method uses an LRU cache to optimize thumbnail loading and
        ensures the merged image meets configured dimensions and
        quality settings.
        """
        collection_repository = Repository(
            self.session, self.cache, Collection)
        document_repository = Repository(
            self.session, self.cache, Document)

        documents = await document_repository.select_all(
            thumbnail_filename_encrypted__ne=None,
            collection_id__eq=collection_id,
            order_by="id", order="asc", offset=0, limit=2)

        if len(documents) <= 2:
            # To maintain the consistency of the documents_count, we
            # should select the model from the Postgres without the
            # cache. Therefore, instead of "id", we use "id__eq" here.
            collection = await collection_repository.select(
                id__eq=collection_id)

            if collection.thumbnail_filename:
                await FileManager.delete(collection.thumbnail_path)
                collection.thumbnail_filename = None
                await collection_repository.update(collection)

            thumbnail_filename = str(uuid.uuid4())
            thumbnail_path = os.path.join(
                cfg.THUMBNAILS_PATH, thumbnail_filename)

            documents_thumbnails = []
            for document in documents:
                if document.has_thumbnail:
                    encrypted_data = await FileManager.read(
                        document.thumbnail_path)
                    decrypted_data = decrypt_bytes(encrypted_data)
                    documents_thumbnails.append(decrypted_data)

            thumbnail_data = await images_merge(
                documents_thumbnails, cfg.THUMBNAILS_WIDTH,
                cfg.THUMBNAILS_HEIGHT, cfg.THUMBNAILS_QUALITY)

            if thumbnail_data:
                encrypted_data = encrypt_bytes(thumbnail_data)
                await FileManager.write(thumbnail_path, encrypted_data)

                collection.thumbnail_filename = thumbnail_filename
                await collection_repository.update(collection)
