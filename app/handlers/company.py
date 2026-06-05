from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import content
from app.keyboards import user as kb
from app.services.messages import show_text

router = Router()


@router.callback_query(F.data == "menu:company")
async def company_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.COMPANY_MENU_TEXT, reply_markup=kb.company_menu())


@router.callback_query(F.data == "company:history")
async def company_history(callback: CallbackQuery) -> None:
    await show_text(callback, content.COMPANY_HISTORY_TEXT, reply_markup=kb.back_main_menu("menu:company"))


@router.callback_query(F.data == "company:facts")
async def company_facts(callback: CallbackQuery) -> None:
    await show_text(callback, content.COMPANY_FACTS_TEXT, reply_markup=kb.back_main_menu("menu:company"))


@router.callback_query(F.data == "company:philosophy")
async def company_philosophy(callback: CallbackQuery) -> None:
    await show_text(callback, content.COMPANY_PHILOSOPHY_TEXT, reply_markup=kb.back_main_menu("menu:company"))


@router.callback_query(F.data == "company:links")
async def company_links(callback: CallbackQuery) -> None:
    await show_text(callback, content.COMPANY_LINKS_TEXT, reply_markup=kb.back_main_menu("menu:company"))


@router.callback_query(F.data == "company:partners")
async def company_partners(callback: CallbackQuery) -> None:
    await show_text(callback, content.COMPANY_PARTNERS_TEXT, reply_markup=kb.back_main_menu("menu:company"))

