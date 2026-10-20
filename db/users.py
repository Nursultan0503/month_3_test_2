import sqlite3
from db.database import get_connection
from db.queries import ADD_OR_IGNORE_USER, GET_USER


def register_user(telegram_id: int, full_name: str):
    with get_connection() as conn:
        conn.execute(ADD_OR_IGNORE_USER, (telegram_id, full_name))
        conn.commit()


def get_user_by_id(telegram_id: int):
    with get_connection() as conn:
        cursor = conn.execute(GET_USER, (telegram_id,))
        return cursor.fetchone()