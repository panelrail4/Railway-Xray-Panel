from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    traffic_limit: int = 0
    expire_at: datetime | None = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    uuid: str
    traffic_limit: int
    traffic_used: int
    expire_at: datetime | None
    enabled: bool
