import sqlite3
from config import DB_NAME
from db.queries import CREATE_USERS_TABLE, CREATE_TASKS_TABLE


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Создание таблиц пользователей и задач"""
    with get_connection() as conn:
        conn.execute(CREATE_USERS_TABLE)
        conn.execute(CREATE_TASKS_TABLE)
        conn.commit()