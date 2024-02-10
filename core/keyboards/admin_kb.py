from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.keyboards.main_menu_kb import MenuCallback
from core.utils.translations import get_translate


def get_admin_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Сменить реквизиты",
                             callback_data=MenuCallback(menu_name="admin", action="change_requisites").pack()))
    builder.row(
        InlineKeyboardButton(text="Добавить воркера",
                             callback_data=MenuCallback(menu_name="admin", action="add_worker").pack()),
        InlineKeyboardButton(text="Удалить воркера",
                             callback_data=MenuCallback(menu_name="admin", action="delete_worker").pack()))

    return builder.as_markup()


def get_admin_back_kb():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="<-",
                             callback_data=MenuCallback(menu_name="admin", action="menu").pack()))

    return builder.as_markup()


def get_change_requisites_kb():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="UAH",
                             callback_data=MenuCallback(menu_name="change_requisites", action="UAH").pack()),
        InlineKeyboardButton(text="EUR",
                             callback_data=MenuCallback(menu_name="change_requisites", action="EUR").pack()))
    builder.row(
        InlineKeyboardButton(text="USD",
                             callback_data=MenuCallback(menu_name="change_requisites", action="USD").pack()),
        InlineKeyboardButton(text="RUB",
                             callback_data=MenuCallback(menu_name="change_requisites", action="RUB").pack()))
    builder.row(
        InlineKeyboardButton(text="BYN",
                             callback_data=MenuCallback(menu_name="change_requisites", action="BYN").pack()),
        InlineKeyboardButton(text="ILS",
                             callback_data=MenuCallback(menu_name="change_requisites", action="ILS").pack()))

    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="admin", action="menu").pack()))
    return builder.as_markup()
