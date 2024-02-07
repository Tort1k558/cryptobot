import logging

import requests
import json
import aiohttp
import time

import yfinance as yf

exchange_rates_cache = {}
update_time = 3


async def fetch_exchange_rates(currency: str):
    current_time = time.time()

    if currency not in exchange_rates_cache or current_time - exchange_rates_cache[currency]["timestamp"] > update_time:
        url = f"https://api.coinbase.com/v2/exchange-rates?currency={currency}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                exchange_rates_data = await response.json()
                exchange_rates_cache[currency] = {
                    "data": exchange_rates_data,
                    "timestamp": current_time
                }

    return exchange_rates_cache[currency]["data"]


async def convert_from_usd(to_currency: str):
    result = await fetch_exchange_rates("USD")
    return round(float(result["data"]["rates"][to_currency]), 4)


async def convert_to_usd(from_currency: str):
    result = await fetch_exchange_rates("USD")
    return round(1.0 / float(result["data"]["rates"][from_currency]), 4)


async def convert_currency(from_currency: str, to_currency: str):
    if from_currency.startswith("stock") and not to_currency.startswith("stock"):
        stock_price = get_stock_price(from_currency.split("_")[1])
        usd_to_currency = await convert_from_usd(to_currency)
        return round(usd_to_currency * stock_price, 4)
    elif not from_currency.startswith("stock") and to_currency.startswith("stock"):
        stock_price = get_stock_price(to_currency.split("_")[1])
        usd_to_currency = await convert_from_usd(from_currency)
        return usd_to_currency * stock_price
    elif from_currency.startswith("stock") and to_currency.startswith("stock"):
        from_stock_price = get_stock_price(from_currency.split("_")[1])
        to_stock_price = get_stock_price(to_currency.split("_")[1])
        return from_stock_price / to_stock_price
    else:
        from_rate_usd = await convert_to_usd(from_currency)
        to_rate_usd = await convert_to_usd(to_currency)
        return round(from_rate_usd/to_rate_usd, 4)


def get_stock_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        current_price = stock.info["currentPrice"]
        return current_price
    except Exception as e:
        print(f"Ошибка при получении цены акций: {e}")
        return None
