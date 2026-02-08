from fastapi import APIRouter, BackgroundTasks
from app.services.reminder import handle_user_message, get_list_messages

router = APIRouter()

@router.post("/telegram/webhook")
async def telegram_webhook(update: dict, background_tasks: BackgroundTasks):
    # Respond FAST
    background_tasks.add_task(handle_user_message, update)
    return {"ok": True}


@router.get("/debug/messages")
def list_messages():
    return get_list_messages()