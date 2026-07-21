from __future__ import annotations

from collections.abc import Iterator

from instream_db.session import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
