from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.keyboards.main_menu_kb import MenuCallback
from core.utils.translations import get_translate


def get_marketplace_kb(language):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="FAQ",
                                     callback_data=MenuCallback(menu_name="marketplace", action="faq").pack()))
    builder.row(
        InlineKeyboardButton(text=get_translate("btn_cryptocurrencies", language),
                             callback_data=MenuCallback(menu_name="marketplace",
                                                        action="cryptocurrency").pack()),
        InlineKeyboardButton(text=get_translate("btn_company_shares", language),
                             callback_data=MenuCallback(menu_name="marketplace",
                                                        action="company_shares").pack()))

    builder.row(
        InlineKeyboardButton(text="<-", callback_data=MenuCallback(menu_name="main", action="menu").pack()))
    return builder.as_markup()


def get_marketplace_faq_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="marketplace").pack()))
    return builder.as_markup()


def get_marketplace_crypto_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Bitcoin",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="BTC").pack()),
        InlineKeyboardButton(text="Etherium",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="ETH").pack()))
    builder.row(
        InlineKeyboardButton(text="Ada",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="ADA").pack()),
        InlineKeyboardButton(text="DogeCoin",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="DOGE").pack()))
    builder.row(
        InlineKeyboardButton(text="Matic",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="MATIC").pack()),
        InlineKeyboardButton(text="Solana",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="SOL").pack()))
    builder.row(
        InlineKeyboardButton(text="Fill",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="FIL").pack()),
        InlineKeyboardButton(text="Litecoin",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="LTC").pack()))

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="marketplace").pack()))
    return builder.as_markup()


class AssetActionCallback(CallbackData, prefix="crypto_select_action"):
    asset: str
    action: str


def get_asset_action_kb(asset):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Обновить",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action=asset).pack()))
    builder.row(
        InlineKeyboardButton(text="Long",
                             callback_data=AssetActionCallback(asset=asset, action="long").pack()))
    builder.row(
        InlineKeyboardButton(text="Short",
                             callback_data=AssetActionCallback(asset=asset, action="short").pack()))
    back_menu = "cryptocurrency"
    if asset.startswith("stock"):
        back_menu = "company_shares"
    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="marketplace",
                                                                action=back_menu).pack()))
    return builder.as_markup()


def get_asset_action_back_kb(asset):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="marketplace_assets",
                                                                action=asset).pack()))
    return builder.as_markup()


def get_marketplace_stocks_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Amazon",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="stock_AMZN").pack()),
        InlineKeyboardButton(text="Tesla",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="stock_TSLA").pack()))
    builder.row(
        InlineKeyboardButton(text="Apple",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="stock_AAPL").pack()),
        InlineKeyboardButton(text="Google",
                             callback_data=MenuCallback(menu_name="marketplace_assets", action="stock_GOOGL").pack()))

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="marketplace").pack()))
    return builder.as_markup()


class PositionData(CallbackData, prefix="position"):
    asset: str
    action: str
    amount: float
    duration: int


def get_asset_action_time_kb(asset, action, amount):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="10s",
                             callback_data=PositionData(asset=asset, action=action, amount=amount, duration=10).pack()),
        InlineKeyboardButton(text="30s",
                             callback_data=PositionData(asset=asset, action=action, amount=amount, duration=30).pack()),
        InlineKeyboardButton(text="60s",
                             callback_data=PositionData(asset=asset, action=action, amount=amount, duration=60).pack()))

    builder.row(InlineKeyboardButton(text="<-",
                                     callback_data=MenuCallback(menu_name="main", action="marketplace").pack()))
    return builder.as_markup()
