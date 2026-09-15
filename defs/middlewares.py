from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Callable, Dict, Any, Awaitable
import time
import db


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, time_limit: int = 2):
        self.limit = time_limit
        self.users = {}

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.time()

        last_time = self.users.get(user_id, 0)
        if now - last_time < self.limit:
            return

        self.users[user_id] = now
        return await handler(event, data)


class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        user = data.get("event_from_user")

        if user is not None:
            if db.check_on_ban(user.id):

                return

        return await handler(event, data)

