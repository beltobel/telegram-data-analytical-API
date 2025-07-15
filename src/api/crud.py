from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from src.api.models import Message, ImageDetection
from typing import List

def get_top_products(db: Session, limit: int = 10) -> List[dict]:
    results = (
        db.query(
            ImageDetection.detected_object_class,
            func.count().label("mention_count")
        )
        .group_by(ImageDetection.detected_object_class)
        .order_by(func.count().desc())
        .limit(limit)
        .all()
    )
    return [{"detected_object_class": r.detected_object_class, "mention_count": r.mention_count} for r in results]

def get_channel_activity(db: Session, channel_name: str) -> List[dict]:
    results = (
        db.query(
            Message.message_date_key.label("message_date"),
            func.count().label("message_count")
        )
        .filter(Message.channel_name == channel_name)
        .group_by(Message.message_date_key)
        .order_by(Message.message_date_key)
        .all()
    )
    return [{"message_date": r.message_date, "message_count": r.message_count} for r in results]

def search_messages(db: Session, query: str) -> List[dict]:
    results = (
        db.query(Message)
        .filter(Message.message_text.ilike(f"%{query}%"))
        .all()
    )
    return [
        {
            "message_id": r.message_id,
            "channel_name": r.channel_name,
            "message_text": r.message_text,
            "message_timestamp": r.message_timestamp
        }
        for r in results
    ]