"""SQLAlchemy models for user-related database tables.

This module defines the User model representing system users (customers and
administrators) with authentication and authorization attributes.
"""

from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, func, DateTime

class User(Base):
    """User account record.
    
    Represents a user in the system with authentication credentials and role-based
    access control. Users can be regular customers or administrators.
    
    Attributes:
        id: Primary key, auto-incrementing user identifier.
        email: User's email address (unique, used for login).
        password_hash: Hashed password using bcrypt.
        role: User role. One of: "user", "admin". Defaults to "user".
        is_active: Account status flag. Inactive users cannot authenticate.
        created_at: Timestamp when the user account was created.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default="user")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
