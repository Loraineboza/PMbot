from __future__ import annotations

from datetime import date, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import content
from app.database import db
from app.keyboards import user as kb
from app.services.messages import show_text
from app.services.recommendations import recommendation_by_answers
from app.states import ConsultationFlow, ReminderFlow

router = Router()


@router.callback_query(F.data == "menu:order")
async def order_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.ORDER_MENU_TEXT, reply_markup=kb.order_menu())


@router.callback_query(F.data == "consult:start")
async def consultation_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ConsultationFlow.waiting_goal)
    await state.update_data(flow="consult")
    await show_text(
        callback,
        content.CONSULTATION_INTRO_TEXT + "\n\n1/3. Какая цель сейчас главная?",
        reply_markup=kb.consultation_goal_menu("consult"),
    )


@router.callback_query(ConsultationFlow.waiting_goal, F.data.startswith("consult:goal:"))
async def consultation_goal(callback: CallbackQuery, state: FSMContext) -> None:
    goal = callback.data.rsplit(":", 1)[-1]
    await state.update_data(goal=goal)
    await state.set_state(ConsultationFlow.waiting_lifestyle)
    await show_text(callback, "2/3. Какой у вас ритм жизни?", reply_markup=kb.consultation_lifestyle_menu("consult"))


@router.callback_query(ConsultationFlow.waiting_lifestyle, F.data.startswith("consult:life:"))
async def consultation_lifestyle(callback: CallbackQuery, state: FSMContext) -> None:
    lifestyle = callback.data.rsplit(":", 1)[-1]
    await state.update_data(lifestyle=lifestyle)
    await state.set_state(ConsultationFlow.waiting_format)
    await show_text(callback, "3/3. Какой формат вам ближе?", reply_markup=kb.consultation_format_menu("consult"))


@router.callback_query(ConsultationFlow.waiting_format, F.data.startswith("consult:format:"))
async def consultation_finish(callback: CallbackQuery, state: FSMContext) -> None:
    preferred_format = callback.data.rsplit(":", 1)[-1]
    data = await state.get_data()
    goal = data.get("goal", "health")
    lifestyle = data.get("lifestyle", "soft")
    text, slugs = recommendation_by_answers(goal, lifestyle, preferred_format)
    await state.clear()
    await show_text(callback, text, reply_markup=kb.product_search_results_menu(slugs))


@router.callback_query(F.data == "order:reminder")
async def reminder_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReminderFlow.waiting_date)
    await show_text(
        callback,
        "⏰ Когда напомнить о повторном заказе?\n\n"
        "Напишите дату в формате <b>YYYY-MM-DD</b> или число дней, например <b>30</b>.",
        reply_markup=kb.back_main_menu("menu:order"),
    )


@router.message(ReminderFlow.waiting_date)
async def reminder_save(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    target_date: date | None = None

    if raw.isdigit():
        days = int(raw)
        if not 1 <= days <= 365:
            await message.answer("Укажите число дней от 1 до 365.")
            return
        target_date = date.today() + timedelta(days=days)
    else:
        try:
            target_date = date.fromisoformat(raw)
        except ValueError:
            await message.answer("Не понял дату. Пример: 2026-07-05 или просто 30.")
            return
        if target_date < date.today():
            await message.answer("Дата уже прошла. Укажите будущую дату.")
            return

    await db.add_reminder(message.from_user.id, target_date.isoformat(), "repeat_order")
    await state.clear()
    await message.answer(
        f"✅ Готово. Напомню о повторном заказе <b>{target_date.isoformat()}</b>.",
        reply_markup=kb.order_menu(),
    )

