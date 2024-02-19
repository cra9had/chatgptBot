import asyncio
import logging
import sys
import os
import yookassa
import locale
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.append(BASE_DIR)
from dotenv import load_dotenv
from pybot.handlers import router
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from openai import AsyncOpenAI


load_dotenv(os.path.join(f"{BASE_DIR}", ".env"))
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_API_KEY"))
client = AsyncOpenAI(
    api_key=os.getenv("CHATGPT_API_KEY"),
    base_url="https://api.proxyapi.ru/openai/v1"
)

yookassa.Configuration.configure(account_id=os.getenv("YOOKASSA_ACCOUNT_ID"),
                                 secret_key=os.getenv("YOOKASSA_SECRET_KEY"))
redis_client = Redis.from_url("redis://localhost:6379/1")
dp = Dispatcher(storage=RedisStorage(redis=redis_client))


async def main():
    dp.include_router(router)
    await dp.start_polling(bot, openai=client)


if __name__ == "__main__":
    asyncio.run(main())
