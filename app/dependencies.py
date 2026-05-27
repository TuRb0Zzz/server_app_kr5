from fastapi import HTTPException, Request, Depends
from app.storage import get_storage, TaskStorage

async def get_current_user(request: Request) -> int:
    user_id_header = request.headers.get("X-User-Id")
    if user_id_header is None:
        raise HTTPException(status_code=401, detail="X-User-Id header missing")
    try:
        user_id = int(user_id_header)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    return user_id