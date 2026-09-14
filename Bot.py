from idlelib.undo import Command
from os import getenv
import asyncio
from aiogram import *
from aiogram.types import Message
from dotenv import load_dotenv
from handlers.routes import router
import db

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

dp.include_router(router)

async def main():
    bot = Bot(token=TOKEN)

    db.create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
