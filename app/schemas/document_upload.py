from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: int
