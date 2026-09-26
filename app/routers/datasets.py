from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _get_or_404(db: Session, dataset_id: int) -> models.Dataset:
    dataset = db.get(models.Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dataset não encontrado")
    return dataset


@router.post("", response_model=schemas.DatasetDetail, status_code=status.HTTP_201_CREATED)
def create_dataset(payload: schemas.DatasetCreate, db: Session = Depends(get_db)):
    """Cria um dataset e seus registros."""
    dataset = models.Dataset(name=payload.name, description=payload.description)
    dataset.records = [models.DataRecord(**r.model_dump()) for r in payload.records]
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("", response_model=schemas.DatasetList)
def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str | None = Query(None, description="Filtro por nome (case-insensitive)"),
    db: Session = Depends(get_db),
):
    """Lista datasets com paginação e filtro opcional por nome."""
    count_stmt = select(func.count(models.Dataset.id))
    stmt = select(models.Dataset)
    if name:
        pattern = f"%{name}%"
        count_stmt = count_stmt.where(models.Dataset.name.ilike(pattern))
        stmt = stmt.where(models.Dataset.name.ilike(pattern))

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(models.Dataset.id).offset(skip).limit(limit)
    ).all()
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/{dataset_id}", response_model=schemas.DatasetDetail)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Detalha um dataset e seus registros."""
    return _get_or_404(db, dataset_id)


@router.put("/{dataset_id}", response_model=schemas.DatasetDetail)
def update_dataset(
    dataset_id: int, payload: schemas.DatasetUpdate, db: Session = Depends(get_db)
):
    """Atualiza nome/descrição de um dataset."""
    dataset = _get_or_404(db, dataset_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dataset, field, value)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Remove um dataset e seus registros em cascata."""
    dataset = _get_or_404(db, dataset_id)
    db.delete(dataset)
    db.commit()


@router.get("/{dataset_id}/records", response_model=list[schemas.RecordOut])
def list_records(
    dataset_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lista os registros de um dataset (paginado)."""
    _get_or_404(db, dataset_id)
    stmt = (
        select(models.DataRecord)
        .where(models.DataRecord.dataset_id == dataset_id)
        .order_by(models.DataRecord.id)
        .offset(skip)
        .limit(limit)
    )
    return db.scalars(stmt).all()
