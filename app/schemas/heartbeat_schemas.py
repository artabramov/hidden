
from pydantic import BaseModel


class HeartbeatRetrieveResponse(BaseModel):
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int
    is_locked: bool
    lock_time: int
