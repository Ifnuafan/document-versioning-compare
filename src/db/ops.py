# src/db/ops.py

from typing import Optional, List
from sqlalchemy.orm import Session

from .models import Document, DocumentVersion, Comparison, ChangeItem


def get_or_create_document(db: Session, name: str, category: Optional[str] = None) -> Document:
    doc = db.query(Document).filter(Document.name == name).first()
    if doc:
        return doc
    doc = Document(name=name, category=category)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def create_document_version(
    db: Session,
    document: Document,
    version_label: str,
    file_path: str,
    uploaded_by: Optional[str] = None,
) -> DocumentVersion:
    ver = DocumentVersion(
        document_id=document.id,
        version_label=version_label,
        file_path=file_path,
        uploaded_by=uploaded_by,
    )
    db.add(ver)
    db.commit()
    db.refresh(ver)
    return ver


def create_comparison(
    db: Session,
    document: Document,
    version_old: DocumentVersion,
    version_new: DocumentVersion,
    overall_risk_level: Optional[str],
    summary_text: Optional[str],
) -> Comparison:
    comp = Comparison(
        document_id=document.id,
        version_old_id=version_old.id,
        version_new_id=version_new.id,
        overall_risk_level=overall_risk_level,
        summary_text=summary_text,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp


def bulk_insert_changes(
    db: Session,
    comparison: Comparison,
    changes: List[dict],
):
    """
    changes: list ของ dict เช่น:
    {
      "change_type": "ADDED",
      "section_label": "page 3",
      "old_text": None,
      "new_text": "...",
      "risk_level": "LOW",
      "ai_comment": None,
    }
    """
    items = []
    for ch in changes:
        item = ChangeItem(
            comparison_id=comparison.id,
            change_type=ch["change_type"],
            section_label=ch.get("section_label"),
            old_text=ch.get("old_text"),
            new_text=ch.get("new_text"),
            risk_level=ch.get("risk_level"),
            ai_comment=ch.get("ai_comment"),
        )
        db.add(item)
        items.append(item)
    db.commit()
    return items
