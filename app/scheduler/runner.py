from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timedelta
from sqlmodel import Session

from app.core.config import settings
from app.db.database import engine
from app.db.crud import get_due_reminders, reschedule_reminder

router = APIRouter()


@router.post("/internal/run-reminders")
def run_reminders(authorization: str = Header(None)):
    # 1️⃣ Auth check
    # if authorization != f"Bearer {settings.SCHEDULER_SECRET}":
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.utcnow()

    with Session(engine) as session:
        # 2️⃣ Fetch due reminders
        due_reminders = get_due_reminders(session, now)

        if not due_reminders:
            print("[SCHEDULER] No due reminders")
            return {"status": "ok", "due": 0}

        # 3️⃣ Process due reminders
        for reminder in due_reminders:
            print(
                f"[DUE REMINDER] "
                f"ReminderID={reminder.id} "
                f"UserID={reminder.user_id} "
                f"Task='{reminder.task}' "
                f"At={reminder.next_reminder_at}"
            )

            # 4️⃣ For now: reschedule again after 10 minutes
            # (acts like a placeholder for Telegram send)
            new_time = now.replace(microsecond=0)
            new_time = new_time + timedelta(minutes=2)

            reschedule_reminder(
                session=session,
                reminder=reminder,
                new_time=new_time
            )

        return { "status": "ok", "due": len(due_reminders), "reminders":due_reminders}
