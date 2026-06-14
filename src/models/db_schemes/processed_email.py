from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, EmailStr, Field


class ProcessedEmail(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    message_id: str = Field(..., min_length=1)
    interview_id: Optional[str] = None
    from_email: Optional[EmailStr] = None
    subject: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("message_id", 1)],
                "name": "message_id_index_1",
                "unique": True,
            }
        ]
