from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from instream_auth import get_current_tenant
from instream_db.models import Classification, Document
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.celery_client import celery_client
from instream_api.deps import get_db

router = APIRouter()


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    attachment_id: uuid.UUID
    ocr_provider: str
    ocr_confidence: float


class ClassificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doc_type: str
    confidence: float
    model: str


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[Document]:
    return list(db.scalars(select(Document).where(Document.tenant_id == tenant_id)).all())


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/classification", response_model=ClassificationResponse)
def get_classification(
    document_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> Classification:
    classification = db.scalar(
        select(Classification)
        .where(Classification.document_id == document_id, Classification.tenant_id == tenant_id)
        .order_by(Classification.created_at.desc())
    )
    if classification is None:
        raise HTTPException(status_code=404, detail="No classification for this document")
    return classification


@router.post("/{document_id}/reclassify", status_code=202)
def reclassify_document(
    document_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> dict:
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")
    celery_client.send_task(
        "instream_worker.tasks.reclassify_document_task", args=[str(tenant_id), str(document_id)]
    )
    return {"queued": True}
