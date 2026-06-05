from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import content
from app.database import db
from app.keyboards import user as kb
from app.services.messages import show_text

router = Router()


@router.callback_query(F.data == "menu:registration")
async def registration_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.REGISTRATION_MENU_TEXT, reply_markup=kb.registration_menu())


@router.callback_query(F.data == "registration:steps")
async def registration_steps(callback: CallbackQuery) -> None:
    await show_text(callback, content.REGISTRATION_STEPS_TEXT, reply_markup=kb.registration_link_menu())


@router.callback_query(F.data == "registration:packages")
async def registration_packages(callback: CallbackQuery) -> None:
    await show_text(callback, content.START_PACKAGES_TEXT, reply_markup=kb.registration_link_menu())


@router.callback_query(F.data == "registration:open")
async def registration_open(callback: CallbackQuery) -> None:
    await db.add_event(callback.from_user.id, "conversion", "registration_click")
    await show_text(
        callback,
        "🔗 Официальная регистрация PM-International открывается по кнопке ниже.\n\n"
        "Проверьте страну, данные консультанта, условия и актуальный состав стартовых вариантов на сайте.",
        reply_markup=kb.registration_link_menu(),
    )

