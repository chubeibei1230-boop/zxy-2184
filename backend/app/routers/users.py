from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return schemas.ApiResponse(
        data={"items": [schemas.User.model_validate(u).model_dump() for u in users]}
    )


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = models.User(
        username=user_in.username,
        name=user_in.name,
        role=user_in.role,
        password_hash=auth.get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.User.model_validate(user).model_dump()
    )


@router.put("/{user_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def update_user(user_id: int, user_in: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_in.name:
        user.name = user_in.name
    if user_in.role:
        user.role = user_in.role
    if user_in.password:
        user.password_hash = auth.get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)

    return schemas.ApiResponse(
        message="更新成功",
        data=schemas.User.model_validate(user).model_dump()
    )


@router.delete("/{user_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.username == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")

    db.delete(user)
    db.commit()

    return schemas.ApiResponse(message="删除成功")
