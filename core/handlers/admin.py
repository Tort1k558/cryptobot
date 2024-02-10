from typing import Any, Callable, Dict, Awaitable

from aiogram import types, Dispatcher, F, Router, Bot, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, TelegramObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.keyboards.admin_kb import *
from core.utils.translations import get_translate
from core.utils.sqlite_db import cursor, conn

from core.handlers.worker_promo import *
from core.handlers.worker_mammoths import *


class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        cursor.execute(f"SELECT * FROM admins WHERE id = {user.id}")
        worker = cursor.fetchone()
        if worker:
            return await handler(event, data)


admin_router = Router()
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


async def command_admin(msg: Message):
    admin = User.get_user(msg.from_user.id)
    caption = "Приветствую админ!"
    await msg.answer(caption, reply_markup=get_admin_kb(admin.language))


class AddWorkerStates(StatesGroup):
    setting_id = State()


class DeleteWorkerStates(StatesGroup):
    setting_id = State()


async def callback_admin_menu(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    admin = User.get_user(callback.from_user.id)

    if callback_data.action == "menu":
        caption = "Приветствую админ!"
        await callback.message.edit_text(caption, reply_markup=get_admin_kb(admin.language))
        await state.set_state(None)

    elif callback_data.action == "add_worker":
        caption = "Введите id пользователя"
        await callback.message.edit_text(caption, reply_markup=get_admin_back_kb())
        await state.set_state(AddWorkerStates.setting_id)
    elif callback_data.action == "delete_worker":
        caption = "Введите id пользователя"
        await callback.message.edit_text(caption, reply_markup=get_admin_back_kb())
        await state.set_state(DeleteWorkerStates.setting_id)
    elif callback_data.action == "change_requisites":
        caption = "Выберете валюту"
        await callback.message.edit_text(caption, reply_markup=get_change_requisites_kb())


async def add_worker_id(msg: Message, state: FSMContext):
    admin = User.get_user(msg.from_user.id)

    try:
        worker_id = int(msg.text)

        cursor.execute(f"SELECT id FROM workers WHERE id = {worker_id}")
        worker_info = cursor.fetchone()
        if worker_info:
            raise Exception("Пользователь уже является воркером!")

        cursor.execute(f"""INSERT INTO workers(id, min_deposit, min_withdraw, default_language,default_currency)
         VALUES({worker_id}, 1.0, 1.0, "RUS", "USD")""")
        conn.commit()
        caption = "Воркер успешно добавлен!"
        await msg.answer(caption, reply_markup=get_admin_back_kb())

        await state.clear()
    except ValueError:
        caption = get_translate("invalid_input", admin.language)
        await msg.answer(caption, reply_markup=get_admin_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_admin_back_kb())


async def delete_worker_id(msg: Message, state: FSMContext):
    admin = User.get_user(msg.from_user.id)

    try:
        worker_id = int(msg.text)

        cursor.execute(f"SELECT id FROM workers WHERE id = {worker_id}")
        worker_info = cursor.fetchone()
        if worker_info is None:
            raise Exception("Воркера с данным id не существует!")

        cursor.execute(f"""DELETE FROM workers WHERE id = {worker_id}""")
        conn.commit()
        caption = "Воркер успешно удалён"
        await msg.answer(caption, reply_markup=get_admin_back_kb())

        await state.clear()
    except ValueError:
        caption = get_translate("invalid_input", admin.language)
        await msg.answer(caption, reply_markup=get_admin_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_admin_back_kb())


class ChangeRequisitesStates(StatesGroup):
    setting_requisites = State()


async def change_requisites(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    admin = User.get_user(callback.from_user.id)

    currency = callback_data.action.upper()
    requisites = "None"

    cursor.execute(f"SELECT requisites FROM currencies WHERE name = \"{currency}\" ")
    current_requisites = cursor.fetchone()
    if current_requisites:
        requisites = current_requisites[0]

    caption = f"""Валюта: {currency}
Текущие реквизиты: {requisites}

Введите реквизиты:"""
    await callback.message.edit_text(caption, reply_markup=get_admin_back_kb())

    await state.set_state(ChangeRequisitesStates.setting_requisites)
    await state.update_data(currency=currency)


async def set_requisites(msg: Message, state: FSMContext):
    admin = User.get_user(msg.from_user.id)

    requisites_data = await state.get_data()
    currency = requisites_data["currency"]

    cursor.execute(f"SELECT name FROM currencies WHERE name = \"{currency}\" ")
    current_requisites = cursor.fetchone()
    if current_requisites:
        cursor.execute(f"UPDATE currencies SET requisites = \"{msg.text}\" WHERE name = \"{currency}\" ")
    else:
        cursor.execute(f"INSERT INTO currencies(name, requisites) VALUES(\"{currency}\", \"{msg.text}\")")
    conn.commit()

    caption = "Реквизиты успешно сменены!"
    await msg.answer(caption, reply_markup=get_admin_back_kb())

    await state.clear()


admin_router.message.register(command_admin, Command("admin"))
admin_router.callback_query.register(callback_admin_menu, MenuCallback.filter(F.menu_name == "admin"))
admin_router.message.register(add_worker_id, AddWorkerStates.setting_id)
admin_router.message.register(delete_worker_id, DeleteWorkerStates.setting_id)
admin_router.callback_query.register(change_requisites, MenuCallback.filter(F.menu_name == "change_requisites"))
admin_router.message.register(set_requisites, ChangeRequisitesStates.setting_requisites)
