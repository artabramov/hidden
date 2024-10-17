import time
from fastapi import Request
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, String, Text
from app.database import Base
from app.models.user_model import User
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.context import get_context

ctx = get_context()


class Log(Base):
    __tablename__ = "users_logs"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    remote_address = Column(String(128), nullable=True)
    user_agent = Column(Text, nullable=True)

    def __init__(self, user: User, request: Request):
        self.user_id = user.id
        self.remote_address = self.get_remote_address(request)
        self.user_agent = self.get_user_agent(request)

    def get_remote_address(self, request: Request):
        if request.headers.get("x-forwarded-for"):
            return request.headers.get("x-forwarded-for").split(",")[0]
        else:
            return request.client.host

    def get_user_agent(self, request: Request):
        return ctx.request.headers.get("user-agent")


async def after_token_select(
    entity_manager: EntityManager, cache_manager: CacheManager,
    current_user: None, user: User
):
    """
    Executes after a token is retrieved. Receives the user
    entity and performs any necessary post-processing actions.
    """
    log = Log(current_user, ctx.request)
    await entity_manager.insert(log)
