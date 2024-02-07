from aiogram import types, Dispatcher, F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.keyboards.worker_kb import *
from core.utils.translations import get_translate
from core.utils.sqlite_db import cursor, conn


class PromoStates(StatesGroup):
    setting_code = State()
    setting_balance = State()
    setting_uses = State()


async def callback_worker_promo(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {callback.from_user.id}")
    language = cursor.fetchone()[0]
    if callback_data.action == "new":
        caption = get_translate("enter_new_promo", language)
        await state.set_state(PromoStates.setting_code)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "list":
        caption = get_translate("promo_list", language)
        cursor.execute(f"SELECT code FROM promocodes WHERE id_creator = {callback.from_user.id}")
        promos = cursor.fetchall()
        await callback.message.edit_text(caption, reply_markup=get_worker_promo_list_kb(promos))


async def set_promo_code(msg: Message, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    try:
        code = msg.text

        await state.update_data(code=code)
        await state.set_state(PromoStates.setting_balance)

        caption = get_translate("enter_balance", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())

    except ValueError:
        caption = get_translate("invalid_input", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())


async def set_promo_balance(msg: Message, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    try:
        balance = float(msg.text)

        await state.update_data(balance=balance)
        await state.set_state(PromoStates.setting_uses)

        caption = get_translate("enter_promo_uses", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())

    except ValueError:
        caption = get_translate("invalid_input", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())


async def set_promo_uses(msg: Message, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    try:
        promo_data = await state.get_data()
        uses = int(msg.text)
        code = promo_data["code"]
        balance = promo_data["balance"]

        cursor.execute(
            f"INSERT INTO promocodes(code,id_creator,balance,uses) VALUES (\"{code}\", {msg.from_user.id}, {balance}, {uses})")
        conn.commit()
        await state.clear()
        caption = get_translate("promo_created", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except ValueError:
        caption = get_translate("invalid_input", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())


async def callback_promo_info(callback: CallbackQuery, callback_data: MenuCallback):
    cursor.execute(f"SELECT language FROM users WHERE id = {callback.from_user.id}")
    language = cursor.fetchone()[0]
    cursor.execute(f"SELECT code,id_creator,balance,uses FROM promocodes WHERE code = \"{callback_data.action}\"")
    promo_info = cursor.fetchone()
    caption = get_translate("promo_info", language).format(code=promo_info[0],
                                                           id_creator=promo_info[1],
                                                           balance=promo_info[2],
                                                           uses=promo_info[3])
    await callback.message.edit_text(caption, reply_markup=get_promo_info_kb(promo_info[0]))


async def callback_promo_delete(callback: CallbackQuery, callback_data: MenuCallback):
    cursor.execute(f"SELECT language FROM users WHERE id = {callback.from_user.id}")
    language = cursor.fetchone()[0]
    code = callback_data.action
    cursor.execute(f"DELETE FROM promocodes WHERE code = \"{code}\"")
    conn.commit()
    caption = get_translate("promo_deleted", language)
    await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
