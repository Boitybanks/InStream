from __future__ import annotations

import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from instream_analytics import summary as analytics_summary
from instream_auth import get_current_tenant
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()


@router.get("/summary")
def get_summary(
    start: date | None = None,
    end: date | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> dict:
    end = end or date.today()
    start = start or (end - timedelta(days=30))
    return analytics_summary(db, tenant_id=tenant_id, start=start, end=end)
