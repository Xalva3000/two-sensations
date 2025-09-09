import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import config
from database import db
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.topics import router as topics_router
from handlers.settings import router as settings_router
from handlers.photo import router as photo_router
from handlers.matching import router as matching_router
from handlers.profile import router as profile_router
from handlers.companions import router as companions_router
from handlers.contacts import router as contacts_router
from handlers.admin import router as admin_router


logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализация базы данных
    await db.create_pool()
    await db.create_tables()

    # Инициализация бота
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(admin_router)
    dp.include_router(contacts_router)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(companions_router)
    dp.include_router(topics_router)
    dp.include_router(settings_router)
    dp.include_router(photo_router)
    dp.include_router(matching_router)
    dp.include_router(profile_router)


    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
