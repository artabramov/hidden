
import time
import os
from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, String, event
from app.config import get_config
from app.database import Base
import asyncio
from app.log import get_log
from app.managers.file_manager import FileManager

cfg = get_config()
log = get_log()


class Member(Base):
    __tablename__ = "members"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True,
                          onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)

    member_name = Column(String(256), index=True, unique=True)
    member_summary = Column(String(512), nullable=True)
    member_contacts = Column(String(512), nullable=True)
    emblem_filename = Column(String(128), nullable=True, unique=True)

    member_user = relationship(
        "User", back_populates="user_members", lazy="joined")

    member_documents = relationship(
        "Document", back_populates="document_member")

    def __init__(self, user_id: int, member_name: str,
                 member_summary: str = None, member_contacts: str = None):
        self.user_id = user_id
        self.member_name = member_name
        self.member_summary = member_summary
        self.member_contacts = member_contacts

    @property
    def emblem_url(self):
        if self.emblem_filename:
            return cfg.EMBLEM_BASE_URL + self.emblem_filename

    @property
    def emblem_path(self):
        if self.emblem_filename:
            return os.path.join(cfg.EMBLEM_BASE_PATH,
                                self.emblem_filename)

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "member_name": self.member_name,
            "member_summary": self.member_summary,
            "member_contacts": self.member_contacts,
            "emblem_url": self.emblem_url,
            "member_user": self.member_user.to_dict(),
        }


@event.listens_for(Member, "after_delete")
def after_delete_listener(mapper, connection, member: Member):
    if member.emblem_filename:
        asyncio.get_event_loop().create_task(delete_emblem(member))


async def delete_emblem(member: Member):
    try:
        await FileManager.delete(member.emblem_path)

    except Exception as e:
        log.error("File deletion failed; module=member_model; "
                  "function=delete_emblem; e=%s;" % str(e))
