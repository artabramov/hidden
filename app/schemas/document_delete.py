from pydantic import BaseModel


class DocumentDeleteResponse(BaseModel):
    document_id: int
    latest_revision_number: int
