from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.keyboards.main_menu_kb import MenuCallback
from core.utils.sqlite_db import User


def get_worker_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Список мамонтов",
                                     callback_data=MenuCallback(menu_name="worker", action="users_list").pack()))
    builder.row(
        InlineKeyboardButton(text="Рассылка",
                             callback_data=MenuCallback(menu_name="worker", action="mailing").pack()))
    builder.row(InlineKeyboardButton(text="Привязать мамонта",
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="assign_mammoth").pack()))
    builder.row(InlineKeyboardButton(text="Мин. пополнение всем",
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="min_deposit").pack()))
    builder.row(InlineKeyboardButton(text="Мин. вывод всем",
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="min_withdraw").pack()))
    builder.row(
        InlineKeyboardButton(text="Промокод",
                             callback_data=MenuCallback(menu_name="worker", action="promo").pack()))
    builder.row(InlineKeyboardButton(text="Задать валюту",
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="select_currency").pack()))
    builder.row(InlineKeyboardButton(text="Личный линк",
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="private_link").pack()))
    builder.row(InlineKeyboardButton(text="Удалить всех мамонтов",
                                     callback_data=MenuCallback(menu_name="worker",
                                                                action="delete_all_mammoths").pack()))

    return builder.as_markup()


class MammothActionCallback(CallbackData, prefix='mammoth'):
    id: int
    action: str


class MammothsPageCallback(CallbackData, prefix='mammoth_pages'):
    current: int


def get_users_kb(mammoths, current):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Поиск",
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


def get_promo_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Новый промокод",
                                     callback_data=MenuCallback(menu_name="worker_promo", action="new").pack()),
                InlineKeyboardButton(text="Список промокодов",
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


def get_delete_users_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Удалить", callback_data=MenuCallback(menu_name="mammoths_delete",
                                                                                action="").pack()))
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
    builder.row(InlineKeyboardButton(text="Удалить", callback_data=MenuCallback(menu_name="promo_delete",
                                                                                action=code).pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_mammoth_kb(mammoth: User):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Обновить", callback_data=MammothActionCallback(id=mammoth.id, action="info").pack()))
    builder.row(InlineKeyboardButton(text="Выигрыш",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_win").pack()),
                InlineKeyboardButton(text="Проигрыш",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_loss").pack()),
                InlineKeyboardButton(text="Рандом",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_random").pack()),
                InlineKeyboardButton(text="Реальность",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="marketplace_strategy_real").pack()
                                     ))
    if mammoth.verification:
        builder.row(InlineKeyboardButton(text="Забрать верификацию", callback_data=MammothActionCallback(id=mammoth.id,
                                                                                                         action="verification_0").pack()))
    else:
        builder.row(InlineKeyboardButton(text="Выдать верификацию", callback_data=MammothActionCallback(id=mammoth.id,
                                                                                                        action="verification_1").pack()))
    btn_marketplace_status = None
    if mammoth.marketplace_status:
        btn_marketplace_status = InlineKeyboardButton(text="Блокировать торги",
                                                      callback_data=MammothActionCallback(id=mammoth.id,
                                                                                          action="marketplace_status_0").pack())
    else:
        btn_marketplace_status = InlineKeyboardButton(text="Разблокировать торги",
                                                      callback_data=MammothActionCallback(id=mammoth.id,
                                                                                          action="marketplace_status_1").pack())
    btn_withdraw_status = None
    if mammoth.withdraw_status:
        btn_withdraw_status = InlineKeyboardButton(text="Блокировать вывод",
                                                   callback_data=MammothActionCallback(id=mammoth.id,
                                                                                       action="withdraw_status_0").pack())
    else:
        btn_withdraw_status = InlineKeyboardButton(text="Разблокировать вывод",
                                                   callback_data=MammothActionCallback(id=mammoth.id,
                                                                                       action="withdraw_status_1").pack())
    builder.row(btn_marketplace_status, btn_withdraw_status)
    builder.row(InlineKeyboardButton(text="Изменить баланс",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="change_balance").pack()),
                InlineKeyboardButton(text="Добавить к балансу",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="add_balance").pack()))
    builder.row(InlineKeyboardButton(text="Написать",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="mail").pack()))
    builder.row(InlineKeyboardButton(text="Мин. Вывод",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="set_min_withdraw").pack()),
                InlineKeyboardButton(text="Мин. Пополнение",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="set_min_deposit").pack()))
    builder.row(InlineKeyboardButton(text="Удалить",
                                     callback_data=MammothActionCallback(id=mammoth.id,
                                                                         action="delete").pack()))
    if mammoth.blocked:
        builder.row(InlineKeyboardButton(text="Разблокировать",
                                         callback_data=MammothActionCallback(id=mammoth.id,
                                                                             action="unblock").pack()))
    else:
        builder.row(InlineKeyboardButton(text="Заблокировать",
                                         callback_data=MammothActionCallback(id=mammoth.id,
                                                                             action="block").pack()))
    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="worker", action="menu").pack()))

    return builder.as_markup()


def get_mammoth_back_kb(id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="<-", callback_data=MammothActionCallback(id=id, action="info").pack()))
    return builder.as_markup()


def get_control_mammoth_kb(mammoth_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Управление мамонтом",
                                     callback_data=MammothActionCallback(id=mammoth_id, action="info").pack()))
    return builder.as_markup()