from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.database import Database


class AnalyticsMiddleware(BaseMiddleware):
    def __init__(self, database: Database) -> None:
        self.database = database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if user is not None:
            await self.database.upsert_user(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name,
                language_code=user.language_code,
            )

        if isinstance(event, CallbackQuery):
            await self.database.add_event(user.id if user else None, "callback", event.data)
        elif isinstance(event, Message):
            payload = "text"
            if event.text and event.text.startswith("/"):
                payload = event.text.split(maxsplit=1)[0]
            await self.database.add_event(user.id if user else None, "message", payload)

        return await handler(event, data)

