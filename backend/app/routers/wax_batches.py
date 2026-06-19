from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/wax-batches", tags=["蜡料批次管理"])


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_wax_batches(db: Session = Depends(get_db)):
    batches = db.query(models.WaxBatch).order_by(models.WaxBatch.code).all()
    return schemas.ApiResponse(
        data={"items": [schemas.WaxBatch.model_validate(b).model_dump() for b in batches]}
    )


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def create_wax_batch(batch_in: schemas.WaxBatchCreate, db: Session = Depends(get_db)):
    existing = db.query(models.WaxBatch).filter(models.WaxBatch.code == batch_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="蜡料批次编码已存在")

    batch = models.WaxBatch(**batch_in.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.WaxBatch.model_validate(batch).model_dump()
    )


@router.put("/{batch_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def update_wax_batch(batch_id: int, batch_in: schemas.WaxBatchUpdate, db: Session = Depends(get_db)):
    batch = db.query(models.WaxBatch).filter(models.WaxBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="蜡料批次不存在")

    if batch_in.code and batch_in.code != batch.code:
        existing = db.query(models.WaxBatch).filter(models.WaxBatch.code == batch_in.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="蜡料批次编码已存在")

    for key, value in batch_in.model_dump(exclude_unset=True).items():
        setattr(batch, key, value)

    db.commit()
    db.refresh(batch)

    return schemas.ApiResponse(
        message="更新成功",
        data=schemas.WaxBatch.model_validate(batch).model_dump()
    )


@router.delete("/{batch_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def delete_wax_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.WaxBatch).filter(models.WaxBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="蜡料批次不存在")

    has_batches = db.query(models.Batch).filter(models.Batch.wax_batch_id == batch_id).first()
    if has_batches:
        raise HTTPException(status_code=400, detail="该蜡料批次有关联试制批次，无法删除")

    db.delete(batch)
    db.commit()

    return schemas.ApiResponse(message="删除成功")
