from __future__ import annotations

import asyncio
from datetime import date
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from app.database import Database
from app.keyboards.user import order_menu

logger = logging.getLogger(__name__)


async def reminder_loop(bot: Bot, database: Database, interval_seconds: int) -> None:
    while True:
        try:
            await send_due_reminders(bot, database)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to process reminders")
        await asyncio.sleep(interval_seconds)


async def send_due_reminders(bot: Bot, database: Database) -> None:
    today_iso = date.today().isoformat()
    reminders = await database.due_reminders(today_iso)
    for reminder in reminders:
        try:
            await bot.send_message(
                reminder["user_id"],
                "⏰ Напоминание: пора проверить остаток FitLine и при необходимости оформить повторный заказ.\n\n"
                "Если хотите изменить набор, лучше пройти мини-консультацию или написать консультанту.",
                reply_markup=order_menu(),
            )
            await database.mark_reminder_sent(reminder["id"])
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
        except TelegramForbiddenError:
            await database.set_blocked(reminder["user_id"], True)

