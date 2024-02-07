import logging

from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.main_menu_kb import *
from core.keyboards.marketplace_kb import *
from core.keyboards.wallet_kb import *

from core.utils.sqlite_db import cursor, conn, User
from core.utils.converter import convert_currency
from core.utils.translations import get_translate

from core.handlers.briefcase_marketplace import *
from core.handlers.briefcase_wallet import *

client_router = Router()


async def command_start(msg: Message, command: CommandObject, state: FSMContext):
    await msg.answer(get_translate("start", "russian"))
    cursor.execute(f"SELECT id FROM users WHERE id = {msg.from_user.id}")
    existing_user = cursor.fetchone()
    if not existing_user:
        referrer_id = 0
        min_deposit = 1.0
        min_withdraw = 1.0
        language = "russian"
        currency = "USD"

        if command.args:
            ref_id = int(command.args)
            cursor.execute(
                f"SELECT min_deposit,min_withdraw,default_language,default_currency FROM workers WHERE id ={ref_id}")
            referrer = cursor.fetchone()
            if referrer:
                referrer_id = ref_id
                min_deposit = referrer[0]
                min_withdraw = referrer[1]
                language = referrer[2]
                currency = referrer[3]
        cursor.execute(f""" INSERT INTO users(id, username, language, currency, min_deposit, 
        min_withdraw, referrer, ) VALUES ({msg.from_user.id},"{msg.from_user.username}", "{language}",
        "{currency}", {min_deposit}, {min_withdraw}, {referrer_id})""")
        conn.commit()
    await get_portfolio(msg, state)


async def get_portfolio_caption(user: User) -> str:
    exchange_rate = await convert_currency("USD", user.currency)

    cursor.execute(f"SELECT COUNT(id) FROM transactions WHERE user_id = {user.id}")
    user_transactions = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(id) FROM transactions WHERE made = 1")
    all_transactions = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(id) FROM users WHERE referrer = {user.id}")
    referrals = cursor.fetchone()[0]

    caption = get_translate("briefcase", user.language).format(username=user.username,
                                                               balance=round(user.balance * exchange_rate, 4),
                                                               currency=user.currency,
                                                               verification="✅" if user.verification else "❌",
                                                               user_transactions=user_transactions,
                                                               referrals=referrals,
                                                               active_transactions=all_transactions,
                                                               id=user.id)

    return caption


async def get_portfolio(msg: Message, state: FSMContext):
    user = User.get_user(msg.from_user.id)

    caption = await get_portfolio_caption(user)

    photo = FSInputFile("files/123.jpg")

    await msg.answer_photo(photo, caption=caption, reply_markup=get_main_kb(user.language))

    await state.set_state(state=None)


async def callback_main_menu(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    user = User.get_user(callback.from_user.id)

    if callback_data.action == "menu":
        await callback.message.edit_caption(caption=await get_portfolio_caption(user),
                                            reply_markup=get_main_kb(user.language))
        await state.clear()
    elif callback_data.action == "marketplace":
        if user.marketplace_status:
            await callback.message.edit_caption(caption=get_translate("marketplace", user.language),
                                                reply_markup=get_marketplace_kb(user.language))
        else:
            await callback.message.edit_caption(caption=get_translate("marketplace_blocked", user.language),
                                                reply_markup=get_back_main_kb())
    elif callback_data.action == "wallet":
        exchange_rate = await convert_currency("USD", user.currency)

        caption = get_translate("your_wallet", user.language).format(user_id=user.id,
                                                                     balance=round(user.balance * exchange_rate, 4),
                                                                     currency=user.currency)

        await callback.message.edit_caption(caption=caption, reply_markup=get_wallet_kb(user.language))
    elif callback_data.action == "change_language":
        caption = get_translate("change_language", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_change_language_kb())
    elif callback_data.action == "change_currency":
        caption = get_translate("change_currency", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_change_currency_kb())
    elif callback_data.action == "verification":
        await callback.message.edit_caption(caption=get_translate("verification_caption", user.language),
                                            reply_markup=get_verification_kb(user.language))
    elif callback_data.action == "tech_support":
        await callback.message.edit_caption(caption=get_translate("tech_support_caption", user.language),
                                            reply_markup=get_tech_support_kb(user.language))


async def callback_change_currency(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    cursor.execute(f"UPDATE users SET currency = \"{callback_data.action.upper()}\" WHERE id = {callback.from_user.id}")
    conn.commit()

    await callback_main_menu(callback, MenuCallback(menu_name="main", action="menu"), state)


async def callback_change_language(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    cursor.execute(f"UPDATE users SET language = \"{callback_data.action}\" WHERE id = {callback.from_user.id}")
    conn.commit()
    await callback_main_menu(callback, MenuCallback(menu_name="main", action="menu"), state)


client_router.message.register(command_start, Command("start"))
client_router.message.register(get_portfolio, Command("briefcase"))
client_router.callback_query.register(callback_main_menu, MenuCallback.filter(F.menu_name == "main"))

# Marketplace
client_router.callback_query.register(callback_marketplace_menu,
                                      MenuCallback.filter(F.menu_name == "marketplace"))
client_router.callback_query.register(callback_marketplace_assets,
                                      MenuCallback.filter(F.menu_name == "marketplace_assets"))
client_router.callback_query.register(callback_asset_action,
                                      AssetActionCallback.filter())

client_router.message.register(get_asset_position, PositionStates.setting_amount)

client_router.callback_query.register(callback_process_position,
                                      PositionData.filter())

# Wallet
client_router.callback_query.register(callback_wallet_menu, MenuCallback.filter(F.menu_name == "wallet"))
client_router.callback_query.register(callback_pay_method_menu,
                                      MenuCallback.filter(F.menu_name == "wallet_deposit"))
client_router.callback_query.register(callback_mammoth_wallet,
                                      MammothWalletCallback.filter())

client_router.message.register(set_deposit_card_amount, DepositCard.setting_amount)

client_router.callback_query.register(callback_deposit_crypto,
                                      MenuCallback.filter(F.menu_name == "deposit_crypto"))

client_router.message.register(set_withdraw_amount, Withdraw.setting_amount)
client_router.callback_query.register(callback_check_deposit,
                                      MenuCallback.filter(F.menu_name == "check_deposit"))

client_router.message.register(set_promocode, Promocode.setting_code)

# Changes
client_router.callback_query.register(callback_change_currency,
                                      MenuCallback.filter(F.menu_name == "change_currency"))
client_router.callback_query.register(callback_change_language,
                                      MenuCallback.filter(F.menu_name == "change_language"))
