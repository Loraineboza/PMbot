from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import content
from app.database import db
from app.keyboards import user as kb
from app.services.messages import product_text, show_text
from app.services.recommendations import recommendation_by_answers
from app.services.search import search_products
from app.states import ConsultationFlow, ProductSearch

router = Router()


@router.callback_query(F.data == "menu:products")
async def products_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.PRODUCTS_MENU_TEXT, reply_markup=kb.products_menu())


@router.callback_query(F.data.startswith("products:category:"))
async def product_category(callback: CallbackQuery) -> None:
    category_key = callback.data.rsplit(":", 1)[-1]
    category = content.PRODUCT_CATEGORIES.get(category_key)
    if not category:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    text = f"{category['title']}\n\n{category['description']}\n\nВыберите продукт:"
    await show_text(callback, text, reply_markup=kb.product_category_menu(category_key))


@router.callback_query(F.data.startswith("product:"))
async def product_detail(callback: CallbackQuery) -> None:
    slug = callback.data.split(":", 1)[1]
    product = content.PRODUCTS.get(slug)
    if not product:
        await callback.answer("Продукт не найден.", show_alert=True)
        return

    text = product_text(product)
    markup = kb.product_detail_menu(product["category"])
    if product.get("photo_file_id") and callback.message:
        await callback.message.answer_photo(product["photo_file_id"], caption=text, reply_markup=markup)
        await callback.answer()
        return
    await show_text(callback, text, reply_markup=markup)


@router.callback_query(F.data == "products:sets")
async def recommended_sets(callback: CallbackQuery) -> None:
    await show_text(callback, content.RECOMMENDED_SETS_TEXT, reply_markup=kb.back_main_menu("menu:products"))


@router.callback_query(F.data == "products:search")
async def product_search_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProductSearch.waiting_query)
    await show_text(
        callback,
        "🔎 Напишите название продукта или эффект, который вас интересует.\n\nНапример: «активиз», «красота», «вес», «спорт», «омега».",
        reply_markup=kb.back_main_menu("menu:products"),
    )


@router.message(ProductSearch.waiting_query)
async def product_search_result(message: Message, state: FSMContext) -> None:
    query = (message.text or "").strip()
    if len(query) > 80:
        await message.answer("Слишком длинный запрос. Напишите 1–3 слова, например «спорт» или «контроль веса».")
        return

    results = search_products(query)
    await state.clear()
    if not results:
        await message.answer(
            "Ничего точного не нашёл. Попробуйте другое слово или откройте каталог.",
            reply_markup=kb.products_menu(),
        )
        return

    names = "\n".join(f"• {content.PRODUCTS[slug]['name']}" for slug in results)
    await message.answer(
        f"Нашёл варианты по запросу <b>{query}</b>:\n\n{names}",
        reply_markup=kb.product_search_results_menu(results),
    )


@router.callback_query(F.data == "quiz:start")
async def quiz_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ConsultationFlow.waiting_goal)
    await state.update_data(flow="quiz")
    await show_text(callback, content.QUIZ_INTRO_TEXT + "\n\n1/3. Какая цель сейчас главная?", reply_markup=kb.consultation_goal_menu("quiz"))


@router.callback_query(ConsultationFlow.waiting_goal, F.data.startswith("quiz:goal:"))
async def quiz_goal(callback: CallbackQuery, state: FSMContext) -> None:
    goal = callback.data.rsplit(":", 1)[-1]
    await state.update_data(goal=goal)
    await state.set_state(ConsultationFlow.waiting_lifestyle)
    await show_text(callback, "2/3. Какой у вас ритм жизни?", reply_markup=kb.consultation_lifestyle_menu("quiz"))


@router.callback_query(ConsultationFlow.waiting_lifestyle, F.data.startswith("quiz:life:"))
async def quiz_lifestyle(callback: CallbackQuery, state: FSMContext) -> None:
    lifestyle = callback.data.rsplit(":", 1)[-1]
    await state.update_data(lifestyle=lifestyle)
    await state.set_state(ConsultationFlow.waiting_format)
    await show_text(callback, "3/3. Какой формат вам ближе?", reply_markup=kb.consultation_format_menu("quiz"))


@router.callback_query(ConsultationFlow.waiting_format, F.data.startswith("quiz:format:"))
async def quiz_finish(callback: CallbackQuery, state: FSMContext) -> None:
    preferred_format = callback.data.rsplit(":", 1)[-1]
    data = await state.get_data()
    goal = data.get("goal", "health")
    lifestyle = data.get("lifestyle", "soft")
    text, slugs = recommendation_by_answers(goal, lifestyle, preferred_format)
    await db.save_quiz_result(callback.from_user.id, {"goal": goal, "lifestyle": lifestyle, "format": preferred_format}, text)
    await state.clear()
    await show_text(callback, text, reply_markup=kb.product_search_results_menu(slugs))

