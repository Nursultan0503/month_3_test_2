from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_tasks_inline_keyboard(tasks: list[tuple]) -> InlineKeyboardMarkup:
    """Генерирует инлайн-кнопки для быстрой отметки задачи выполненной"""
    buttons = []
    for idx, (task_id, title, is_done, _) in enumerate(tasks, start=1):
        if not is_done:
            btn = InlineKeyboardButton(
                text=f"✅ Выполнить №{idx}",
                callback_data=f"done_task:{task_id}"
            )
            buttons.append([btn])

    return InlineKeyboardMarkup(inline_keyboard=buttons)