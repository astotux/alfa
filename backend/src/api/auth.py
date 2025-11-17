from datetime import timedelta
from uuid import uuid4

from another_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from auth.password_utils import get_password_hash, verify_password
from common.config import settings
from database.database import get_db
from models.user import User
from schemas.auth import TokenResponse, UserRegister

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username, email=user_data.email, hashed_password=hashed_pwd, id=str(uuid4())
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    print(settings.authjwt_secret_key)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = Authorize.create_access_token(
        subject=user.username,
        expires_time=timedelta(minutes=settings.access_token_expire_minutes),
        algorithm="HS256",
    )

    refresh_token = Authorize.create_refresh_token(
        subject=user.username,
        expires_time=timedelta(days=settings.refresh_token_expire_days),
        algorithm="HS256",
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    Authorize: AuthJWT = Depends(),
):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    username = Authorize.get_jwt_subject()

    new_access_token = Authorize.create_access_token(
        subject=username,
        expires_time=timedelta(minutes=settings.access_token_expire_minutes),
    )
    
    new_refresh_token = Authorize.create_refresh_token(
        subject=username, expires_time=timedelta(days=7)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout():
    return {"message": "Logged out"}