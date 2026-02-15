"""Repository layer for notification database operations.

This module provides CRUD operations for notification channel management
and notification history tracking.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.notification import NotificationChannel, NotificationHistory, NotificationChannelType
from app.schemas.notification import NotificationChannelCreate, NotificationChannelUpdate


def get_user_channels(db: Session, user_id: int) -> List[NotificationChannel]:
    """Retrieve all notification channels for a user.
    
    Args:
        db: Database session.
        user_id: User identifier.
        
    Returns:
        List[NotificationChannel]: List of user's notification channels.
    """
    return db.query(NotificationChannel).filter(
        NotificationChannel.user_id == user_id
    ).all()


def get_channel_by_id(db: Session, channel_id: int) -> Optional[NotificationChannel]:
    """Retrieve a notification channel by ID.
    
    Args:
        db: Database session.
        channel_id: Channel identifier.
        
    Returns:
        Optional[NotificationChannel]: Channel record if found, None otherwise.
    """
    return db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id
    ).first()


def create_channel(db: Session, channel: NotificationChannelCreate) -> NotificationChannel:
    """Create a new notification channel.
    
    Args:
        db: Database session.
        channel: Channel creation data.
        
    Returns:
        NotificationChannel: Newly created channel record.
    """
    db_channel = NotificationChannel(
        user_id=channel.user_id,
        channel_type=channel.channel_type,
        address=channel.address,
        is_primary=channel.is_primary,
        is_active=channel.is_active
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def update_channel(
    db: Session, 
    channel_id: int, 
    update: NotificationChannelUpdate
) -> Optional[NotificationChannel]:
    """Update notification channel settings.
    
    Allows updating address, primary status, and active status. Only provided
    fields are updated (partial update).
    
    Args:
        db: Database session.
        channel_id: Channel identifier.
        update: Channel update data.
        
    Returns:
        Optional[NotificationChannel]: Updated channel record if found, None otherwise.
    """
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        return None
    
    if update.address is not None:
        channel.address = update.address
    if update.is_primary is not None:
        channel.is_primary = update.is_primary
    if update.is_active is not None:
        channel.is_active = update.is_active
    
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def delete_channel(db: Session, channel_id: int) -> bool:
    """Delete a notification channel.
    
    Args:
        db: Database session.
        channel_id: Channel identifier.
        
    Returns:
        bool: True if channel was deleted, False if not found.
    """
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        return False
    
    db.delete(channel)
    db.commit()
    return True


def get_user_email(db: Session, user_id: int) -> Optional[str]:
    """Retrieve user's primary email address from notification channels.
    
    This function looks for the primary email channel for a user. If no primary
    channel exists, it returns the first active email channel.
    
    Args:
        db: Database session.
        user_id: User identifier.
        
    Returns:
        Optional[str]: User's email address if found, None otherwise.
    """
    # Try to get primary email channel
    primary_channel = db.query(NotificationChannel).filter(
        NotificationChannel.user_id == user_id,
        NotificationChannel.channel_type == NotificationChannelType.EMAIL,
        NotificationChannel.is_primary,
        NotificationChannel.is_active
    ).first()
    
    if primary_channel:
        return primary_channel.address
    
    # Fallback to any active email channel
    any_email_channel = db.query(NotificationChannel).filter(
        NotificationChannel.user_id == user_id,
        NotificationChannel.channel_type == NotificationChannelType.EMAIL,
        NotificationChannel.is_active
    ).first()
    
    if any_email_channel:
        return any_email_channel.address
    
    return None


def save_notification_history(
    db: Session,
    user_id: int,
    channel_type: NotificationChannelType,
    event_type: str,
    recipient: str,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    notification_status: str = "sent",
    error_message: Optional[str] = None
) -> NotificationHistory:
    """Save notification delivery history.
    
    Records the details of a sent notification for audit and debugging purposes.
    
    Args:
        db: Database session.
        user_id: User identifier.
        channel_type: Type of notification channel (email, discord).
        event_type: Type of event that triggered notification.
        recipient: Recipient address (email or Discord webhook).
        subject: Email subject (optional).
        body: Notification body content (optional).
        status: Delivery status ("sent" or "failed").
        error_message: Error details if delivery failed (optional).
        
    Returns:
        NotificationHistory: Created history record.
    """
    history = NotificationHistory(
        user_id=user_id,
        channel_type=channel_type,
        event_type=event_type,
        recipient=recipient,
        subject=subject,
        body=body,
        status=notification_status,
        error_message=error_message
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_notification_history(
    db: Session,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[NotificationHistory]:
    """Retrieve notification history records.
    
    Args:
        db: Database session.
        user_id: Optional user identifier to filter by.
        skip: Number of records to skip (offset). Defaults to 0.
        limit: Maximum number of records to return. Defaults to 100.
        
    Returns:
        List[NotificationHistory]: List of notification history records.
    """
    query = db.query(NotificationHistory)
    
    if user_id is not None:
        query = query.filter(NotificationHistory.user_id == user_id)
    
    return query.order_by(NotificationHistory.sent_at.desc()).offset(skip).limit(limit).all()
