from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/styles", tags=["款式管理"])


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_styles(db: Session = Depends(get_db)):
    styles = db.query(models.Style).order_by(models.Style.code).all()
    return schemas.ApiResponse(
        data={"items": [schemas.Style.model_validate(s).model_dump() for s in styles]}
    )


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def create_style(style_in: schemas.StyleCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Style).filter(models.Style.code == style_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="款式编码已存在")

    style = models.Style(**style_in.model_dump())
    db.add(style)
    db.commit()
    db.refresh(style)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.Style.model_validate(style).model_dump()
    )


@router.put("/{style_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def update_style(style_id: int, style_in: schemas.StyleUpdate, db: Session = Depends(get_db)):
    style = db.query(models.Style).filter(models.Style.id == style_id).first()
    if not style:
        raise HTTPException(status_code=404, detail="款式不存在")

    if style_in.code and style_in.code != style.code:
        existing = db.query(models.Style).filter(models.Style.code == style_in.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="款式编码已存在")

    for key, value in style_in.model_dump(exclude_unset=True).items():
        setattr(style, key, value)

    db.commit()
    db.refresh(style)

    return schemas.ApiResponse(
        message="更新成功",
        data=schemas.Style.model_validate(style).model_dump()
    )


@router.delete("/{style_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def delete_style(style_id: int, db: Session = Depends(get_db)):
    style = db.query(models.Style).filter(models.Style.id == style_id).first()
    if not style:
        raise HTTPException(status_code=404, detail="款式不存在")

    has_batches = db.query(models.Batch).filter(models.Batch.style_id == style_id).first()
    if has_batches:
        raise HTTPException(status_code=400, detail="该款式有关联批次，无法删除")

    db.delete(style)
    db.commit()

    return schemas.ApiResponse(message="删除成功")
