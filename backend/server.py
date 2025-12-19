import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from aiogram import Bot, Dispatcher, F
from aiogram.types import Update, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from backend.api import app as api_app
from backend.config import BOT_TOKEN


app = FastAPI()

# 1) API будет доступен как /api/add /api/list /api/clear
app.mount("/api", api_app)

# 2) Mini App статика
WEB_DIR = Path(__file__).resolve().parent.parent / "webapp"
app.mount("/webapp", StaticFiles(directory=str(WEB_DIR), html=True), name="webapp")

dp = Dispatcher()
bot: Bot | None = None


PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")


@dp.message(F.text == "/start")
async def start(msg):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🚀 Открыть приложение",
        web_app=WebAppInfo(url=f"{PUBLIC_BASE_URL}/webapp/index.html"),
    )
    kb.adjust(1)
    await msg.answer("Привет! Открывай Mini App 👇", reply_markup=kb.as_markup())

@app.on_event("startup")
async def on_startup():
    global bot

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is empty")

    if not PUBLIC_BASE_URL:
        raise RuntimeError("PUBLIC_BASE_URL is empty")

    bot = Bot(token)
    await bot.set_webhook(f"{PUBLIC_BASE_URL}/webhook")


@app.on_event("shutdown")
async def on_shutdown():
    if bot is not None:
        await bot.delete_webhook(drop_pending_updates=True)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    if bot is None:
        return {"ok": False, "error": "bot not initialized"}

    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

app.get("/")(lambda: {"ok": True})


