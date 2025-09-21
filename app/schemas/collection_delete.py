from pydantic import BaseModel


class CollectionDeleteResponse(BaseModel):
    collection_id: int
