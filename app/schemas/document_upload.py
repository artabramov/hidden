from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: int
    latest_revision_number: int
