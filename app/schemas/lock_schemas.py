
from pydantic import BaseModel


class LockCreateResponse(BaseModel):
    is_locked: bool


class LockDeleteResponse(BaseModel):
    is_locked: bool
