from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.keyboards.main_menu_kb import MenuCallback
from core.utils.translations import get_translate
from core.keyboards.worker_kb import MammothActionCallback


def get_wallet_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=get_translate("btn_deposit", language),
                             callback_data=MenuCallback(menu_name="wallet", action="deposit").pack()),
        InlineKeyboardButton(text=get_translate("btn_withdraw", language),
                             callback_data=MenuCallback(menu_name="wallet", action="withdraw").pack()))
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_promo", language),
                             callback_data=MenuCallback(menu_name="wallet", action="promo").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()


def get_deposit_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=get_translate("btn_card", language),
                             callback_data=MenuCallback(menu_name="wallet_deposit", action="card").pack()),
        InlineKeyboardButton(text=get_translate("btn_cryptocurrencies", language),
                             callback_data=MenuCallback(menu_name="wallet_deposit", action="crypto").pack()))

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="wallet").pack()))
    return builder.as_markup()


def get_deposit_card_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="wallet", action="deposit").pack()))
    return builder.as_markup()


def get_check_deposit_kb(language):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_translate("btn_check_payment", language),
                                     callback_data=MenuCallback(menu_name="check_deposit", action="card").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_tech_support", language), url="https://t.me/Forex_SupportBot"))
    return builder.as_markup()


def get_deposit_crypto_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="USDT[TRC-20]",
                                     callback_data=MenuCallback(menu_name="deposit_crypto",
                                                                action="USDT[TRC-20]").pack()))
    builder.row(InlineKeyboardButton(text="BTC", callback_data=MenuCallback(menu_name="deposit_crypto",
                                                                            action="BTC").pack()))
    builder.row(InlineKeyboardButton(text="ETH", callback_data=MenuCallback(menu_name="deposit_crypto",
                                                                            action="ETH").pack()))
    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="wallet", action="deposit").pack()))
    return builder.as_markup()


def get_wallet_back_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="wallet").pack()))
    return builder.as_markup()


def get_promo_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="wallet").pack()))
    return builder.as_markup()


class MammothWalletCallback(CallbackData, prefix="mammoth_wallet"):
    action: str
    commit: bool
    id: int
    amount: float


def get_withdraw_mammoth_kb(mammoth_id, amount):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅",
                             callback_data=MammothWalletCallback(action="withdraw", amount=amount, commit=True,
                                                                 id=mammoth_id).pack()),
        InlineKeyboardButton(text="❌",
                             callback_data=MammothWalletCallback(action="withdraw", amount=amount, commit=False,
                                                                 id=mammoth_id).pack()))
    return builder.as_markup()


def get_deposit_card_mammoth_kb(mammoth_id, amount):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅",
                             callback_data=MammothWalletCallback(action="deposit", amount=amount, commit=True,
                                                                 id=mammoth_id).pack()),
        InlineKeyboardButton(text="❌",
                             callback_data=MammothWalletCallback(action="deposit", amount=amount, commit=False,
                                                                 id=mammoth_id).pack()))
    return builder.as_markup()

