from pydantic import BaseModel
from datetime import datetime, date
from typing import List

class TopProduct(BaseModel):
    detected_object_class: str
    mention_count: int

class ChannelActivity(BaseModel):
    message_date: date
    message_count: int

class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    message_timestamp: datetime