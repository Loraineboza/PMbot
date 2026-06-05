from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.8) -> None:
        self.rate_limit = rate_limit
        self._last_seen: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_seen.get(user.id, 0.0)
        if now - last < self.rate_limit:
            if isinstance(event, CallbackQuery):
                await event.answer("Секунду, обрабатываю предыдущий запрос.", show_alert=False)
            elif isinstance(event, Message):
                await event.answer("Секунду, пожалуйста.")
            return None

        self._last_seen[user.id] = now
        return await handler(event, data)

