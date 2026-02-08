from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.db.database import engine
from app.db.models import Message, Reminder, User
from app.db.crud import get_or_create_user, create_reminder

def handle_user_message(update: dict):
    message = update.get("message", {})
    text = message.get("text")

    user_data = message.get("from", {})
    telegram_id = user_data.get("id")

    if not telegram_id or not text:
        print("Invalid message payload")
        return

    text = text.strip()

    with Session(engine) as session:
        # 1️⃣ Get or create user
        user = get_or_create_user(session, telegram_id)

        # 2️⃣ Save incoming message
        msg = Message( 
            telegram_id=telegram_id,
            user_id=user.id,
            text=text
        )
        session.add(msg)
        session.commit()

        # 3️⃣ Basic reminder creation rule
        if text.lower().startswith("remind"):
            task = text[len("remind"):].strip()

            if not task:
                print("[REMINDER] No task provided")
                return

            next_time = datetime.utcnow() + timedelta(minutes=10)

            reminder = create_reminder(
                session=session,
                user_id=user.id,
                task=task,
                next_reminder_at=next_time
            )

            print(
                f"[REMINDER CREATED] "
                f"User={user.id} "
                f"Task='{task}' "
                f"NextAt={next_time.isoformat()}"
            )
        else:
            print(f"[MESSAGE] User={user.id} Text='{text}'")


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