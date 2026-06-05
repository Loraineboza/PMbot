from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="admin:stats")
    builder.button(text="📣 Рассылка", callback_data="admin:broadcast")
    builder.button(text="📝 Модерация отзывов", callback_data="admin:reviews")
    builder.button(text="🏠 Главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def review_moderation_menu(review_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Одобрить", callback_data=f"admin:review:approve:{review_id}")
    builder.button(text="🚫 Отклонить", callback_data=f"admin:review:reject:{review_id}")
    builder.button(text="📝 К списку", callback_data="admin:reviews")
    builder.button(text="🛠 Админка", callback_data="admin:panel")
    builder.adjust(2, 1, 1)
    return builder.as_markup()

