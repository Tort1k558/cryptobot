from typing import Any, Callable, Dict, Awaitable

from aiogram import types, Dispatcher, F, Router, Bot, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, TelegramObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.keyboards.worker_kb import *
from core.utils.translations import get_translate
from core.utils.sqlite_db import cursor, conn

from core.handlers.worker_promo import *
from core.handlers.worker_mammoths import *


class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        cursor.execute(f"SELECT * FROM admins WHERE id = {user.id}")
        worker = cursor.fetchone()
        if worker:
            return await handler(event, data)


admin_router = Router()
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


async def command_admin(msg: Message):
    admin = User.get_user(msg.from_user.id)
    caption = get_translate("hello_admin", admin.language)
    await msg.answer(caption)


admin_router.message.register(command_admin, Command("admin"))
