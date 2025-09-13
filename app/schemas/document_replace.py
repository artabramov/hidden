from pydantic import BaseModel


class DocumentReplaceResponse(BaseModel):
    document_id: int
