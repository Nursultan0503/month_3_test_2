# --- Инициализация БД ---
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    is_done INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);
"""

# --- USERS queries ---
ADD_OR_IGNORE_USER = """
INSERT OR IGNORE INTO users (telegram_id, full_name)
VALUES (?, ?);
"""

GET_USER = """
SELECT telegram_id, full_name FROM users WHERE telegram_id = ?;
"""

# --- TASKS queries ---
ADD_TASK = """
INSERT INTO tasks (user_id, title)
VALUES (?, ?);
"""

# 3. /tasks: INNER JOIN пользователей и задач
GET_USER_TASKS_JOIN = """
SELECT t.id, t.title, t.is_done, u.full_name
FROM tasks t
INNER JOIN users u ON t.user_id = u.telegram_id
WHERE t.user_id = ?
ORDER BY t.id ASC;
"""

GET_TASK_BY_ID = """
SELECT id, user_id, title, is_done
FROM tasks
WHERE id = ? AND user_id = ?;
"""

MARK_TASK_DONE = """
UPDATE tasks
SET is_done = 1
WHERE id = ? AND user_id = ?;
"""

DELETE_TASK = """
DELETE FROM tasks
WHERE id = ? AND user_id = ?;
"""

# 5. /stats: Статистика с GROUP BY
GET_USER_STATS_GROUP_BY = """
SELECT is_done, COUNT(*) as count
FROM tasks
WHERE user_id = ?
GROUP BY is_done;
"""