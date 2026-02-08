# Reminder Buddy

Minimal starter scaffold for a Reminder service using FastAPI and Telegram.

Quick start

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Set `TELEGRAM_BOT_TOKEN` in a `.env` file or environment.

3. Run the app:

```bash
uvicorn app.main:app --reload --port 8000
```

4. Run the scheduler in another terminal to deliver reminders:

```bash
python -m app.scheduler.runner
```
