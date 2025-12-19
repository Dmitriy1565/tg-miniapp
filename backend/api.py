from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os

from backend.db import init_db, add_note, get_notes, clear_notes, DB_PATH
from backend.tg_auth import verify_webapp_init_data, TelegramAuthError

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

IS_LOCAL = os.getenv("RENDER", "") == ""

if not BOT_TOKEN and not IS_LOCAL:
    raise RuntimeError("BOT_TOKEN env is empty (Render env var missing?)")


app = FastAPI()

class AddPayload(BaseModel):
    text: str



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

@app.get("/plans")
@app.post("/plans")
async def api_plans():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, days, price FROM plans ORDER BY days")
        rows = await cur.fetchall()

    return {
        "plans": [
            {"id": r[0], "name": r[1], "days": r[2], "price": r[3]}
            for r in rows
        ]
    }

