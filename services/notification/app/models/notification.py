from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text, func
from app.core.database import Base
import enum


class NotificationChannelType(str, enum.Enum):
    EMAIL = "email"
    DISCORD = "discord"


class NotificationChannel(Base):
    __tablename__ = "notification_channels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel_type = Column(SQLEnum(NotificationChannelType), nullable=False)
    address = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel_type = Column(SQLEnum(NotificationChannelType), nullable=False)
    event_type = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text)
    status = Column(String, nullable=False)
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)