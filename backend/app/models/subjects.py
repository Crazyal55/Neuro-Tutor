"""Pydantic and SQLAlchemy models for subjects and course materials."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.db import Base

MaterialType = Literal["pptx", "pdf", "docx", "md", "txt"]
MaterialKind = Literal["slides", "book", "notes", "homework", "other"]
MaterialStatus = Literal["pending", "processing", "ready", "failed"]


class SubjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class SubjectUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class SubjectSummary(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    material_count: int = 0


class SubjectListResponse(BaseModel):
    subjects: List[SubjectSummary]


class MaterialSummary(BaseModel):
    id: str
    subject_id: str
    filename: str
    file_type: MaterialType
    material_kind: MaterialKind
    status: MaterialStatus
    error: Optional[str] = None
    chunk_count: int = 0
    uploaded_at: datetime


class MaterialListResponse(BaseModel):
    materials: List[MaterialSummary]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    filename: str
    locator: str
    score: float
    text: str


class SearchResponse(BaseModel):
    hits: List[SearchHit]


class SourceCitation(BaseModel):
    filename: str
    locator: str
    score: float


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    materials = relationship(
        "Material",
        back_populates="subject",
        cascade="all, delete-orphan",
    )
    chat_sessions = relationship("ChatSession", back_populates="subject")


class Material(Base):
    __tablename__ = "materials"

    id = Column(String, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    material_kind = Column(String, nullable=False, default="other")
    status = Column(String, nullable=False, default="pending")
    error = Column(Text, nullable=True)
    chunk_count = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subject = relationship("Subject", back_populates="materials")
