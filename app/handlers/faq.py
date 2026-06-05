from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import content
from app.config import settings
from app.database import db
from app.keyboards import user as kb
from app.services.messages import show_text
from app.states import SupportFlow

router = Router()


@router.callback_query(F.data == "menu:faq")
async def faq_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.FAQ_MENU_TEXT, reply_markup=kb.faq_menu())


@router.callback_query(F.data.startswith("faq:"))
async def faq_item(callback: CallbackQuery) -> None:
    key = callback.data.split(":", 1)[1]
    item = content.FAQ_ITEMS.get(key)
    if not item:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return
    await show_text(callback, f"❔ <b>{item['q']}</b>\n\n{item['a']}", reply_markup=kb.back_main_menu("menu:faq"))


@router.callback_query(F.data == "support:start")
async def support_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SupportFlow.waiting_message)
    await show_text(
        callback,
        "💬 Напишите вопрос для консультанта одним сообщением.\n\n"
        f"Также можно открыть прямой чат: @{settings.consultant_username}",
        reply_markup=kb.support_link_menu(),
    )


@router.message(SupportFlow.waiting_message)
async def support_message(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not 5 <= len(text) <= 1500:
        await message.answer("Сообщение должно быть от 5 до 1500 символов.")
        return

    request_id = await db.add_support_request(message.from_user.id, message.from_user.username, text)
    await state.clear()

    payload = (
        f"💬 Новый запрос консультанту #{request_id}\n\n"
        f"Пользователь: {html.escape(message.from_user.full_name)} / @{html.escape(message.from_user.username or '-')}\n"
        f"ID: <code>{message.from_user.id}</code>\n\n"
        f"{html.escape(text)}"
    )

    targets = list(settings.admin_id_list)
    if settings.consultant_tg_id:
        targets.insert(0, settings.consultant_tg_id)

    for target_id in dict.fromkeys(targets):
        await message.bot.send_message(target_id, payload)

    await message.answer(
        "✅ Сообщение сохранено и передано администратору бота.\n\n"
        f"Если нужен прямой чат, напишите консультанту: @{settings.consultant_username}",
        reply_markup=kb.support_link_menu(),
    )

