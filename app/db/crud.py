from sqlalchemy.orm import Session
from app.db import models


def create_user(db: Session, username: str):
    user = models.User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_reminder(db: Session, user_id: int, text: str, due_at):
    reminder = models.Reminder(user_id=user_id, text=text, due_at=due_at)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def get_due_reminders(db: Session):
    from datetime import datetime

    return (
        db.query(models.Reminder)
        .filter(models.Reminder.sent == False, models.Reminder.due_at <= datetime.utcnow())
        .all()
    )


def mark_sent(db: Session, reminder: models.Reminder):
    reminder.sent = True
    db.commit()
    db.refresh(reminder)
    return reminder
