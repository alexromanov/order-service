from __future__ import annotations

from app.db import Base, engine
from app import models  # noqa: F401  Needed so metadata includes all models.


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
