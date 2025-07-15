from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.api import crud, schemas
from src.api.database import get_db

app = FastAPI(title="Telegram Analytics API")

@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be positive")
    products = crud.get_top_products(db, limit=limit)
    return products

@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    activity = crud.get_channel_activity(db, channel_name=channel_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Channel not found or no activity")
    return activity

@app.get("/api/search/messages", response_model=List[schemas.MessageSearchResult])
def search_messages(query: str, db: Session = Depends(get_db)):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    messages = crud.search_messages(db, query=query)
    return messages