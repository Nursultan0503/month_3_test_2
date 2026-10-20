import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db.database import init_db
from src.handlers import router


async def main():
    # 1. Инициализация БД (создание таблиц пользователей и задач)
    init_db()
    logging.info("База данных успешно инициализирована.")

    # 2. Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 3. Регистрация роутеров
    dp.include_router(router)

    # 4. Запуск поллинга
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())