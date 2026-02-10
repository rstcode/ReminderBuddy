from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.db.database import engine
from app.db.models import Message, Reminder, User
from app.db.crud import get_active_reminder_for_user, get_or_create_user, create_reminder, mark_reminder_done, reschedule_reminder
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

        # 3️ Command handling
        text_lower = text.lower()

        if "test reminder" in text:
            next_time = datetime.now() + timedelta(minutes=1)

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

        # ✅ DONE COMMAND
        if text_lower == "done":
            active_reminder = get_active_reminder_for_user(
                session=session,
                user_id=user.id
            )

            if not active_reminder:
                await send_telegram_message(
                    chat_id=telegram_id,
                    text="👍 You have no active reminders."
                )
                return

            mark_reminder_done(session, active_reminder)

            await send_telegram_message(
                chat_id=telegram_id,
                text=f"✅ Done! I’ve marked this as completed:\n{active_reminder.task}"
            )

            print(f"[DONE] Reminder {active_reminder.id} completed")
            return

        # ⏳ LATER COMMAND
        if text_lower == "later":
            active_reminder = get_active_reminder_for_user(session, user.id)

            if not active_reminder:
                await send_telegram_message(
                    chat_id=telegram_id,
                    text="👍 You have no active reminders to postpone."
                )
                return

            new_time = datetime.now() + timedelta(minutes=10)

            reschedule_reminder(
                session=session,
                reminder=active_reminder,
                new_time=new_time
            )

            await send_telegram_message(
                chat_id=telegram_id,
                text=(
                    f"⏳ No problem! I’ll remind you again in 10 minutes.\n\n"
                    f"📝 {active_reminder.task}"
                )
            )

            print(
                f"[LATER] Reminder {active_reminder.id} "
                f"rescheduled to {new_time}"
            )
            return

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