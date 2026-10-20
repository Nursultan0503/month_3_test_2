from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.users import register_user
from db.tasks import (
    create_task,
    get_tasks_with_user_info,
    mark_task_as_done,
    remove_task,
    get_task_statistics,
)
from src.keyboards import get_tasks_inline_keyboard

router = Router()


# --- FSM Состояния ---
class AddTaskState(StatesGroup):
    title = State()


class DoneTaskState(StatesGroup):
    task_number = State()


class DeleteTaskState(StatesGroup):
    task_number = State()


# --- 1. /start ---
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    register_user(telegram_id=user_id, full_name=full_name)

    await message.answer(
        f"👋 Привет, <b>{full_name}</b>!\n\n"
        f"Я твой личный трекер задач.\n\n"
        f"<b>Доступные команды:</b>\n"
        f"/add — Добавить новую задачу\n"
        f"/tasks — Список всех задач\n"
        f"/done — Отметить задачу выполненной\n"
        f"/delete — Удалить задачу\n"
        f"/stats — Посмотреть статистику",
        parse_mode="HTML"
    )


# --- 2. /add (FSM) ---
@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await state.set_state(AddTaskState.title)
    await message.answer("📝 Введите название задачи:")


@router.message(AddTaskState.title)
async def process_task_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("Название задачи не может быть пустым. Попробуйте еще раз:")
        return

    task_id = create_task(user_id=message.from_user.id, title=title)
    await state.clear()
    await message.answer(f"✅ Задача <b>«{title}»</b> успешно добавлена!", parse_mode="HTML")


# --- 3. /tasks (INNER JOIN + Инлайн-кнопки) ---
@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    tasks = get_tasks_with_user_info(message.from_user.id)

    if not tasks:
        await message.answer("📭 У вас пока нет созданных задач. Используйте /add, чтобы добавить.")
        return

    user_name = tasks[0][3]  # Вытаскиваем full_name из INNER JOIN
    text = f"📋 <b>Список задач пользователя {user_name}:</b>\n\n"

    for idx, (task_id, title, is_done, _) in enumerate(tasks, start=1):
        status_icon = "✅" if is_done else "⬜"
        text += f"{idx}. {status_icon} <b>{title}</b>\n"

    kb = get_tasks_inline_keyboard(tasks)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# --- Inline callback для /tasks ---
@router.callback_query(F.data.startswith("done_task:"))
async def cb_done_task(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    success = mark_task_as_done(task_id=task_id, user_id=user_id)
    if success:
        await callback.answer("Задача отмечена выполненной! ✅", show_alert=True)
        # Обновляем список задач
        tasks = get_tasks_with_user_info(user_id)
        if tasks:
            text = f"📋 <b>Список задач пользователя {tasks[0][3]}:</b>\n\n"
            for idx, (t_id, title, is_done, _) in enumerate(tasks, start=1):
                status_icon = "✅" if is_done else "⬜"
                text += f"{idx}. {status_icon} <b>{title}</b>\n"
            kb = get_tasks_inline_keyboard(tasks)
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.answer("Ошибка: Задача не найдена или принадлежит другому пользователю.", show_alert=True)


# --- 4. /done (FSM по порядковому номеру) ---
@router.message(Command("done"))
async def cmd_done(message: Message, state: FSMContext):
    tasks = get_tasks_with_user_info(message.from_user.id)
    if not tasks:
        await message.answer("У вас нет задач для отметки.")
        return

    await state.set_state(DoneTaskState.task_number)
    await message.answer("Введите порядковый номер задачи, которую хотите отметить выполненной:")


@router.message(DoneTaskState.task_number)
async def process_done_number(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный числовой номер задачи:")
        return

    task_number = int(message.text)
    user_id = message.from_user.id
    tasks = get_tasks_with_user_info(user_id)

    if task_number < 1 or task_number > len(tasks):
        await message.answer("❌ Задача с таким порядковым номером не найдена или принадлежит другому пользователю!")
        await state.clear()
        return

    selected_task = tasks[task_number - 1]
    task_id = selected_task[0]

    success = mark_task_as_done(task_id=task_id, user_id=user_id)
    await state.clear()

    if success:
        await message.answer(f"✅ Задача №{task_number} <b>«{selected_task[1]}»</b> отмечена как выполненная!", parse_mode="HTML")
    else:
        await message.answer("❌ Ошибка при отметке задачи.")


# --- Доп. требование: /delete (по порядковому номеру) ---
@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext):
    tasks = get_tasks_with_user_info(message.from_user.id)
    if not tasks:
        await message.answer("У вас нет задач для удаления.")
        return

    await state.set_state(DeleteTaskState.task_number)
    await message.answer("Введите порядковый номер задачи для удаления:")


@router.message(DeleteTaskState.task_number)
async def process_delete_number(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный числовой номер задачи:")
        return

    task_number = int(message.text)
    user_id = message.from_user.id
    tasks = get_tasks_with_user_info(user_id)

    if task_number < 1 or task_number > len(tasks):
        await message.answer("❌ Задача с таким порядковым номером не найдена или принадлежит другому пользователю!")
        await state.clear()
        return

    selected_task = tasks[task_number - 1]
    task_id = selected_task[0]

    success = remove_task(task_id=task_id, user_id=user_id)
    await state.clear()

    if success:
        await message.answer(f"🗑 Задача №{task_number} <b>«{selected_task[1]}»</b> успешно удалена!", parse_mode="HTML")
    else:
        await message.answer("❌ Ошибка при удалении задачи.")


# --- 5. /stats (GROUP BY) ---
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    stats = get_task_statistics(message.from_user.id)

    await message.answer(
        f"📊 <b>Ваша статистика задач:</b>\n\n"
        f"📌 Всего задач: <b>{stats['total']}</b>\n"
        f"✅ Выполнено: <b>{stats['done']}</b>\n"
        f"⬜ Не выполнено: <b>{stats['pending']}</b>",
        parse_mode="HTML"
    )