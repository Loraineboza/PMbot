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
from app.states import ReviewFlow

router = Router()


@router.callback_query(F.data == "menu:reviews")
async def reviews_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.REVIEWS_MENU_TEXT, reply_markup=kb.reviews_menu())


@router.callback_query(F.data == "reviews:list")
async def reviews_list(callback: CallbackQuery) -> None:
    rows = await db.list_reviews(status="approved", limit=7)
    if not rows:
        await show_text(callback, content.DEFAULT_REVIEWS_TEXT, reply_markup=kb.reviews_menu())
        return

    parts = ["💬 <b>Опубликованные отзывы</b>"]
    for row in rows:
        username = f"@{row['username']}" if row["username"] else "пользователь"
        stars = "⭐" * int(row["rating"])
        parts.append(f"\n{stars}\n<b>{html.escape(username)}</b>: {html.escape(row['text'])}")
    await show_text(callback, "\n".join(parts), reply_markup=kb.reviews_menu())


@router.callback_query(F.data == "reviews:videos")
async def reviews_videos(callback: CallbackQuery) -> None:
    await show_text(callback, content.VIDEO_REVIEWS_TEXT, reply_markup=kb.back_main_menu("menu:reviews"))


@router.callback_query(F.data == "reviews:before_after")
async def reviews_before_after(callback: CallbackQuery) -> None:
    await show_text(callback, content.BEFORE_AFTER_TEXT, reply_markup=kb.back_main_menu("menu:reviews"))


@router.callback_query(F.data == "reviews:add")
async def review_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReviewFlow.waiting_rating)
    await show_text(callback, "✍️ Оцените опыт от 1 до 5. Отправьте только цифру.", reply_markup=kb.back_main_menu("menu:reviews"))


@router.message(ReviewFlow.waiting_rating)
async def review_rating(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw not in {"1", "2", "3", "4", "5"}:
        await message.answer("Пожалуйста, отправьте цифру от 1 до 5.")
        return
    await state.update_data(rating=int(raw))
    await state.set_state(ReviewFlow.waiting_text)
    await message.answer(
        "Теперь напишите отзыв: что было удобно, какая цель, какой формат понравился.\n\n"
        "Не пишите диагнозы и заявления об излечении. Минимум 20 символов, максимум 1000."
    )


@router.message(ReviewFlow.waiting_text)
async def review_text(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not 20 <= len(text) <= 1000:
        await message.answer("Отзыв должен быть от 20 до 1000 символов.")
        return

    data = await state.get_data()
    review_id = await db.add_review(
        user_id=message.from_user.id,
        username=message.from_user.username,
        rating=int(data["rating"]),
        text=text,
    )
    await state.clear()

    for admin_id in settings.admin_id_list:
        await message.bot.send_message(
            admin_id,
            f"📝 Новый отзыв на модерации #{review_id}\n\n"
            f"Пользователь: {html.escape(message.from_user.full_name)} / @{html.escape(message.from_user.username or '-')}\n"
            f"Оценка: {data['rating']}\n\n{html.escape(text)}",
        )

    await message.answer(
        "✅ Спасибо. Отзыв сохранён и отправлен на модерацию перед публикацией.",
        reply_markup=kb.reviews_menu(),
    )

