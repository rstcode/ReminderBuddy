from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(index=True, unique=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relationship
    reminders: List["Reminder"] = Relationship(back_populates="user")


class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    task: str

    next_reminder_at: datetime
    status: str = Field(default="pending")  
    # expected values: pending, done, cancelled

    follow_up_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relationship
    user: Optional[User] = Relationship(back_populates="reminders")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    telegram_id: int = Field(index=True)
    text: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
