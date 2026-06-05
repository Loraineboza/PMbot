from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import content
from app.database import db
from app.keyboards import user as kb
from app.services.messages import show_text

router = Router()


@router.callback_query(F.data == "menu:profile")
async def profile(callback: CallbackQuery) -> None:
    user = await db.get_user(callback.from_user.id)
    reminders = await db.list_active_reminders(callback.from_user.id)
    is_subscribed = bool(user and user["is_subscribed"])
    subscription = "включена" if is_subscribed else "выключена"
    reminder_text = "\n".join(f"• {row['reminder_date']}" for row in reminders) if reminders else "нет активных напоминаний"

    text = (
        f"{content.PROFILE_TEXT}\n\n"
        f"<b>Ваши данные в боте:</b>\n"
        f"• Telegram ID: <code>{callback.from_user.id}</code>\n"
        f"• Рассылка: {subscription}\n"
        f"• Напоминания: {reminder_text}"
    )
    await show_text(callback, text, reply_markup=kb.profile_menu(is_subscribed))

