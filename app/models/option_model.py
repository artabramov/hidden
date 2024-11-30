"""
The module defines the SQLAlchemy model for the option entity, which is
used to store and manage configuration values for both the application
and its plugins within the database.
"""

import time
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Option(Base):
    """
    SQLAlchemy model for an option entity. The model is used to store
    and manage configuration values for both the application and its
    plugins within the database.
    """
    __tablename__ = "options"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True,
                          onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    option_key = Column(String(40), nullable=False, index=True, unique=True)
    option_value = Column(String(512), nullable=False, index=True)

    option_user = relationship(
        "User", back_populates="user_options", lazy="noload")

    def __init__(self, user_id: int, option_key: str, option_value: str):
        """
        Initializes an option instance with the specified user ID,
        option key, and option value.
        """
        self.user_id = user_id
        self.option_key = option_key
        self.option_value = option_value

    async def to_dict(self):
        """
        Converts the option instance to a dictionary representation,
        including all necessary attributes.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "option_key": self.option_key,
            "option_value": self.option_value,
        }
