from fastapi import APIRouter, Header, HTTPException
from app.core.config import SCHEDULER_SECRET

router = APIRouter()

@router.post("/internal/run-reminders")
def run_reminders(authorization: str = Header(None)):
    if authorization != f"Bearer {SCHEDULER_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    print("Running reminder check...")
    return {"status": "ok"}
