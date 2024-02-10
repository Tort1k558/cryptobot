from aiogram import types, Dispatcher, F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.keyboards.worker_kb import *
from core.utils.translations import get_translate
from core.utils.sqlite_db import cursor, conn, User


class SettingBalanceStates(StatesGroup):
    setting_amount = State()


class AddingBalanceStates(StatesGroup):
    setting_amount = State()


class MailMammothStates(StatesGroup):
    setting_message = State()


class MinWithdrawMammothStates(StatesGroup):
    setting_amount = State()


class MinDepositMammothStates(StatesGroup):
    setting_amount = State()


class FindMammothStates(StatesGroup):
    setting_id = State()


async def callback_mammoth_pages(callback: CallbackQuery, callback_data: MammothsPageCallback):
    worker = User.get_user(callback.from_user.id)

    cursor.execute(f"SELECT id,username FROM users WHERE referrer = {callback.from_user.id}")
    mammoths = cursor.fetchall()

    caption = get_translate("all_mammoths", worker.language).format(count=len(mammoths))
    try:
        await callback.message.edit_text(caption,
                                         reply_markup=get_users_kb(mammoths, callback_data.current, worker.language))
    except:
        pass


async def callback_worker_mammoths(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    worker = User.get_user(callback.from_user.id)
    if callback_data.action == "find":
        await state.set_state(FindMammothStates.setting_id)
        caption = get_translate("enter_mammoth_id", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())


async def get_mammoth_info(mammoth: User, language: str) -> str:
    cursor.execute(f"SELECT amount,profit,asset,duration from transactions WHERE id = "
                   f"(SELECT MAX(id) FROM transactions WHERE user_id = {mammoth.id})")
    last_transaction_info = cursor.fetchone()
    last_transaction = "None"
    if last_transaction_info:
        transaction_amount = last_transaction_info[0]
        transaction_profit = last_transaction_info[1]
        transaction_asset = last_transaction_info[2]
        transaction_duration = last_transaction_info[3]
        last_transaction = get_translate("last_transaction", language).format(amount=transaction_amount,
                                                                              profit=transaction_profit,
                                                                              asset=transaction_asset,
                                                                              duration=transaction_duration)

    caption = get_translate("mammoth_info", language).format(id=mammoth.id, username=mammoth.username,
                                                             balance=mammoth.balance,
                                                             on_withdraw=mammoth.on_withdraw,
                                                             referrer=mammoth.referrer,
                                                             min_deposit=mammoth.min_deposit,
                                                             min_withdraw=mammoth.min_withdraw,
                                                             verification="✅" if mammoth.verification else "❌",
                                                             last_transcation=last_transaction,
                                                             marketplace_status="✅" if mammoth.marketplace_status else "❌",
                                                             marketplace_strategy=mammoth.marketplace_strategy,
                                                             withdraw_status="✅" if mammoth.withdraw_status else "❌")
    return caption


async def find_mammoth_by_id(msg: Message, state: FSMContext):
    worker = User.get_user(msg.from_user.id)
    try:
        mammoth_id = int(msg.text)
        mammoth = User.get_user(mammoth_id)
        caption = await get_mammoth_info(mammoth, worker.language)

        await msg.answer(caption, reply_markup=get_mammoth_kb(mammoth, worker.language))
        await state.clear()
    except ValueError:
        caption = get_translate("mammoth_not_found", worker.language)
        await msg.answer(caption, reply_markup=get_worker_back_kb())
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_worker_back_kb())


async def callback_mammoth_info(callback: CallbackQuery, callback_data: MammothActionCallback, state: FSMContext,
                                bot: Bot):
    worker = User.get_user(callback.from_user.id)
    mammoth = User.get_user(callback_data.id)
    if callback_data.action == "info":

        caption = await get_mammoth_info(mammoth, worker.language)
        try:
            await callback.message.edit_text(caption, reply_markup=get_mammoth_kb(mammoth, worker.language))
        except:
            pass

        await state.set_state(None)
    elif callback_data.action.startswith("marketplace_strategy"):
        cursor.execute(
            f"UPDATE users SET marketplace_strategy = \"{callback_data.action.split('_')[2]}\" WHERE id = {mammoth.id}")
        conn.commit()
        await callback_mammoth_info(callback, MammothActionCallback(id=mammoth.id, action="info"), state, bot)
    elif callback_data.action.startswith("verification"):
        cursor.execute(
            f"UPDATE users SET verification = {callback_data.action.split('_')[1]} WHERE id = {mammoth.id}")
        conn.commit()
        await callback_mammoth_info(callback, MammothActionCallback(id=mammoth.id, action="info"), state, bot)
    elif callback_data.action.startswith("marketplace_status"):
        cursor.execute(
            f"UPDATE users SET marketplace_status = {callback_data.action.split('_')[2]} WHERE id = {mammoth.id}")
        conn.commit()
        await callback_mammoth_info(callback, MammothActionCallback(id=mammoth.id, action="info"), state, bot)
    elif callback_data.action.startswith("withdraw_status"):
        cursor.execute(
            f"UPDATE users SET withdraw_status = {callback_data.action.split('_')[2]} WHERE id = {mammoth.id}")
        conn.commit()
        await callback_mammoth_info(callback, MammothActionCallback(id=mammoth.id, action="info"), state, bot)
    elif callback_data.action == "change_balance":
        await state.set_state(SettingBalanceStates.setting_amount)
        await state.update_data(mammoth_id=mammoth.id)
        caption = get_translate("enter_new_mammoth_balance", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    elif callback_data.action == "add_balance":
        await state.set_state(AddingBalanceStates.setting_amount)
        await state.update_data(mammoth_id=mammoth.id)
        caption = get_translate("enter_add_mammoth_balance", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    elif callback_data.action == "mail":
        await state.set_state(MailMammothStates.setting_message)
        await state.update_data(mammoth_id=mammoth.id)
        caption = get_translate("enter_add_mammoth_balance", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    elif callback_data.action == "set_min_withdraw":
        await state.set_state(MinWithdrawMammothStates.setting_amount)
        await state.update_data(mammoth_id=mammoth.id)
        caption = get_translate("enter_min_mammoth_withdraw", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    elif callback_data.action == "set_min_deposit":
        await state.set_state(MinDepositMammothStates.setting_amount)
        await state.update_data(mammoth_id=mammoth.id)
        caption = get_translate("enter_min_mammoth_deposit", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    elif callback_data.action == "delete":
        cursor.execute(f"UPDATE users set referrer = 0 WHERE id = {mammoth.id}")
        conn.commit()
        caption = get_translate("mammoth_deleted", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "block":
        cursor.execute(f"UPDATE users set blocked = 1 WHERE id = {mammoth.id}")
        conn.commit()
        caption = get_translate("mammoth_blocked", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())
    elif callback_data.action == "unblock":
        cursor.execute(f"UPDATE users set blocked = 0 WHERE id = {mammoth.id}")
        conn.commit()
        caption = get_translate("mammoth_unblocked", worker.language)
        await callback.message.edit_text(caption, reply_markup=get_worker_back_kb())


async def set_mammoth_balance(msg: Message, state: FSMContext):
    worker = User.get_user(msg.from_user.id)
    mammoth_data = await state.get_data()
    mammoth = User.get_user(mammoth_data["mammoth_id"])

    try:
        amount = float(msg.text)

        cursor.execute(f"UPDATE users SET balance = {amount} WHERE id = {mammoth.id}")
        conn.commit()

        caption = get_translate("mammoth_balance_set", worker.language).format(amount=amount)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except ValueError:
        caption = get_translate("invalid_input", worker.language)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_mammoth_back_kb(mammoth.id))

    await state.clear()


async def add_mammoth_balance(msg: Message, state: FSMContext):
    worker = User.get_user(msg.from_user.id)
    mammoth_data = await state.get_data()
    mammoth = User.get_user(mammoth_data["mammoth_id"])

    try:
        amount = float(msg.text)

        cursor.execute(f"UPDATE users SET balance = {mammoth.balance + amount} WHERE id = {mammoth.id}")
        conn.commit()

        caption = get_translate("mammoth_balance_add", worker.language).format(amount=amount)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except ValueError:
        caption = get_translate("invalid_input", worker.language)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_mammoth_back_kb(mammoth.id))

    await state.clear()


async def mail_mammoth(msg: Message, state: FSMContext, bot: Bot):
    worker = User.get_user(msg.from_user.id)

    mammoth_data = await state.get_data()
    mammoth = User.get_user(mammoth_data["mammoth_id"])
    send_messages = 0

    try:
        await bot.send_message(chat_id=mammoth.id, text=msg.text)
        send_messages += 1
    except:
        pass

    caption = get_translate("mailing_completed", worker.language).format(count_messages=send_messages)
    await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))

    await state.clear()


async def set_mammoth_min_withdraw(msg: Message, state: FSMContext):
    worker = User.get_user(msg.from_user.id)

    mammoth_data = await state.get_data()
    mammoth = User.get_user(mammoth_data["mammoth_id"])
    try:
        amount = float(msg.text)

        cursor.execute(f"UPDATE users SET min_withdraw = {amount} WHERE id = {mammoth.id}")
        conn.commit()

        caption = get_translate("min_withdraw_is_set", worker.language).format(amount=amount)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except ValueError:
        caption = get_translate("invalid_input", worker.language)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_mammoth_back_kb(mammoth.id))

    await state.clear()


async def set_mammoth_min_deposit(msg: Message, state: FSMContext):
    worker = User.get_user(msg.from_user.id)

    mammoth_data = await state.get_data()
    mammoth = User.get_user(mammoth_data["mammoth_id"])
    try:
        amount = float(msg.text)

        cursor.execute(f"UPDATE users SET min_deposit = {amount} WHERE id = {mammoth.id}")
        conn.commit()

        caption = get_translate("min_deposit_is_set", worker.language).format(amount=amount)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except ValueError:
        caption = get_translate("invalid_input", worker.language)
        await msg.answer(caption, reply_markup=get_mammoth_back_kb(mammoth.id))
    except Exception as e:
        await msg.answer(str(e), reply_markup=get_mammoth_back_kb(mammoth.id))

    await state.clear()
