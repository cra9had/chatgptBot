from pybot.database import get_start_prompts
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_main_keyboard() -> InlineKeyboardMarkup:
    prompts = await get_start_prompts()
    buttons = []
    for prompt in prompts:
        buttons.append([InlineKeyboardButton(text=prompt.name, callback_data=f"prompt_{prompt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def not_enough_trial_prompts() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Оформить подписку", callback_data="back_to_subscriptions")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def subscription_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="1 день - 50₽", callback_data='subscription/1')],
         [InlineKeyboardButton(text="7 дней - 150₽", callback_data='subscription/7')],
        [InlineKeyboardButton(text="30 дней - 390₽", callback_data='subscription/30')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def payment_keyboard(payment_id: str, payment_url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="✅Я оплатил", callback_data='paid/' + payment_id),
         InlineKeyboardButton(text="Назад", callback_data='back_to_subscriptions')],
        [InlineKeyboardButton(text="Оплатить", url=payment_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
