from fastapi import Header, HTTPException


async def verify_token(x_api_key: str = Header(None)):
    # Simple placeholder: replace with real auth logic
    if x_api_key is None or x_api_key == "":
        raise HTTPException(status_code=401, detail="Unauthorized")
