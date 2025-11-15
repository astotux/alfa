import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models.user import User
from models.sync_token import SyncToken
from schemas.sync_token import SyncTokenResponse

router = APIRouter()


@router.post("/user/sync-token", status_code=status.HTTP_200_OK, response_model=SyncTokenResponse)
def create_sync_token(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(SyncToken).filter(
        SyncToken.user_id == user.id
    ).delete()

    token = secrets.token_urlsafe(32)
    
    sync_token = SyncToken(
        token=token,
        user_id=user.id,
        created_at=datetime.now()
    )
    
    db.add(sync_token)
    db.commit()
    db.refresh(sync_token)
    
    return SyncTokenResponse(
        token=token
    )

