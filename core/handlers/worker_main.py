from typing import Any, Callable, Dict, Awaitable

from aiogram import types, Dispatcher, F, Router, Bot, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, TelegramObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.keyboards.worker_kb import *
from core.utils.translations import get_translate
from core.utils.sqlite_db import cursor, conn

from core.handlers.worker_promo import *
from core.handlers.worker_mammoths import *


class WorkerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        cursor.execute(f"SELECT * FROM workers WHERE id = {user.id}")
        worker = cursor.fetchone()
        if worker:
            return await handler(event, data)


worker_router = Router()
worker_router.message.middleware(WorkerMiddleware())
worker_router.callback_query.middleware(WorkerMiddleware())


async def command_worker(msg: Message):
    worker = User.get_user(msg.from_user.id)
    caption = get_translate("hello_worker", worker.language)
    await msg.answer(caption, reply_markup=get_worker_kb())


class MailingStates(StatesGroup):
    setting_message = State()


class AssignStates(StatesGroup):
    setting_mammoth_id = State()


class MinWithdrawStates(StatesGroup):
    setting_amount = State()


class MinDepositStates(StatesGroup):
    setting_amount = State()


async def callback_worker_menu(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {callback.from_user.id}")
    language = cursor.fetchone()[0]

    if callback_data.action == "menu":
        caption = get_translate("hello_worker", language)
        await callback.message.edit_text(caption, reply_markup=get_worker_kb())
        await state.set_state(None)
    elif callback_data.action == "users_list":
        cursor.execute(f"SELECT id,username FROM users WHERE referrer = {callback.from_user.id}")
        mammoths = cursor.fetchall()
        caption = get_translate("all_mammoths", language).format(count=len(mammoths))
        await callback.message.edit_text(caption, reply_markup=get_users_kb(mammoths, 0))
    elif callback_data.action == "mailing":
        await state.set_state(MailingStates.setting_message)
        caption = get_translate("send_mailing_message", language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "assign_mammoth":
        await state.set_state(AssignStates.setting_mammoth_id)
        caption = get_translate("enter_id_mammoth", language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "min_deposit":
        await state.set_state(MinDepositStates.setting_amount)
        caption = get_translate("enter_min_deposit_mammoths", language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "min_withdraw":
        await state.set_state(MinWithdrawStates.setting_amount)
        caption = get_translate("enter_min_withdraw_mammoths", language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "promo":
        caption = get_translate("select_action", language)
        await callback.message.edit_text(caption, reply_markup=get_promo_kb())
    elif callback_data.action == "select_currency":
        cursor.execute(f"SELECT default_currency FROM workers WHERE id = {callback.from_user.id}")
        currency = cursor.fetchone()[0]
        caption = get_translate("select_currency_mammoths", language).format(currency=currency)
        await callback.message.edit_text(caption, reply_markup=get_currencies_kb())
    elif callback_data.action == "private_link":
        pass
    elif callback_data.action == "delete_all_mammoths":
        caption = get_translate("delete_all_mammoths", language)
        await callback.message.edit_text(caption, reply_markup=get_delete_users_kb())


async def send_mailing_message(msg: Message, state: FSMContext, bot: Bot):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    cursor.execute(f"SELECT id FROM users WHERE referrer = {msg.from_user.id}")
    mammoths = cursor.fetchall()
    send_messages = 0
    for mammoth in mammoths:
        try:
            await bot.send_message(chat_id=mammoth[0], text=msg.text)
            send_messages += 1
        except:
            pass
    caption = get_translate("mailing_completed", language).format(count_messages=send_messages)

    await state.clear()

    await msg.answer(caption, reply_markup=get_worker_back_kb())


async def assign_mammoth(msg: Message, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    try:
        mammoth_id = int(msg.text)
        cursor.execute(f"SELECT referrer FROM users WHERE id = {mammoth_id}")
        mammoth_info = cursor.fetchone()
        if mammoth_info is None:
            raise Exception(get_translate("mammoth_not_found", language))
        if mammoth_info[0] != 0:
            raise Exception(get_translate("mammoth_is_already_assign", language))
        cursor.execute(f"UPDATE users SET referrer = {msg.from_user.id} WHERE id = {mammoth_id}")
        conn.commit()
        caption = get_translate("mammoth_is_assigned", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except ValueError:
        caption = get_translate("mammoth_not_found", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())

    await state.clear()


async def set_min_deposit(msg: Message, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    try:
        amount = float(msg.text)

        cursor.execute(f"UPDATE users SET min_deposit = {amount} WHERE referrer = {msg.from_user.id}")
        conn.commit()

        cursor.execute(f"UPDATE workers SET min_deposit = {amount} WHERE id = {msg.from_user.id}")
        conn.commit()

        caption = get_translate("min_deposit_is_set", language).format(amount=amount)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except ValueError:
        caption = get_translate("invalid_input", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())

    await state.clear()


async def set_min_withdraw(msg: Message, state: FSMContext):
    cursor.execute(f"SELECT language FROM users WHERE id = {msg.from_user.id}")
    language = cursor.fetchone()[0]

    try:
        amount = float(msg.text)

        cursor.execute(f"UPDATE users SET min_withdraw = {amount} WHERE referrer = {msg.from_user.id}")
        conn.commit()

        cursor.execute(f"UPDATE workers SET min_withdraw = {amount} WHERE id = {msg.from_user.id}")
        conn.commit()

        caption = get_translate("min_withdraw_is_set", language).format(amount=amount)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except ValueError:
        caption = get_translate("invalid_input", language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())

    await state.clear()


async def callback_worker_currency(callback: CallbackQuery, callback_data: MenuCallback):
    cursor.execute(f"SELECT language FROM users WHERE id = {callback.from_user.id}")
    language = cursor.fetchone()[0]
    currency = callback_data.action

    cursor.execute(f"UPDATE workers set default_currency = \"{currency}\" WHERE id = {callback.from_user.id}")
    conn.commit()

    caption = get_translate("select_worker_currency", language).format(currency=currency)
    await callback.message.edit_text(caption, reply_markup=get_currencies_kb())


async def callback_mammoths_delete(callback: CallbackQuery):
    cursor.execute(f"SELECT language FROM users WHERE id = {callback.from_user.id}")
    language = cursor.fetchone()[0]

    cursor.execute(f"UPDATE users set referrer = 0 WHERE referrer = {callback.from_user.id}")
    conn.commit()

    caption = get_translate("mammoths_deleted", language)
    await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())


worker_router.message.register(command_worker, Command("worker"))
worker_router.callback_query.register(callback_worker_menu, MenuCallback.filter(F.menu_name == "worker"))
worker_router.message.register(send_mailing_message, MailingStates.setting_message)
worker_router.message.register(assign_mammoth, AssignStates.setting_mammoth_id)
worker_router.message.register(set_min_deposit, MinDepositStates.setting_amount)
worker_router.message.register(set_min_withdraw, MinWithdrawStates.setting_amount)
worker_router.callback_query.register(callback_worker_currency,
                                      MenuCallback.filter(F.menu_name == "worker_currency"))
worker_router.callback_query.register(callback_worker_mammoths,
                                      MenuCallback.filter(F.menu_name == "worker_mammoths"))
worker_router.message.register(find_mammoth_by_id, FindMammothStates.setting_id)

worker_router.callback_query.register(callback_worker_promo,
                                      MenuCallback.filter(F.menu_name == "worker_promo"))
worker_router.message.register(set_promo_code, PromoStates.setting_code)
worker_router.message.register(set_promo_balance, PromoStates.setting_balance)
worker_router.message.register(set_promo_uses, PromoStates.setting_uses)

worker_router.callback_query.register(callback_promo_info,
                                      MenuCallback.filter(F.menu_name == "promo_info"))
worker_router.callback_query.register(callback_promo_delete,
                                      MenuCallback.filter(F.menu_name == "promo_delete"))

worker_router.callback_query.register(callback_mammoths_delete,
                                      MenuCallback.filter(F.menu_name == "mammoths_delete"))

worker_router.callback_query.register(callback_mammoth_pages,
                                      MammothsPageCallback.filter())
worker_router.callback_query.register(callback_mammoth_info,
                                      MammothActionCallback.filter())

worker_router.message.register(set_mammoth_balance, SettingBalanceStates.setting_amount)
worker_router.message.register(add_mammoth_balance, AddingBalanceStates.setting_amount)
worker_router.message.register(mail_mammoth, MailMammothStates.setting_message)
worker_router.message.register(set_mammoth_min_withdraw, MinWithdrawMammothStates.setting_amount)
worker_router.message.register(set_mammoth_min_deposit, MinDepositMammothStates.setting_amount)
