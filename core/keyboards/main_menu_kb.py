from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.utils.translations import get_translate


class MenuCallback(CallbackData, prefix="menu"):
    menu_name: str
    action: str


def get_main_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=get_translate("btn_marketplace", language),
                                     callback_data=MenuCallback(menu_name="main", action="marketplace").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_wallet", language),
                                     callback_data=MenuCallback(menu_name="main", action="wallet").pack()))
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_change_language", language),
                             callback_data=MenuCallback(menu_name="main", action="change_language").pack()),
        InlineKeyboardButton(text=get_translate("btn_change_currency", language),
                             callback_data=MenuCallback(menu_name="main", action="change_currency").pack())
    )
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_verification", language),
                             callback_data=MenuCallback(menu_name="main", action="verification").pack()),
        InlineKeyboardButton(text=get_translate("btn_tech_support", language),
                             callback_data=MenuCallback(menu_name="main", action="tech_support").pack())
    )
    builder.row(InlineKeyboardButton(text=get_translate("btn_license", language), url="http://fxclub.online/"))
    return builder.as_markup()


def get_change_language_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Russian",
                             callback_data=MenuCallback(menu_name="change_language", action="russian").pack()),
        InlineKeyboardButton(text="English",
                             callback_data=MenuCallback(menu_name="change_language", action="english").pack()))
    builder.row(
        InlineKeyboardButton(text="Polish",
                             callback_data=MenuCallback(menu_name="change_language", action="polish").pack()),
        InlineKeyboardButton(text="Ukrainian",
                             callback_data=MenuCallback(menu_name="change_language", action="ukrainian").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()


def get_change_currency_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="UAH",
                             callback_data=MenuCallback(menu_name="change_currency", action="uah").pack()),
        InlineKeyboardButton(text="EUR",
                             callback_data=MenuCallback(menu_name="change_currency", action="eur").pack()))

    builder.row(
        InlineKeyboardButton(text="USD",
                             callback_data=MenuCallback(menu_name="change_currency", action="usd").pack()),
        InlineKeyboardButton(text="RUB",
                             callback_data=MenuCallback(menu_name="change_currency", action="rub").pack()))
    builder.row(
        InlineKeyboardButton(text="BYN",
                             callback_data=MenuCallback(menu_name="change_currency", action="byn").pack()),
        InlineKeyboardButton(text="ILS",
                             callback_data=MenuCallback(menu_name="change_currency", action="ils").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()


def get_verification_kb(language):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_translate("btn_pass_verification", language),
                                     url="https://t.me/Forex_SupportBot"))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()


def get_tech_support_kb(language):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_translate("btn_tech_support", language),
                                     url="https://t.me/Forex_SupportBot"))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()


def get_back_main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()
