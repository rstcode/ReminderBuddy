async def extract_intent(text: str) -> str:
    """Placeholder for intent extraction (NLP/AI).

    Replace with real model call (OpenAI, local model, etc.).
    """
    # Very naive stub
    text = text.lower().strip()
    if "remind" in text or "reminder" in text:
        return "create_reminder"
    return "unknown"
