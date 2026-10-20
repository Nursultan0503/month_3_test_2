import os
from decouple import config

# Получаем токен из .env или переменной окружения
BOT_TOKEN = config("BOT_TOKEN", default="YOUR_BOT_TOKEN_HERE")
DB_NAME = config("DB_NAME", default="tasks_tracker.db")