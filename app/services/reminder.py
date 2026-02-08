def handle_user_message(update: dict):
    message = update.get("message", {})
    text = message.get("text")
    user = message.get("from", {})

    telegram_id = user.get("id")

    print(f"[MSG] {telegram_id}: {text}")

    # TODO:
    # 1. find or create user
    # 2. detect intent (AI later)
    # 3. update reminder
    # 4. send Telegram reply
