from sqlmodel import Session, select
from app.db.database import engine
from app.db.models import Message

def handle_user_message(update: dict):
    message = update.get("message", {})
    text = message.get("text")
    user = message.get("from", {})

    telegram_id = user.get("id")

    with Session(engine) as session:
        msg = Message(
            telegram_id=telegram_id,
            text=text
        )
        session.add(msg)
        session.commit()

    print(f"[SAVED] {telegram_id}: {text}")


def get_list_messages():
    with Session(engine) as session:
        return session.exec(select(Message)).all()
