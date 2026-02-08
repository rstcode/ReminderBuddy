from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.db.models import User, Reminder


def get_or_create_user(session: Session, telegram_id: int) -> User:
    statement = select(User).where(User.telegram_id == telegram_id)
    user = session.exec(statement).first()

    if user:
        return user

    user = User(telegram_id=telegram_id)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

def create_reminder(session: Session, user_id: int, task: str, next_reminder_at: datetime) -> Reminder:
    reminder = Reminder(
        user_id=user_id,
        task=task,
        next_reminder_at=next_reminder_at,
        status="pending",
        follow_up_count=0
    )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return reminder

def get_active_reminder_for_user(session: Session, user_id: int) -> Optional[Reminder]:
    statement = (
                    select(Reminder) .where(
                    Reminder.user_id == user_id,
                    Reminder.status == "pending"
                    ).order_by(Reminder.next_reminder_at.desc())
                )

    return session.exec(statement).first()

def reschedule_reminder(session: Session, reminder: Reminder, new_time: datetime) -> Reminder:
    reminder.next_reminder_at = new_time
    reminder.follow_up_count += 1
    reminder.updated_at = datetime.utcnow()

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return reminder

def mark_reminder_done(session: Session, reminder: Reminder) -> Reminder:
    reminder.status = "done"
    reminder.updated_at = datetime.utcnow()

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return reminder

def get_due_reminders(session: Session, now: datetime) -> list[Reminder]:
    
    statement = select(Reminder).where(Reminder.status == "pending", Reminder.next_reminder_at <= now)
    return session.exec(statement).all()

def get_pending_reminders_for_user(session: Session, user_id: int) -> list[Reminder]:
    statement = (
        select(Reminder)
        .where(
            Reminder.user_id == user_id,
            Reminder.status == "pending"
        )
        .order_by(Reminder.next_reminder_at)
    )

    return session.exec(statement).all()
