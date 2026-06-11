# app/db/base.py
# SPDX-License-Identifier: GPL-3.0-only

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Declarative base class for all ORM models.
    Registers models in the shared SQLAlchemy metadata.
    """
    pass
