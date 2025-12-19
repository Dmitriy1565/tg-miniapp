from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os

from backend.db import init_db, add_note, get_notes, clear_notes
from backend.config import BOT_TOKEN
from backend.tg_auth import verify_webapp_init_data, TelegramAuthError

app = FastAPI()

class AddPayload(BaseModel):
    text: str

@app.on_event("startup")
async def startup():
    await init_db()

def get_user_id_from_request(request: Request) -> int:
    init_data = request.headers.get("X-Tg-Init-Data", "")
    try:
        tg_user = verify_webapp_init_data(init_data, BOT_TOKEN)
        return tg_user.id
    except TelegramAuthError as e:
        if os.getenv("DEV_ALLOW_NO_TG_AUTH") == "1":
            return 0
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/add")
async def api_add(request: Request, payload: AddPayload):
    user_id = get_user_id_from_request(request)
    await add_note(user_id, payload.text)
    return {"ok": True}

@app.post("/list")
async def api_list(request: Request):
    user_id = get_user_id_from_request(request)
    notes = await get_notes(user_id)
    return {"ok": True, "notes": notes}

@app.post("/clear")
async def api_clear(request: Request):
    user_id = get_user_id_from_request(request)
    await clear_notes(user_id)
    return {"ok": True}
