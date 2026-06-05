from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import content
from app.config import settings


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏢 О компании PM-International", callback_data="menu:company")
    builder.button(text="🧃 Продукты FitLine", callback_data="menu:products")
    builder.button(text="💼 Бизнес-возможности", callback_data="menu:business")
    builder.button(text="💬 Отзывы и результаты", callback_data="menu:reviews")
    builder.button(text="🛒 Как заказать / Магазин", callback_data="menu:order")
    builder.button(text="📝 Регистрация", callback_data="menu:registration")
    builder.button(text="❓ FAQ / Поддержка", callback_data="menu:faq")
    builder.button(text="👤 Мой профиль", callback_data="menu:profile")
    builder.adjust(1)
    return builder.as_markup()


def company_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📜 История", callback_data="company:history")
    builder.button(text="📌 Факты", callback_data="company:facts")
    builder.button(text="🧬 Философия NTC", callback_data="company:philosophy")
    builder.button(text="🔗 Официальные ссылки", callback_data="company:links")
    builder.button(text="🏅 Галерея партнёров", callback_data="company:partners")
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def products_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, item in content.PRODUCT_CATEGORIES.items():
        builder.button(text=item["title"], callback_data=f"products:category:{key}")
    builder.button(text="🎯 Рекомендуемые наборы", callback_data="products:sets")
    builder.button(text="🔎 Поиск по продукту/эффекту", callback_data="products:search")
    builder.button(text="🧪 Квиз подбора", callback_data="quiz:start")
    builder.button(text="🛍 Полный каталог и магазин", url=settings.fitline_shop_url)
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def product_category_menu(category_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for slug, product in content.PRODUCTS.items():
        if product["category"] == category_key:
            builder.button(text=f"• {product['name']}", callback_data=f"product:{slug}")
    builder.button(text="🔎 Поиск", callback_data="products:search")
    add_navigation(builder, back_to="menu:products")
    builder.adjust(1)
    return builder.as_markup()


def product_detail_menu(category_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Магазин", url=settings.fitline_shop_url)
    builder.button(text="💬 Консультант", callback_data="support:start")
    add_navigation(builder, back_to=f"products:category:{category_key}")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def product_search_results_menu(slugs: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for slug in slugs[:8]:
        product = content.PRODUCTS[slug]
        builder.button(text=product["name"], callback_data=f"product:{slug}")
    builder.button(text="🔎 Новый поиск", callback_data="products:search")
    add_navigation(builder, back_to="menu:products")
    builder.adjust(1)
    return builder.as_markup()


def business_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Как стать партнёром", callback_data="business:steps")
    builder.button(text="⭐ Преимущества", callback_data="business:advantages")
    builder.button(text="📊 Компенсационный план", callback_data="business:plan")
    builder.button(text="🌟 Истории партнёров", callback_data="business:stories")
    builder.button(text="✅ Присоединиться сейчас", url=settings.registration_url)
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def reviews_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Читать отзывы", callback_data="reviews:list")
    builder.button(text="🎥 Видео-отзывы", callback_data="reviews:videos")
    builder.button(text="🖼 Фото до/после", callback_data="reviews:before_after")
    builder.button(text="✍️ Оставить отзыв", callback_data="reviews:add")
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def order_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧭 Опросник-консультация", callback_data="consult:start")
    builder.button(text="⏰ Напомнить о повторном заказе", callback_data="order:reminder")
    builder.button(text="🛍 Открыть FitLine магазин", url=settings.fitline_shop_url)
    builder.button(text="💬 Помощь консультанта", callback_data="support:start")
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def consultation_goal_menu(prefix: str = "consult") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌱 Здоровье и база", callback_data=f"{prefix}:goal:health")
    builder.button(text="⚡ Спорт и энергия", callback_data=f"{prefix}:goal:sport")
    builder.button(text="⚖️ Контроль веса", callback_data=f"{prefix}:goal:weight")
    builder.button(text="💎 Красота", callback_data=f"{prefix}:goal:beauty")
    add_navigation(builder, back_to="menu:order" if prefix == "consult" else "menu:products")
    builder.adjust(1)
    return builder.as_markup()


def consultation_lifestyle_menu(prefix: str = "consult") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏃 Много движения/тренировки", callback_data=f"{prefix}:life:active")
    builder.button(text="💻 Офис и высокий темп", callback_data=f"{prefix}:life:office")
    builder.button(text="🌙 Нужна вечерняя рутина", callback_data=f"{prefix}:life:evening")
    builder.button(text="🧘 Мягкий старт без спешки", callback_data=f"{prefix}:life:soft")
    add_navigation(builder, back_to="menu:order" if prefix == "consult" else "menu:products")
    builder.adjust(1)
    return builder.as_markup()


def consultation_format_menu(prefix: str = "consult") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🥤 Напитки", callback_data=f"{prefix}:format:drinks")
    builder.button(text="📦 Готовый набор", callback_data=f"{prefix}:format:set")
    builder.button(text="💬 Сначала консультация", callback_data=f"{prefix}:format:consult")
    add_navigation(builder, back_to="menu:order" if prefix == "consult" else "menu:products")
    builder.adjust(1)
    return builder.as_markup()


def registration_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Инструкция", callback_data="registration:steps")
    builder.button(text="🎁 Стартовые пакеты", callback_data="registration:packages")
    builder.button(text="🔗 Открыть регистрацию", callback_data="registration:open")
    builder.button(text="💬 Помощь консультанта", callback_data="support:start")
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def registration_link_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Перейти к регистрации", url=settings.registration_url)
    builder.button(text="💬 Написать консультанту", callback_data="support:start")
    add_navigation(builder, back_to="menu:registration")
    builder.adjust(1)
    return builder.as_markup()


def faq_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, item in content.FAQ_ITEMS.items():
        builder.button(text=f"❔ {item['q']}", callback_data=f"faq:{key}")
    builder.button(text="📚 Библиотека", callback_data="library:open")
    builder.button(text="📬 Подписка на рассылку", callback_data="subscription:open")
    builder.button(text="💬 Связаться с консультантом", callback_data="support:start")
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def library_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for title, url in content.LIBRARY_ITEMS:
        builder.button(text=title, url=url)
    add_navigation(builder, back_to="menu:faq")
    builder.adjust(1)
    return builder.as_markup()


def subscription_menu(is_subscribed: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_subscribed:
        builder.button(text="🔕 Отписаться", callback_data="subscription:off")
    else:
        builder.button(text="✅ Подписаться", callback_data="subscription:on")
    add_navigation(builder, back_to="menu:faq")
    builder.adjust(1)
    return builder.as_markup()


def profile_menu(is_subscribed: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📬 Управлять рассылкой", callback_data="subscription:open")
    builder.button(text="⏰ Напоминание о заказе", callback_data="order:reminder")
    builder.button(text="💬 Консультант", callback_data="support:start")
    add_navigation(builder, back_to="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def back_main_menu(back_to: str = "nav:main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    add_navigation(builder, back_to=back_to)
    builder.adjust(1)
    return builder.as_markup()


def support_link_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Открыть Telegram консультанта", url=settings.consultant_url)
    add_navigation(builder, back_to="menu:faq")
    builder.adjust(1)
    return builder.as_markup()


def add_navigation(builder: InlineKeyboardBuilder, back_to: str | None = None) -> None:
    if back_to:
        builder.button(text="⬅️ Назад", callback_data=back_to)
    builder.button(text="🏠 Главное меню", callback_data="nav:main")
