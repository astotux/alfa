from fastapi import APIRouter
from .auth import router as auth_router
from .llm import router as llm_router
from .chat import router as chat_router
from .user import router as user_router
from .sync_token import router as sync_token_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(llm_router, prefix="", tags=["llm"])
api_router.include_router(chat_router, prefix="", tags=["chat"])
api_router.include_router(user_router, prefix="", tags=["user"])
api_router.include_router(sync_token_router, prefix="", tags=["sync"])

__all__ = ["api_router"]