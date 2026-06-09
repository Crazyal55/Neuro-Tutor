"""Database operations for subjects and materials."""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.vector_db import delete_by_material_id, delete_by_subject_id
from app.models.subjects import Material, Subject
from app.services.ingestion import detect_file_type


def create_subject(db: Session, name: str, description: Optional[str] = None) -> Subject:
    subject = Subject(
        id=str(uuid.uuid4()),
        name=name.strip(),
        description=description,
        created_at=datetime.utcnow(),
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def list_subjects(db: Session) -> List[Subject]:
    return db.query(Subject).order_by(Subject.created_at.desc()).all()


def get_subject(db: Session, subject_id: str) -> Optional[Subject]:
    return db.query(Subject).filter(Subject.id == subject_id).first()


def update_subject(
    db: Session,
    subject_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Subject]:
    subject = get_subject(db, subject_id)
    if subject is None:
        return None

    if name is not None:
        subject.name = name.strip()
    if description is not None:
        subject.description = description
    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject_id: str) -> bool:
    subject = get_subject(db, subject_id)
    if subject is None:
        return False

    delete_by_subject_id(subject_id)
    upload_dir = Path(settings.uploads_dir) / subject_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)

    db.delete(subject)
    db.commit()
    return True


def count_materials(db: Session, subject_id: str) -> int:
    return db.query(Material).filter(Material.subject_id == subject_id).count()


def list_materials(db: Session, subject_id: str) -> List[Material]:
    return (
        db.query(Material)
        .filter(Material.subject_id == subject_id)
        .order_by(Material.uploaded_at.desc())
        .all()
    )


def get_material(db: Session, material_id: str) -> Optional[Material]:
    return db.query(Material).filter(Material.id == material_id).first()


def create_material_record(
    db: Session,
    subject_id: str,
    filename: str,
    file_path: str,
    file_type: str,
    material_kind: str,
) -> Material:
    material = Material(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        material_kind=material_kind,
        status="pending",
        chunk_count=0,
        uploaded_at=datetime.utcnow(),
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, material_id: str) -> bool:
    material = get_material(db, material_id)
    if material is None:
        return False

    delete_by_material_id(material_id)
    file_path = Path(material.file_path)
    if file_path.exists():
        file_path.unlink(missing_ok=True)

    db.delete(material)
    db.commit()
    return True


def save_upload_file(subject_id: str, material_id: str, filename: str, content: bytes) -> str:
    upload_dir = Path(settings.uploads_dir) / subject_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{material_id}_{Path(filename).name}"
    destination.write_bytes(content)
    return str(destination)


def validate_upload(filename: str, size: int) -> tuple[str, str]:
    file_type = detect_file_type(filename)
    if file_type is None:
        raise ValueError("Unsupported file type. Allowed: pptx, pdf, docx, md, txt")
    if size > settings.upload_max_bytes:
        raise ValueError("File exceeds 50 MB upload limit")
    return file_type, file_type
