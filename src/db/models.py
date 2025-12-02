# src/db/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    versions = relationship("DocumentVersion", back_populates="document")
    comparisons = relationship("Comparison", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_label = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_by = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="versions")
    comparisons_old = relationship(
        "Comparison",
        foreign_keys="Comparison.version_old_id",
        back_populates="version_old",
    )
    comparisons_new = relationship(
        "Comparison",
        foreign_keys="Comparison.version_new_id",
        back_populates="version_new",
    )


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_old_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False)
    version_new_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    overall_risk_level = Column(String(20), nullable=True)
    summary_text = Column(Text, nullable=True)

    document = relationship("Document", back_populates="comparisons")
    version_old = relationship("DocumentVersion", foreign_keys=[version_old_id])
    version_new = relationship("DocumentVersion", foreign_keys=[version_new_id])

    changes = relationship("ChangeItem", back_populates="comparison")


class ChangeItem(Base):
    __tablename__ = "changes"

    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"), nullable=False)

    change_type = Column(String(20), nullable=False)  # ADDED / REMOVED / MODIFIED
    section_label = Column(String(255), nullable=True)

    old_text = Column(Text, nullable=True)
    new_text = Column(Text, nullable=True)

    risk_level = Column(String(20), nullable=True)
    ai_comment = Column(Text, nullable=True)

    comparison = relationship("Comparison", back_populates="changes")
