from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from pybot.keyboards import get_main_keyboard, subscription_keyboard, payment_keyboard
from openai import AsyncOpenAI
import database
from pybot.utils import (process_dialog, get_subscription_payment,
                         get_subscription_price_by_days, check_subscription)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await database.create_user(
        message.chat.id,
        message.chat.username
    )
    await message.answer("И так, давай выберем, что нам интересно на данный момент:",
                         reply_markup=await get_main_keyboard())


@router.callback_query(F.data.startswith("prompt_"))
async def start_dialog(call: types.CallbackQuery, state: FSMContext):
    prompt_id = int(call.data.replace("prompt_", ""))
    prompt = await database.get_start_prompt_by_id(prompt_id)
    await database.clear_prompt_history(call.message.chat.id)
    await call.answer()
    await call.message.answer(prompt.bot_answer)
    await state.set_data({
        "prompt_id": prompt_id
    })


@router.message(Command("subscribe"))
async def subscription_handler(message: Message):
    await message.answer("""
Выбери подходящий тариф:
""", reply_markup=await subscription_keyboard())


@router.callback_query(F.data.startswith("subscription/"))
async def subscription_payment_details(call: CallbackQuery):
    days = int(call.data.replace("subscription/", ""))
    payment = await get_subscription_payment(days)
    await call.message.delete()
    await call.message.answer(
        f"""Вы выбрали подписку на {days} дней
Сумма к оплате: {await get_subscription_price_by_days(days)}₽""",
        reply_markup=await payment_keyboard(payment.id, payment.confirmation.confirmation_url))


@router.callback_query(F.data == "back_to_subscriptions")
async def back_to_subscriptions(call: CallbackQuery):
    await call.message.delete()
    await subscription_handler(call.message)


@router.callback_query(F.data.startswith("paid/"))
async def check_is_paid(call: CallbackQuery):
    payment_id = call.data.replace("paid/", "")
    if await check_subscription(telegram_id=call.message.chat.id, payment_id=payment_id):
        await call.message.delete()
        await call.message.answer("Подписка успешно куплена")
    else:
        await call.answer("Сначала оплати подписку")


@router.message()
async def dialog(message: Message, state: FSMContext, bot: Bot, openai: AsyncOpenAI):
    prompt_id = (await state.get_data())["prompt_id"]
    return await process_dialog(message, prompt_id, openai, bot)
