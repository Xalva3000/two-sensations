from aiogram import Bot
from aiogram.types import BotCommand



# Функция для настройки кнопок нижнего меню бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="Запуск/Перезапуск/Меню"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/info", description="Информация"),
        BotCommand(command="/admin", description="Админ панель"),
    ]
    await bot.set_my_commands(main_menu_commands)