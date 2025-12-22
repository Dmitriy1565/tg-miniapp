from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
import aiosqlite
import sqlite3
from backend.db import init_db, add_note, get_notes, clear_notes, DB_PATH, create_order, get_last_order, set_order_status, issue_access_for_order
from backend.tg_auth import verify_webapp_init_data, TelegramAuthError

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

IS_LOCAL = os.getenv("RENDER", "") == ""

if not BOT_TOKEN and not IS_LOCAL:
    raise RuntimeError("BOT_TOKEN env is empty (Render env var missing?)")


app = FastAPI()

class AddPayload(BaseModel):
    text: str

class MarkPaidPayload(BaseModel):
    order_id: int

class MarkPaidPayload(BaseModel):
    order_id: int

class CreateOrderPayload(BaseModel):
    plan_id: int


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
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT id, name, days, price FROM plans ORDER BY days")
            rows = await cur.fetchall()
    except sqlite3.OperationalError as e:
        # Если таблицы еще нет — создаем ее через init_db() и пробуем снова
        if "no such table: plans" in str(e):
            await init_db()
            async with aiosqlite.connect(DB_PATH) as db:
                cur = await db.execute("SELECT id, name, days, price FROM plans ORDER BY days")
                rows = await cur.fetchall()
        else:
            raise

    return {
        "plans": [
            {"id": r[0], "name": r[1], "days": r[2], "price": r[3]}
            for r in rows
        ]
    }
@app.post("/order/create")
async def api_order_create(request: Request, payload: CreateOrderPayload):
    user_id = get_user_id_from_request(request)
    order_id = await create_order(user_id, payload.plan_id)
    return {"ok": True, "order_id": order_id}

@app.post("/order/last")
async def api_order_last(request: Request):
    user_id = get_user_id_from_request(request)
    order = await get_last_order(user_id)
    return {"ok": True, "order": order}

@app.post("/order/mark_paid")
async def api_order_mark_paid(request: Request, payload: MarkPaidPayload):
    user_id = get_user_id_from_request(request)

    # защита: убедимся, что заказ принадлежит этому пользователю
    order = await get_last_order(user_id)
    if not order or order["id"] != payload.order_id:
        raise HTTPException(status_code=403, detail="Order does not belong to user")

    await set_order_status(payload.order_id, "paid")
    return {"ok": True}

@app.post("/order/mark_paid")
async def api_order_mark_paid(request: Request, payload: MarkPaidPayload):
    user_id = get_user_id_from_request(request)

    # проверка, что заказ принадлежит пользователю (берём последний заказ)
    last = await get_last_order(user_id)
    if not last or last["id"] != payload.order_id:
        raise HTTPException(status_code=403, detail="Order does not belong to user")

    await set_order_status(payload.order_id, "paid")
    return {"ok": True}

@app.post("/order/access")
async def api_order_access(request: Request):
    user_id = get_user_id_from_request(request)

    order = await get_last_order(user_id)
    if not order:
        raise HTTPException(status_code=404, detail="No orders")

    if order["status"] != "paid":
        raise HTTPException(status_code=400, detail="Order not paid")

    # если access_code уже есть — просто вернем его
    # иначе выдадим новый
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT access_code FROM orders WHERE id=?", (order["id"],))
        row = await cur.fetchone()
        access_code = row[0] if row else None

    if not access_code:
        access_code = await issue_access_for_order(order["id"])

    return {"ok": True, "access_code": access_code}
