import uuid
from datetime import datetime
from pydantic import BaseModel


class AchievementOut(BaseModel):
    id: uuid.UUID
    key: str
    name: str
    description: str
    icon: str
    earned_at: datetime

    class Config:
        from_attributes = True
