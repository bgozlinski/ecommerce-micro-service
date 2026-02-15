from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.notification import (
    get_user_channels,
    create_channel,
    update_channel,
    delete_channel
)
from app.schemas.notification import (
    NotificationChannelCreate,
    NotificationChannelResponse,
    NotificationChannelUpdate
)
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.get("/notifications/channels", response_model=list[NotificationChannelResponse])
async def get_channels(user_id: int, db: Session = Depends(get_db)):
    """Get all notification channels for user."""
    channels = get_user_channels(db, user_id)
    return channels

@router.post("/notifications/channels", response_model=NotificationChannelResponse, status_code=status.HTTP_201_CREATED)
async def add_channel(channel: NotificationChannelCreate, db: Session = Depends(get_db)):
    """Add new notification channel."""
    return create_channel(db, channel)

@router.patch("/notifications/channels/{channel_id}", response_model=NotificationChannelResponse)
async def update_channel_settings(channel_id: int, update: NotificationChannelUpdate, db: Session = Depends(get_db)):
    """Update notification channel settings."""
    updated = update_channel(db, channel_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Channel not found")
    return updated

@router.delete("/notifications/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_channel(channel_id: int, db: Session = Depends(get_db)):
    """Delete notification channel."""
    deleted = delete_channel(db, channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Channel not found")