from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.db.database import engine
from app.db.models import Message, Reminder, User
from app.db.crud import get_or_create_user, create_reminder
from app.telegram.client import send_telegram_message

async def handle_user_message(update: dict):
    message = update.get("message", {})
    text = message.get("text", "").strip()

    user_data = message.get("from", {})
    telegram_id = user_data.get("id")

    if not telegram_id or not text:
        return

    with Session(engine) as session:
        # 1️⃣ Ensure user exists
        user = get_or_create_user(session, telegram_id)

        # 2️⃣ Save incoming message
        session.add(
            Message(
                user_id=user.id,
                telegram_id=telegram_id,
                text=text
            )
        )
        session.commit()

        # 3️⃣ Immediate interaction logic
        if "test reminder" in text.lower():
            next_time = datetime.utcnow() + timedelta(minutes=1)

            reminder = create_reminder(
                session=session,
                user_id=user.id,
                task="Test Scheduler Flow",
                next_reminder_at=next_time
            )

            await send_telegram_message(
                chat_id=telegram_id,
                text="👍 Got it! I’ll remind you shortly."
            )

            print(f"[IMMEDIATE REPLY] Reminder {reminder.id} created")

        else:
            await send_telegram_message(
                chat_id=telegram_id,
                text="👋 I heard you.\nTry sending: test reminder"
            )

            print(f"[IMMEDIATE REPLY] Default reply sent")

def debug_overview():
    data = []

    with Session(engine) as session:
        users = session.exec(select(User)).all()

        for user in users:
            messages = session.exec(
                select(Message).where(Message.user_id == user.id)
            ).all()

            reminders = session.exec(
                select(Reminder).where(Reminder.user_id == user.id)
            ).all()

            data.append({
                "user_id": user.id,
                "telegram_id": user.telegram_id,
                "messages": [
                    {
                        "id": m.id,
                        "text": m.text,
                        "created_at": m.created_at
                    }
                    for m in messages
                ],
                "reminders": [
                    {
                        "id": r.id,
                        "task": r.task,
                        "status": r.status,
                        "next_reminder_at": r.next_reminder_at,
                        "follow_up_count": r.follow_up_count
                    }
                    for r in reminders
                ]
            })

    return data