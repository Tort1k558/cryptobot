from aiogram import Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.utils.sqlite_db import cursor, conn, User
from core.keyboards.wallet_kb import *
from core.keyboards.main_menu_kb import *
from core.keyboards.worker_kb import get_control_mammoth_kb

from core.utils.converter import convert_currency


class DepositCard(StatesGroup):
    setting_amount = State()


class Withdraw(StatesGroup):
    setting_amount = State()


class Promocode(StatesGroup):
    setting_code = State()


async def callback_wallet_menu(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    user = User.get_user(callback.from_user.id)

    if callback_data.action == "deposit":
        caption = get_translate("deposit_caption", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_deposit_kb(user.language))
    elif callback_data.action == "withdraw":
        cursor.execute(f"SELECT withdraw_status FROM users WHERE id = {callback.from_user.id}")
        withdraw_status = cursor.fetchone()[0]
        if withdraw_status:
            caption = get_translate("withdraw_amount", user.language)
            await state.set_state(Withdraw.setting_amount)
            await callback.message.edit_caption(caption=caption, reply_markup=get_wallet_back_kb())
        else:
            await callback.message.edit_caption(caption=get_translate("withdraw_blocked", user.language),
                                                reply_markup=get_wallet_back_kb())
    elif callback_data.action == "promo":
        await state.set_state(Promocode.setting_code)
        caption = get_translate("enter_promo", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_promo_kb())


async def callback_pay_method_menu(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    user = User.get_user(callback.from_user.id)

    if callback_data.action == "card":
        caption = get_translate("deposit_amount", user.language)
        await state.set_state(DepositCard.setting_amount)

        await callback.message.edit_caption(caption=caption, reply_markup=get_deposit_card_kb())
    elif callback_data.action == "crypto":
        caption = get_translate("deposit_crypto_caption", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_deposit_crypto_kb())


async def set_deposit_card_amount(msg: Message, state: FSMContext, bot: Bot):
    user = User.get_user(msg.from_user.id)

    exchange_rate_usd = await convert_currency(user.currency, "USD")
    exchange_rate_user_currency = await convert_currency("USD", user.currency)

    requisites = "None"

    cursor.execute(f"SELECT requisites FROM currencies WHERE name = \"{user.currency}\"")
    requisites_info = cursor.fetchone()
    if requisites_info:
        requisites = requisites_info[0]

    try:
        amount = exchange_rate_usd * float(msg.text)

        if amount <= user.min_deposit:
            raise Exception(get_translate("error_min_amount", user.language).format
                            (min_amount=user.min_deposit * exchange_rate_user_currency, currency=user.currency))

        photo = FSInputFile("files/123.jpg")
        caption = get_translate("card_requisites", user.language).format(requisites=requisites, comment="КОММЕНТ")
        await msg.answer_photo(
            photo,
            caption=caption,
            reply_markup=get_check_deposit_kb(user.language)
        )
        await state.clear()

        if referrer != 0:
            caption = get_translate("mammoth_deposit_card", user.language).format(amount=amount, balance=user.balance,
                                                                                  username=user.username,
                                                                                  pay_method="card")
            await bot.send_message(referrer, caption,
                                   reply_markup=get_deposit_card_mammoth_kb(msg.from_user.id, amount))
    except ValueError:
        await msg.answer(get_translate("invalid_input", user.language))
    except Exception as e:
        await msg.answer(str(e))


async def callback_check_deposit(callback: CallbackQuery, callback_data: MenuCallback):
    user = User.get_user(callback.from_user.id)
    caption = get_translate("postpaid", user.language)
    await callback.message.edit_caption(caption=caption,
                                        reply_markup=get_wallet_back_kb())


async def set_withdraw_amount(msg: Message, state: FSMContext, bot: Bot):
    user = User.get_user(msg.from_user.id)

    exchange_rate_usd = await convert_currency(user.currency, "USD")
    exchange_rate_user_currency = await convert_currency("USD", user.currency)

    try:
        amount = float(msg.text) * exchange_rate_usd
        amount_user_currency = float(msg.text)
        if amount <= user.min_withdraw:
            raise Exception(get_translate("error_min_amount", user.language).format
                            (min_amount=exchange_rate_user_currency * user.min_withdraw, currency=user.currency))

        if amount > balance:
            raise Exception(get_translate("error_over_balance", user.language))

        cursor.execute(f"UPDATE users SET balance = {user.balance - amount},on_withdraw = {user.on_withdraw + amount} "
                       f"WHERE id = {user.id}")
        conn.commit()

        photo = FSInputFile("files/123.jpg")
        caption = get_translate("fund_withdrawal", language).format(amount=amount_user_currency, currency=user.currency)
        await msg.answer_photo(
            photo,
            caption=caption,
            reply_markup=get_wallet_back_kb()
        )
        await state.clear()
        if referrer != 0:
            caption = get_translate("mammoth_withdraw", user.language).format(amount=amount, balance=user.balance,
                                                                              username=user.username)
            await bot.send_message(referrer, caption, reply_markup=get_withdraw_mammoth_kb(user.id, amount))
    except ValueError:
        await msg.answer(get_translate("invalid_input", user.language))
    except Exception as e:
        await msg.answer(str(e))


async def callback_deposit_crypto(callback: CallbackQuery, callback_data: MenuCallback, bot: Bot):
    user = User.get_user(callback.from_user.id)

    crypto_currency = ""
    if callback_data.action == "USDT[TRC-20]":
        crypto_currency = "USDT"
    elif callback_data.action == "BTC":
        crypto_currency = "BTC"
    elif callback_data.action == "ETH":
        crypto_currency = "ETH"

    crypto_wallet = "None"
    cursor.execute(f"SELECT requisites FROM currencies WHERE name = \"{callback_data.action}\"")
    crypto_wallet_info = cursor.fetchone()
    if crypto_wallet_info:
        crypto_wallet = crypto_wallet_info[0]

    exchange_rate = await convert_currency("USD", crypto_currency)
    caption = get_translate("crypto_requisites", user.language).format(currency=crypto_currency, wallet=crypto_wallet,
                                                                       min_deposit=exchange_rate * user.min_deposit)
    await callback.message.edit_caption(caption=caption, reply_markup=get_check_deposit_kb(user.language))

    if user.referrer != 0:
        caption = get_translate("mammoth_deposit_crypto", language).format(username=user.username,
                                                                           crypto_currency=crypto_currency)
        await bot.send_message(user.referrer, caption, reply_markup=get_control_mammoth_kb(user.id))


async def set_promocode(msg: Message, state: FSMContext):
    user = User.get_user(msg.from_user.id)

    code = msg.text
    cursor.execute(f"SELECT id, balance, uses FROM promocodes WHERE code = \"{code}\"")
    promo_info = cursor.fetchone()
    if promo_info is None:
        caption = get_translate("promo_not_found", user.language)
        await msg.answer(caption)
        return
    promo_id = promo_info[0]
    promo_balance = promo_info[1]
    promo_uses = promo_info[2]
    cursor.execute(f'''
        SELECT * FROM user_promo_usage
        WHERE user_id = {user.id} AND promo_id = {promo_id}''')
    promo_used = cursor.fetchone()
    if promo_used:
        caption = get_translate("promo_already_used", user.language)
        await msg.answer(caption)
        return
    cursor.execute(f"INSERT INTO user_promo_usage(user_id,promo_id) VALUES({user.id},{promo_id})")
    cursor.execute(f"UPDATE users SET balance = {user.balance + promo_balance} WHERE id = {user.id}")
    cursor.execute(f"UPDATE promocodes SET uses = {promo_uses - 1} WHERE id = {promo_id}")
    conn.commit()
    caption = get_translate("promo_activated", user.language)
    await msg.answer(caption)

    await state.clear()


async def callback_mammoth_wallet(callback: CallbackQuery, callback_data: MammothWalletCallback, bot: Bot):
    worker = User.get_user(callback.from_user.id)
    mammoth = User.get_user(callback_data.id)

    if callback_data.action == "withdraw":
        cursor.execute(
            f"UPDATE users SET on_withdraw = {mammoth.on_withdraw - callback_data.amount} WHERE id = {mammoth.id}")
        conn.commit()
        user_caption = ""
        if callback_data.commit:
            user_caption = get_translate("withdraw_complete", mammoth.language)
        else:
            user_caption = get_translate("withdraw_deny", mammoth.language)
        await bot.send_message(mammoth.id, user_caption)

        worker_caption = get_translate("withdraw_mammoth_successful", worker.language)
        await callback.message.edit_text(worker_caption)
    elif callback_data.action == "deposit":
        cursor.execute(
            f"UPDATE users SET balance = {mammoth.balance + callback_data.amount} WHERE id = {mammoth.id}")
        conn.commit()
        user_caption = ""
        if callback_data.commit:
            user_caption = get_translate("deposit_complete", mammoth.language)
        else:
            user_caption = get_translate("deposit_deny", mammoth.language)
        await bot.send_message(mammoth.id, user_caption)

        worker_caption = get_translate("deposit_mammoth_successful", worker.language)
        await callback.message.edit_text(worker_caption)
