from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app import content
from app.database import db
from app.keyboards import user as kb
from app.services.messages import show_text

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await db.add_event(message.from_user.id, "command", "start")
    await message.answer(content.START_TEXT, reply_markup=kb.main_menu())


@router.message(Command("menu"))
async def menu(message: Message) -> None:
    await message.answer(content.START_TEXT, reply_markup=kb.main_menu())


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(content.HELP_TEXT, reply_markup=kb.main_menu())


@router.callback_query(F.data == "nav:main")
async def nav_main(callback: CallbackQuery) -> None:
    await show_text(callback, content.START_TEXT, reply_markup=kb.main_menu())


@router.callback_query(F.data == "library:open")
async def library(callback: CallbackQuery) -> None:
    await show_text(callback, content.LIBRARY_TEXT, reply_markup=kb.library_menu())


@router.callback_query(F.data == "subscription:open")
async def subscription_open(callback: CallbackQuery) -> None:
    user = await db.get_user(callback.from_user.id)
    is_subscribed = bool(user and user["is_subscribed"])
    await show_text(callback, content.SUBSCRIPTION_TEXT, reply_markup=kb.subscription_menu(is_subscribed))


@router.callback_query(F.data == "subscription:on")
async def subscription_on(callback: CallbackQuery) -> None:
    await db.set_subscription(callback.from_user.id, True)
    await db.add_event(callback.from_user.id, "conversion", "subscription_on")
    await show_text(
        callback,
        "✅ Вы подписались на рассылку.\n\nБуду отправлять только полезные материалы и напоминания. Отписаться можно в этом же разделе.",
        reply_markup=kb.subscription_menu(True),
    )


@router.callback_query(F.data == "subscription:off")
async def subscription_off(callback: CallbackQuery) -> None:
    await db.set_subscription(callback.from_user.id, False)
    await show_text(
        callback,
        "🔕 Вы отписались от рассылки.\n\nСервисные сообщения, например напоминания о заказе, останутся только если вы сами их настроили.",
        reply_markup=kb.subscription_menu(False),
    )

