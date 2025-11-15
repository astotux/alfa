from another_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common.config import settings
from database import get_db
from models.user import User


class JWTConfig(BaseModel):
    authjwt_secret_key: str = settings.authjwt_secret_key
    authjwt_token_location: list = settings.authjwt_token_location
    authjwt_algorithm: str = settings.authjwt_algorithm


@AuthJWT.load_config
def get_jwt_config():
    return JWTConfig()


async def get_current_user(
    Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)
) -> User:
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    username = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
