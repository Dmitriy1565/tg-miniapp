import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, PUBLIC_WEBAPP_URL

dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🚀 Открыть приложение",
        web_app=WebAppInfo(url=f"{PUBLIC_WEBAPP_URL}/webapp/index.html")
    )
    kb.button(text="ℹ️ Помощь", callback_data="help")
    kb.adjust(1)

    await msg.answer(
        "Привет! Это бот с Mini App + базой данных.\n"
        "Нажми кнопку ниже, чтобы открыть приложение 👇",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "help")
async def help_cb(cb):
    await cb.message.answer("Команды: /start\nВ Mini App можно добавлять и смотреть заметки.")
    await cb.answer()

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN пустой. Заполни backend/.env")

    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot, handle_signals=True)


if __name__ == "__main__":
    asyncio.run(main())
