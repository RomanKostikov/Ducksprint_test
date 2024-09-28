import logging
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

from handlers import register_handlers

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получаем токен из переменных окружения
API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков
register_handlers(dp)


async def main():
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
