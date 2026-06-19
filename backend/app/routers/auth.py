from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from .. import models, schemas, auth
from ..config import settings

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=schemas.ApiResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not auth.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return schemas.ApiResponse(
        data=schemas.LoginResponse(
            access_token=access_token,
            user=schemas.User.model_validate(user)
        ).model_dump()
    )


@router.get("/me", response_model=schemas.ApiResponse)
def get_current_user(current_user: models.User = Depends(auth.get_current_active_user)):
    return schemas.ApiResponse(
        data=schemas.User.model_validate(current_user).model_dump()
    )
