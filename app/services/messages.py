from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def show_text(
    target: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    disable_web_page_preview: bool = True,
) -> None:
    if isinstance(target, CallbackQuery):
        if target.message is None:
            await target.answer()
            return
        try:
            await target.message.edit_text(
                text,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
            )
        except TelegramBadRequest:
            await target.message.answer(
                text,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
            )
        await target.answer()
        return

    await target.answer(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)


def product_text(product: dict) -> str:
    benefits = "\n".join(f"• {item}" for item in product["benefits"])
    return f"""
🧃 <b>{product['name']}</b>

{product['summary']}

<b>Преимущества формата:</b>
{benefits}

Важно: проверьте состав, способ применения и ограничения на этикетке. Продукт не является лекарственным средством.
""".strip()

