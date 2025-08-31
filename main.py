import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import config
from database import db
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.matching import router as matching_router

logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация базы данных
    await db.create_pool()
    await db.create_tables()
    
    # Инициализация бота
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(matching_router)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

