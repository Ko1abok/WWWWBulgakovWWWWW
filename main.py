
import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import auth, common, knb, kub, book

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден! Убедитесь, что BOT_TOKEN указан в .env")

async def main() -> None:
    bot = Bot(token=TOKEN)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(auth.router)
    dp.include_router(knb.router)
    dp.include_router(kub.router)
    dp.include_router(book.router)
    dp.include_router(common.router)

    await bot.delete_webhook(drop_pending_updates=True)

    print("Бот запущен! Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")