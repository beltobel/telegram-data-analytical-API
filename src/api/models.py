from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Date
from src.api.database import Base

class Message(Base):
    __tablename__ = "fct_messages"
    message_id = Column(Integer, primary_key=True)
    channel_name = Column(String)
    message_text = Column(Text)
    message_timestamp = Column(DateTime)
    message_length = Column(Integer)
    has_image = Column(Boolean)
    message_date_key = Column(Date)

class ImageDetection(Base):
    __tablename__ = "fct_image_detections"
    message_id = Column(Integer, primary_key=True)
    channel_name = Column(String, primary_key=True)
    image_path = Column(String)
    detected_object_class = Column(String)
    confidence_score = Column(Float)