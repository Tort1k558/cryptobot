from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.keyboards.main_menu_kb import MenuCallback
from core.utils.sqlite_db import User
from core.utils.translations import get_translate


def get_worker_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_list_mammoths", language),
                                     callback_data=MenuCallback(menu_name="worker", action="users_list").pack()))
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_worker_mailing", language),
                             callback_data=MenuCallback(menu_name="worker", action="mailing").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_assign_mammoth", language),
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="assign_mammoth").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_min_deposit", language),
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="min_deposit").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_min_withdraw", language),
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="min_withdraw").pack()))
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_worker_promo", language),
                             callback_data=MenuCallback(menu_name="worker", action="promo").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_set_currency", language),
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="select_currency").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_private_link", language),
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="private_link").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_delete_mammoths", language),
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="delete_all_mammoths").pack()))

    return builder.as_markup()


class MammothActionCallback(CallbackData, prefix='mammoth'):
    id: int
    action: str


class MammothsPageCallback(CallbackData, prefix='mammoth_pages'):
    current: int


def get_users_kb(mammoths, current, language):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_find", language),
                                     callback_data=MenuCallback(menu_name="worker_mammoths",
                                                                action="find").pack()))

    mammoths_per_page = 6
    current_page = int(current / mammoths_per_page)
    page_mammoths = mammoths[current_page * mammoths_per_page: current_page * mammoths_per_page + mammoths_per_page]
    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MammothsPageCallback(current=mammoths_per_page * max(
                                         (current_page - 1), 0)).pack()),
                InlineKeyboardButton(text=f"{current_page * 6 + len(page_mammoths)}/{len(mammoths)}",
                                     callback_data=" "),
                InlineKeyboardButton(text="->",
                                     callback_data=MammothsPageCallback(current=mammoths_per_page * min(
                                         (current_page + 1), int(len(mammoths) / mammoths_per_page))).pack())
                )
    for mammoth in page_mammoths:
        builder.row(InlineKeyboardButton(text=mammoth[1], callback_data=MammothActionCallback(id=mammoth[0],
                                                                                              action="info").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))
    return builder.as_markup()


def get_worker_back_kb():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_promo_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_new_promo", language),
                                     callback_data=MenuCallback(menu_name="worker_promo", action="new").pack()),
                InlineKeyboardButton(text=get_translate("btn_worker_list_promo", language),
                                     callback_data=MenuCallback(menu_name="worker_promo", action="list").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_currencies_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="UAH",
                                     callback_data=MenuCallback(menu_name="worker_currency",
                                                                action="UAH").pack()),
                InlineKeyboardButton(text="EUR",
                                     callback_data=MenuCallback(menu_name="worker_currency",
                                                                action="EUR").pack()))
    builder.row(InlineKeyboardButton(text="USD",
                                     callback_data=MenuCallback(menu_name="worker_currency",
                                                                action="USD").pack()),
                InlineKeyboardButton(text="RUB",
                                     callback_data=MenuCallback(menu_name="worker_currency",
                                                                action="RUB").pack()))
    builder.row(InlineKeyboardButton(text="BYN",
                                     callback_data=MenuCallback(menu_name="worker_currency",
                                                                action="BYN").pack()),
                InlineKeyboardButton(text="ILS",
                                     callback_data=MenuCallback(menu_name="worker_currency",
                                                                action="ILS").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_delete_users_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoths_delete", language),
                                     callback_data=MenuCallback(menu_name="mammoths_delete", action="").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_worker_promo_list_kb(promocodes):
    builder = InlineKeyboardBuilder()

    for promocode in promocodes:
        builder.row(InlineKeyboardButton(text=promocode[0], callback_data=MenuCallback(menu_name="promo_info",
                                                                                       action=promocode[
                                                                                           0]).pack()))

    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_promo_info_kb(code):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_promo_delete", language),
                                     callback_data=MenuCallback(menu_name="promo_delete", action=code).pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_mammoth_kb(mammoth: User, language):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_worker_mammoth_refresh", language),
                             callback_data=MammothActionCallback(id=mammoth.id, action="info").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_win", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_win").pack()),
                InlineKeyboardButton(text=get_translate("btn_worker_mammoth_loss", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_loss").pack()),
                InlineKeyboardButton(text=get_translate("btn_worker_mammoth_random", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_random").pack()),
                InlineKeyboardButton(text=get_translate("btn_worker_mammoth_real", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_real").pack()
                                     ))
    if mammoth.verification:
        builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_retrieve_verification", language),
                                         callback_data=MammothActionCallback(id=mammoth.id,
                                                                             action="verification_0").pack()))
    else:
        builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_give_verification", language),
                                         callback_data=MammothActionCallback(id=mammoth.id,
                                                                             action="verification_1").pack()))
    btn_marketplace_status = None
    if mammoth.marketplace_status:
        btn_marketplace_status = InlineKeyboardButton(
            text=get_translate("btn_worker_mammoth_block_marketplace", language),
            callback_data=MammothActionCallback(id=mammoth.id,
                                                action="marketplace_status_0").pack())
    else:
        btn_marketplace_status = InlineKeyboardButton(
            text=get_translate("btn_worker_mammoth_unblock_marketplace", language),
            callback_data=MammothActionCallback(id=mammoth.id,
                                                action="marketplace_status_1").pack())
    btn_withdraw_status = None
    if mammoth.withdraw_status:
        btn_withdraw_status = InlineKeyboardButton(text=get_translate("btn_worker_mammoth_block_withdraw", language),
                                                   callback_data=MammothActionCallback(id=mammoth.id,
                                                                                       action="withdraw_status_0").pack())
    else:
        btn_withdraw_status = InlineKeyboardButton(text=get_translate("btn_worker_mammoth_unblock_withdraw", language),
                                                   callback_data=MammothActionCallback(id=mammoth.id,
                                                                                       action="withdraw_status_1").pack())
    builder.row(btn_marketplace_status, btn_withdraw_status)
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_change_balance", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="change_balance").pack()),
                InlineKeyboardButton(text=get_translate("btn_worker_mammoth_add_balance", language),
                                     callback_data=MammothActionCallback(id=mammoth.id, action="add_balance").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_mail", language),
                                     callback_data=MammothActionCallback(id=mammoth.id, action="mail").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_min_withdraw", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="set_min_withdraw").pack()),
                InlineKeyboardButton(text=get_translate("btn_worker_mammoth_min_deposit", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="set_min_deposit").pack()))
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_delete", language),
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="delete").pack()))
    if mammoth.blocked:
        builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_unblock", language),
                                         callback_data=MammothActionCallback(id=mammoth.id,
                                                                             action="unblock").pack()))
    else:
        builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoth_block", language),
                                         callback_data=MammothActionCallback(id=mammoth.id,
                                                                             action="block").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_mammoth_back_kb(id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="<-", callback_data=MammothActionCallback(id=id, action="info").pack()))
    return builder.as_markup()


def get_control_mammoth_kb(mammoth_id, language):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_translate("btn_worker_mammoths_control", language),
                                     callback_data=MammothActionCallback(id=mammoth_id, action="info").pack()))
    return builder.as_markup()
