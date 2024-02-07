import asyncio
import logging
from typing import Any, Callable, Dict, Awaitable

from config_reader import config
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods.delete_webhook import DeleteWebhook
from aiogram.types import TelegramObject

from core.handlers.briefcase_main import client_router
from core.handlers.worker_main import worker_router
from core.handlers.admin import admin_router
from core.utils.sqlite_db import sql_start, cursor, conn

logging.basicConfig(level=logging.INFO)

bot = Bot(config.bot_token, parse_mode='HTML')
dp = Dispatcher(storage=MemoryStorage())


class BlockedMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        cursor.execute(f"SELECT blocked FROM users WHERE id = {user.id}")
        blocked = cursor.fetchone()[0]
        if not blocked:
            return await handler(event, data)


async def main():
    sql_start()
    dp.message.middleware(BlockedMiddleware())
    dp.callback_query.middleware(BlockedMiddleware())
    dp.include_router(client_router)
    dp.include_router(worker_router)
    dp.include_router(admin_router)

    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)
    await bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        logging.info("Bot was successfully completed")
