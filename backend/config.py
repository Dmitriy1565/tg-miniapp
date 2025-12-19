import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PUBLIC_WEBAPP_URL = os.getenv("PUBLIC_WEBAPP_URL", "")  # https://xxxx.ngrok-free.app
