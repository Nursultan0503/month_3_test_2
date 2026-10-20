import sqlite3
from db.database import get_connection
from db.queries import (
    ADD_TASK,
    GET_USER_TASKS_JOIN,
    GET_TASK_BY_ID,
    MARK_TASK_DONE,
    DELETE_TASK,
    GET_USER_STATS_GROUP_BY,
)


def create_task(user_id: int, title: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(ADD_TASK, (user_id, title))
        conn.commit()
        return cursor.lastrowid


def get_tasks_with_user_info(user_id: int) -> list[tuple]:
    """Получает список задач с использованием INNER JOIN"""
    with get_connection() as conn:
        cursor = conn.execute(GET_USER_TASKS_JOIN, (user_id,))
        return cursor.fetchall()


def get_task_by_id_and_user(task_id: int, user_id: int):
    with get_connection() as conn:
        cursor = conn.execute(GET_TASK_BY_ID, (task_id, user_id))
        return cursor.fetchone()


def mark_task_as_done(task_id: int, user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(MARK_TASK_DONE, (task_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


def remove_task(task_id: int, user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(DELETE_TASK, (task_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


def get_task_statistics(user_id: int) -> dict:
    """Возвращает агрегированную статистику через GROUP BY"""
    with get_connection() as conn:
        cursor = conn.execute(GET_USER_STATS_GROUP_BY, (user_id,))
        rows = cursor.fetchall()

    stats = {"total": 0, "done": 0, "pending": 0}
    for is_done, count in rows:
        stats["total"] += count
        if is_done == 1:
            stats["done"] = count
        else:
            stats["pending"] = count
    return stats