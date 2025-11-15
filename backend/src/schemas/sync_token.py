from pydantic import BaseModel


class SyncTokenResponse(BaseModel):
    token: str

