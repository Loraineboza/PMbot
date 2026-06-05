from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import content
from app.keyboards import user as kb
from app.services.messages import show_text

router = Router()


@router.callback_query(F.data == "menu:business")
async def business_menu(callback: CallbackQuery) -> None:
    await show_text(callback, content.BUSINESS_MENU_TEXT, reply_markup=kb.business_menu())


@router.callback_query(F.data == "business:steps")
async def business_steps(callback: CallbackQuery) -> None:
    await show_text(callback, content.BUSINESS_STEPS_TEXT, reply_markup=kb.back_main_menu("menu:business"))


@router.callback_query(F.data == "business:advantages")
async def business_advantages(callback: CallbackQuery) -> None:
    await show_text(callback, content.BUSINESS_ADVANTAGES_TEXT, reply_markup=kb.back_main_menu("menu:business"))


@router.callback_query(F.data == "business:plan")
async def business_plan(callback: CallbackQuery) -> None:
    await show_text(callback, content.BUSINESS_PLAN_TEXT, reply_markup=kb.registration_link_menu())


@router.callback_query(F.data == "business:stories")
async def business_stories(callback: CallbackQuery) -> None:
    await show_text(callback, content.BUSINESS_STORIES_TEXT, reply_markup=kb.back_main_menu("menu:business"))

