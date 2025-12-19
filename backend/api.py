from fastapi import FastAPI
from pydantic import BaseModel
from backend.db import init_db, add_note, get_notes, clear_notes

app = FastAPI()

class AddPayload(BaseModel):
    user_id: int
    text: str

class UserPayload(BaseModel):
    user_id: int

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/api/add")
async def api_add(payload: AddPayload):
    await add_note(payload.user_id, payload.text)
    return {"ok": True}

@app.post("/api/list")
async def api_list(payload: UserPayload):
    notes = await get_notes(payload.user_id)
    return {"ok": True, "notes": notes}

@app.post("/api/clear")
async def api_clear(payload: UserPayload):
    await clear_notes(payload.user_id)
    return {"ok": True}