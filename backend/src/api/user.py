from fastapi import APIRouter, Depends
from starlette import status

from auth.dependencies import get_current_user

from models.user import User


router = APIRouter()


@router.get("/user/profile", status_code=status.HTTP_200_OK)
def get_profile(user: User = Depends(get_current_user)):
  return user