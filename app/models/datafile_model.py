import os
import time
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config

cfg = get_config()


class Datafile(Base):
    __tablename__ = "datafiles"
    _cacheable = True

    # Currently, it's not possible to establish a relationship here,
    # so manual handling of latest_revision is required.
    latest_revision = None

    id = Column(BigInteger, primary_key=True)
    created_date = Column(
        Integer, index=True, default=lambda: int(time.time()))
    updated_date = Column(
        Integer, index=True, onupdate=lambda: int(time.time()), default=0)
    user_id = Column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    collection_id = Column(
        BigInteger, ForeignKey("collections.id"), index=True, nullable=True)
    member_id = Column(
        BigInteger, ForeignKey("members.id"), index=True, nullable=True)
    latest_revision_id = Column(BigInteger, index=True, nullable=True)
    datafile_name = Column(String(256), nullable=True)
    datafile_summary = Column(String(512), nullable=True)

    comments_count = Column(Integer, index=True, default=0)
    revisions_count = Column(Integer, index=True, default=0)
    revisions_size = Column(Integer, index=True, default=0)
    downloads_count = Column(Integer, index=True, default=0)

    datafile_user = relationship(
        "User", back_populates="user_datafiles", lazy="joined")

    datafile_collection = relationship(
        "Collection", back_populates="collection_datafiles", lazy="joined")

    datafile_member = relationship(
        "Member", back_populates="member_datafiles", lazy="joined")

    datafile_tags = relationship(
        "Tag", back_populates="tag_datafile", lazy="joined",
        cascade="all, delete-orphan")

    datafile_revisions = relationship(
        "Revision", back_populates="revision_datafile",
        cascade="all, delete-orphan")

    datafile_comments = relationship(
        "Comment", back_populates="comment_datafile",
        cascade="all, delete-orphan")

    datafile_downloads = relationship(
        "Download", back_populates="download_datafile",
        cascade="all, delete-orphan")

    datafile_favorites = relationship(
        "Favorite", back_populates="favorite_datafile",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, datafile_name: str,
                 collection_id: int = None, revisions_count: int = 0,
                 revisions_size: int = 0):
        self.user_id = user_id
        self.datafile_name = datafile_name
        self.collection_id = collection_id
        self.comments_count = 0
        self.revisions_count = revisions_count
        self.revisions_size = revisions_size
        self.downloads_count = 0

    @property
    def is_locked(self) -> bool:
        return (self.collection_id is not None and
                self.datafile_collection.is_locked)

    @property
    def file_path(self):
        return os.path.join(cfg.REVISIONS_BASE_PATH, self.filename)

    @property
    def tag_values(self) -> list:
        if self.datafile_tags:
            return [x.tag_value for x in self.datafile_tags]
        return []

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "collection_id": self.collection_id,
            "member_id": self.member_id,

            "datafile_name": self.datafile_name,
            "datafile_summary": self.datafile_summary,

            "comments_count": self.comments_count,
            "revisions_count": self.revisions_count,
            "revisions_size": self.revisions_size,
            "downloads_count": self.downloads_count,

            "datafile_tags": self.tag_values,
            "datafile_user": self.datafile_user.to_dict(),
            "latest_revision": self.latest_revision.to_dict(),
        }
