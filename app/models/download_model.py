from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
import time

cfg = get_config()


class Download(Base):
    __tablename__ = "documents_downloads"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)
    revision_id = Column(BigInteger, ForeignKey("documents_revisions.id"),
                         index=True)

    download_user = relationship(
        "User", back_populates="user_downloads", lazy="joined")

    download_document = relationship(
        "Document", back_populates="document_downloads", lazy="joined")

    download_revision = relationship(
        "Revision", back_populates="revision_downloads", lazy="joined")

    def __init__(self, user_id: int, document_id: int, revision_id: int):
        self.user_id = user_id
        self.document_id = document_id
        self.revision_id = revision_id

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "revision_id": self.revision_id,
            "download_user": self.download_user.to_dict(),
        }
