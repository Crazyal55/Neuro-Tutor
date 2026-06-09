"""Subjects and course materials API."""

import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.db import SessionLocal, get_db
from app.models.subjects import (
    MaterialKind,
    MaterialListResponse,
    MaterialSummary,
    SearchHit,
    SearchRequest,
    SearchResponse,
    SubjectCreateRequest,
    SubjectListResponse,
    SubjectSummary,
    SubjectUpdateRequest,
)
from app.services.ingestion import ingest_material
from app.services.retrieval import retrieve_context
from app.services.subjects_service import (
    count_materials,
    create_material_record,
    create_subject,
    delete_material,
    delete_subject,
    get_material,
    get_subject,
    list_materials,
    list_subjects,
    save_upload_file,
    update_subject,
    validate_upload,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subjects", tags=["subjects"])


def _run_ingestion(material_id: str) -> None:
    db = SessionLocal()
    try:
        ingest_material(db, material_id)
    finally:
        db.close()


@router.post("/", response_model=SubjectSummary, status_code=status.HTTP_201_CREATED)
async def create_subject_endpoint(
    request: SubjectCreateRequest,
    db: Session = Depends(get_db),
) -> SubjectSummary:
    subject = create_subject(db, request.name, request.description)
    return SubjectSummary(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        created_at=subject.created_at,
        material_count=0,
    )


@router.get("/", response_model=SubjectListResponse)
async def list_subjects_endpoint(db: Session = Depends(get_db)) -> SubjectListResponse:
    subjects = list_subjects(db)
    return SubjectListResponse(
        subjects=[
            SubjectSummary(
                id=subject.id,
                name=subject.name,
                description=subject.description,
                created_at=subject.created_at,
                material_count=count_materials(db, subject.id),
            )
            for subject in subjects
        ]
    )


@router.patch("/{subject_id}", response_model=SubjectSummary)
async def update_subject_endpoint(
    subject_id: str,
    request: SubjectUpdateRequest,
    db: Session = Depends(get_db),
) -> SubjectSummary:
    subject = update_subject(db, subject_id, request.name, request.description)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSummary(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        created_at=subject.created_at,
        material_count=count_materials(db, subject.id),
    )


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject_endpoint(subject_id: str, db: Session = Depends(get_db)) -> None:
    if not delete_subject(db, subject_id):
        raise HTTPException(status_code=404, detail="Subject not found")


@router.get("/{subject_id}/materials", response_model=MaterialListResponse)
async def list_materials_endpoint(
    subject_id: str,
    db: Session = Depends(get_db),
) -> MaterialListResponse:
    if get_subject(db, subject_id) is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    materials = list_materials(db, subject_id)
    return MaterialListResponse(
        materials=[
            MaterialSummary(
                id=material.id,
                subject_id=material.subject_id,
                filename=material.filename,
                file_type=material.file_type,
                material_kind=material.material_kind,
                status=material.status,
                error=material.error,
                chunk_count=material.chunk_count,
                uploaded_at=material.uploaded_at,
            )
            for material in materials
        ]
    )


@router.post("/{subject_id}/materials", response_model=MaterialSummary, status_code=status.HTTP_201_CREATED)
async def upload_material_endpoint(
    subject_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    material_kind: MaterialKind = Form(default="other"),
    db: Session = Depends(get_db),
) -> MaterialSummary:
    if get_subject(db, subject_id) is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    content = await file.read()
    try:
        file_type, _ = validate_upload(file.filename or "upload.txt", len(content))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    material = create_material_record(
        db,
        subject_id=subject_id,
        filename=file.filename or "upload.txt",
        file_path="",
        file_type=file_type,
        material_kind=material_kind,
    )

    file_path = save_upload_file(subject_id, material.id, material.filename, content)
    material.file_path = file_path
    db.commit()
    db.refresh(material)

    background_tasks.add_task(_run_ingestion, material.id)

    return MaterialSummary(
        id=material.id,
        subject_id=material.subject_id,
        filename=material.filename,
        file_type=material.file_type,
        material_kind=material.material_kind,
        status=material.status,
        error=material.error,
        chunk_count=material.chunk_count,
        uploaded_at=material.uploaded_at,
    )


@router.delete("/{subject_id}/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material_endpoint(
    subject_id: str,
    material_id: str,
    db: Session = Depends(get_db),
) -> None:
    material = get_material(db, material_id)
    if material is None or material.subject_id != subject_id:
        raise HTTPException(status_code=404, detail="Material not found")
    delete_material(db, material_id)


@router.post("/{subject_id}/search", response_model=SearchResponse)
async def search_materials_endpoint(
    subject_id: str,
    request: SearchRequest,
    db: Session = Depends(get_db),
) -> SearchResponse:
    if get_subject(db, subject_id) is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    hits, _ = retrieve_context(request.query, subject_id)
    return SearchResponse(
        hits=[
            SearchHit(
                filename=hit["filename"],
                locator=hit["locator"],
                score=hit["score"],
                text=hit["text"],
            )
            for hit in hits[: request.top_k]
        ]
    )
