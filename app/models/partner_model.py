
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


class Partner(Base):
    __tablename__ = "partners"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True,
                          onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)

    partner_name = Column(String(256), index=True, unique=True)
    partner_summary = Column(String(512), nullable=True)
    partner_contacts = Column(String(512), nullable=True)
    emblem_filename = Column(String(128), nullable=True, unique=True)

    partner_user = relationship(
        "User", back_populates="user_partners", lazy="joined")

    partner_documents = relationship(
        "Document", back_populates="document_partner")

    def __init__(self, user_id: int, partner_name: str,
                 partner_summary: str = None, partner_contacts: str = None):
        self.user_id = user_id
        self.partner_name = partner_name
        self.partner_summary = partner_summary
        self.partner_contacts = partner_contacts

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
            "partner_name": self.partner_name,
            "partner_summary": self.partner_summary,
            "partner_contacts": self.partner_contacts,
            "emblem_url": self.emblem_url,
            "partner_user": self.partner_user.to_dict(),
        }


@event.listens_for(Partner, "after_delete")
def after_delete_listener(mapper, connection, partner: Partner):
    if partner.emblem_filename:
        asyncio.get_event_loop().create_task(delete_emblem(partner))


async def delete_emblem(partner: Partner):
    try:
        await FileManager.delete(partner.emblem_path)

    except Exception as e:
        log.error("File deletion failed; module=partner_model; "
                  "function=delete_emblem; e=%s;" % str(e))
