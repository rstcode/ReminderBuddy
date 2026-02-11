from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from sqlmodel import Session

from app.core.config import settings
from app.db.database import engine
from app.db.crud import get_due_reminders, reschedule_reminder
from app.db.models import User
from app.telegram.client import send_telegram_message

router = APIRouter()
security = HTTPBearer()


@router.post("/internal/run-reminders")
async def run_reminders(credentials: HTTPAuthorizationCredentials = Depends(security)):

    # 🔐 Secure endpoint (IMPORTANT)
    if credentials.credentials != settings.SCHEDULER_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 🕒 Always use UTC
    now = datetime.now().replace(microsecond=0)

    response_reminders = []

    with Session(engine) as session:

        due_reminders = get_due_reminders(session, now)

        if not due_reminders:
            print("[SCHEDULER] No due reminders")
            return {"status": "ok", "due": 0, "reminders": []}

        for reminder in due_reminders:

            user = session.get(User, reminder.user_id)
            if not user:
                continue

            print(
                f"[DUE REMINDER] "
                f"ReminderID={reminder.id} "
                f"UserID={reminder.user_id} "
                f"Task='{reminder.task}' "
                f"At={reminder.next_reminder_at}"
            )

            # 📊 Follow-up ladder logic
            follow_count = reminder.follow_up_count or 0

            if follow_count == 0:
                delay_minutes = 5
                message_text = f"⏰ Reminder:\n{reminder.task}"

            elif follow_count == 1:
                delay_minutes = 10
                message_text = f"👋 Just checking on this:\n{reminder.task}"

            elif follow_count == 2:
                delay_minutes = 30
                message_text = f"⏳ Still pending:\n{reminder.task}"

            else:
                delay_minutes = 60
                message_text = f"⚠️ Final reminder for now:\n{reminder.task}"

            # 📤 Send Telegram message
            await send_telegram_message(
                chat_id=user.telegram_id,
                text=message_text
            )

            # 🧾 Prepare clean API response
            response_reminders.append({
                "id": reminder.id,
                "user_id": reminder.user_id,
                "task": reminder.task,
                "status": reminder.status,
                "next_reminder_at": reminder.next_reminder_at,
                "follow_up_count": reminder.follow_up_count,
                "created_at": reminder.created_at,
                "updated_at": reminder.updated_at,
            })

            # ⏳ Reschedule
            new_time = now + timedelta(minutes=delay_minutes)

            reschedule_reminder(
                session=session,
                reminder=reminder,
                new_time=new_time
            )

        return {
            "status": "ok",
            "due": len(response_reminders),
            "reminders": response_reminders
        }
