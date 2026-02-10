from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timedelta
from sqlmodel import Session

from app.core.config import settings
from app.db.database import engine
from app.db.crud import get_due_reminders, reschedule_reminder

router = APIRouter()


@router.post("/internal/run-reminders")
def run_reminders(authorization: str = Header(None)):
    # 🔐 Enable later
    # if authorization != f"Bearer {settings.SCHEDULER_SECRET}":
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.now()
    response_reminders = []

    with Session(engine) as session:
        due_reminders = get_due_reminders(session, now)

        if not due_reminders:
            print("[SCHEDULER] No due reminders")
            return {"status": "ok", "due": 0, "reminders": []}

        for reminder in due_reminders:
            print(
                f"[DUE REMINDER] "
                f"ReminderID={reminder.id} "
                f"UserID={reminder.user_id} "
                f"Task='{reminder.task}' "
                f"At={reminder.next_reminder_at}"
            )

            # ✅ Convert ORM → dict BEFORE commit
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

            # ⏰ Reschedule
            new_time = now.replace(microsecond=0) + timedelta(minutes=2)

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
