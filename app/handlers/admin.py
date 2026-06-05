from __future__ import annotations

import asyncio
import html

from aiogram import F, Router
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import content
from app.config import settings
from app.database import db
from app.keyboards import admin as admin_kb
from app.services.messages import show_text
from app.states import AdminBroadcastFlow

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_list


async def _deny_message(message: Message) -> None:
    await message.answer(
        "Админ-панель недоступна. Добавьте ваш Telegram ID в переменную ADMIN_IDS и перезапустите бота."
    )


async def _deny_callback(callback: CallbackQuery) -> None:
    await callback.answer("Нет доступа к админ-панели.", show_alert=True)


@router.message(Command("admin"))
async def admin_command(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await _deny_message(message)
        return
    await message.answer(content.ADMIN_MENU_TEXT, reply_markup=admin_kb.admin_menu())


@router.callback_query(F.data == "admin:panel")
async def admin_panel(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_callback(callback)
        return
    await show_text(callback, content.ADMIN_MENU_TEXT, reply_markup=admin_kb.admin_menu())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_callback(callback)
        return

    stats = await db.stats()
    top = "\n".join(f"• <code>{html.escape(payload)}</code>: {count}" for payload, count in stats["top_buttons"])
    if not top:
        top = "пока нет данных"

    text = f"""
📊 <b>Статистика</b>

Пользователи: <b>{stats['users']}</b>
Подписчики рассылки: <b>{stats['subscribed']}</b>
Заблокировали бота: <b>{stats['blocked']}</b>

Отзывы:
• на модерации: <b>{stats['pending_reviews']}</b>
• опубликовано: <b>{stats['approved_reviews']}</b>

Новые обращения: <b>{stats['support_new']}</b>
Клики по регистрации: <b>{stats['registration_clicks']}</b>
Завершённых квизов: <b>{stats['quiz_finished']}</b>

<b>Популярные кнопки</b>
{top}
""".strip()
    await show_text(callback, text, reply_markup=admin_kb.admin_menu())


@router.callback_query(F.data == "admin:broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_callback(callback)
        return
    await state.set_state(AdminBroadcastFlow.waiting_text)
    await show_text(
        callback,
        "📣 Отправьте текст рассылки.\n\n"
        "Он уйдёт только пользователям, которые дали согласие через кнопку «Подписаться». "
        "Максимум 3500 символов.",
        reply_markup=admin_kb.admin_menu(),
    )


@router.message(AdminBroadcastFlow.waiting_text)
async def broadcast_send(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        await _deny_message(message)
        await state.clear()
        return

    text = (message.text or "").strip()
    if not 1 <= len(text) <= 3500:
        await message.answer("Текст рассылки должен быть от 1 до 3500 символов.")
        return

    users = await db.subscribed_users()
    await state.clear()
    if not users:
        await message.answer("Нет подписчиков для рассылки.", reply_markup=admin_kb.admin_menu())
        return

    sent = 0
    blocked = 0
    failed = 0
    status = await message.answer(f"Начинаю рассылку по {len(users)} подписчикам...")
    for user_id in users:
        try:
            await message.bot.send_message(user_id, text)
            sent += 1
            await asyncio.sleep(0.05)
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
        except TelegramForbiddenError:
            blocked += 1
            await db.set_blocked(user_id, True)
        except Exception:
            failed += 1

    await db.add_event(message.from_user.id, "admin", f"broadcast:{sent}")
    await status.edit_text(
        f"📣 Рассылка завершена.\n\nОтправлено: {sent}\nЗаблокировали бота: {blocked}\nОшибки: {failed}",
        reply_markup=admin_kb.admin_menu(),
    )


@router.callback_query(F.data == "admin:reviews")
async def admin_reviews(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_callback(callback)
        return

    rows = await db.list_reviews(status="pending", limit=5)
    if not rows:
        await show_text(callback, "📝 Нет отзывов на модерации.", reply_markup=admin_kb.admin_menu())
        return

    first = rows[0]
    text = _review_admin_text(first, total=len(rows))
    await show_text(callback, text, reply_markup=admin_kb.review_moderation_menu(first["id"]))


@router.callback_query(F.data.startswith("admin:review:"))
async def admin_review_action(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_callback(callback)
        return

    _, _, action, raw_id = callback.data.split(":")
    review_id = int(raw_id)
    review = await db.get_review(review_id)
    if not review:
        await callback.answer("Отзыв не найден.", show_alert=True)
        return

    if action == "approve":
        await db.moderate_review(review_id, "approved")
        await callback.bot.send_message(review["user_id"], "✅ Ваш отзыв опубликован после модерации.")
        await show_text(callback, f"✅ Отзыв #{review_id} опубликован.", reply_markup=admin_kb.admin_menu())
        return

    if action == "reject":
        await db.moderate_review(review_id, "rejected", "Rejected by admin")
        await callback.bot.send_message(
            review["user_id"],
            "Спасибо за отзыв. Он не был опубликован, потому что не прошёл модерацию по правилам формулировок.",
        )
        await show_text(callback, f"🚫 Отзыв #{review_id} отклонён.", reply_markup=admin_kb.admin_menu())
        return

    await callback.answer("Неизвестное действие.", show_alert=True)


def _review_admin_text(row, total: int) -> str:
    username = f"@{row['username']}" if row["username"] else "без username"
    return f"""
📝 <b>Отзыв на модерации</b>

В очереди: {total}
ID: <code>{row['id']}</code>
Пользователь: {html.escape(username)}
Оценка: {'⭐' * int(row['rating'])}
Дата: {row['created_at']}

{html.escape(row['text'])}
""".strip()

