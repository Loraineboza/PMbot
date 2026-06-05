import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.database import db
from app.handlers import admin, business, common, company, faq, keywords, order, products, profile, registration, reviews
from app.middlewares.analytics import AnalyticsMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.services.reminders import reminder_loop


async def main() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    await db.connect(settings.database_path)
    await db.init()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    analytics = AnalyticsMiddleware(db)
    throttling = ThrottlingMiddleware(rate_limit=settings.throttle_seconds)
    dp.message.middleware(analytics)
    dp.callback_query.middleware(analytics)
    dp.message.middleware(throttling)
    dp.callback_query.middleware(throttling)

    dp.include_router(common.router)
    dp.include_router(company.router)
    dp.include_router(products.router)
    dp.include_router(business.router)
    dp.include_router(reviews.router)
    dp.include_router(order.router)
    dp.include_router(registration.router)
    dp.include_router(faq.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)
    dp.include_router(keywords.router)

    reminders_task = asyncio.create_task(reminder_loop(bot, db, settings.reminder_check_seconds))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        reminders_task.cancel()
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

