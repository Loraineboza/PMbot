from aiogram import Router
from aiogram.types import Message

from app import content
from app.keyboards import user as kb

router = Router()


@router.message()
async def keyword_autoreply(message: Message) -> None:
    text = (message.text or "").lower()

    if any(word in text for word in ["активиз", "активайз", "activize"]):
        await message.answer(
            "⚡ Activize Oxyplus — продукт для активного дня с витаминами группы B, витамином C и кофеином из гуараны.\n\n"
            "Откройте карточку продукта:",
            reply_markup=kb.product_search_results_menu(["activize"]),
        )
        return

    if any(word in text for word in ["каталог", "продукты", "магазин", "цена", "прайс"]):
        await message.answer(
            "🧃 Каталог FitLine можно посмотреть в боте по категориям или открыть официальный магазин.",
            reply_markup=kb.products_menu(),
        )
        return

    if any(word in text for word in ["скидка", "скидки", "акция", "клуб"]):
        await message.answer(
            "🏷 Актуальные скидки, клубные условия и акции зависят от страны и отображаются на официальной стороне FitLine/PM.\n\n"
            "Могу помочь найти подходящий стартовый вариант.",
            reply_markup=kb.registration_link_menu(),
        )
        return

    if any(word in text for word in ["регистрация", "зарегистрироваться", "партнер", "партнёр", "доход", "бизнес"]):
        await message.answer(content.REGISTRATION_MENU_TEXT, reply_markup=kb.registration_menu())
        return

    if any(word in text for word in ["консультант", "поддержка", "оператор", "вопрос"]):
        await message.answer(
            "💬 Можно отправить вопрос консультанту через бот или открыть прямой чат.",
            reply_markup=kb.support_link_menu(),
        )
        return

    if any(word in text for word in ["противопоказ", "врач", "лекар", "беремен", "детям"]):
        item = content.FAQ_ITEMS["contra"]
        await message.answer(f"❔ <b>{item['q']}</b>\n\n{item['a']}", reply_markup=kb.faq_menu())
        return

    await message.answer(
        "Я могу помочь с продуктами, заказом, регистрацией и консультацией. Выберите раздел в меню.",
        reply_markup=kb.main_menu(),
    )

