from fastapi import FastAPI
import asyncio
from app.db.database import create_db_and_tables
from app.telegram.webhook import router as telegram_router
from app.scheduler.runner import router as scheduler_router

app = FastAPI(title="AI Reminder Buddy")

@app.on_event("startup")
async def on_startup():
    await asyncio.to_thread(create_db_and_tables)

app.include_router(telegram_router)
app.include_router(scheduler_router)
