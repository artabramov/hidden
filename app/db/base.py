# app/db/base.py
# SPDX-License-Identifier: SSPL-1.0

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Declarative base class for all ORM models.
    Registers models in the shared SQLAlchemy metadata.
    """
    pass
