import asyncio
from typing import Optional
from yookassa import Payment
from aiogram.methods import SendMessage
from openai import AsyncOpenAI
from aiogram import types
from aiogram import Bot
from yookassa.domain.response import PaymentResponse
from pybot import keyboards
from pybot import database
from main.models import TelegramUser


TARIFFS = {
    1: 50,
    7: 150,
    30: 390
}


async def get_first_prompt(message: types.Message, prompt_id: int):
    start_prompt = await database.get_start_prompt_by_id(prompt_id)
    return f"{start_prompt}\n{message.text}"


async def can_continue_dialog(telegram_id: int) -> bool:
    """Проверяет есть ли подписка у юзера или остались ли у него бесплатные промпты на сегодня"""
    user = await database.get_user_by_telegram_id(telegram_id)
    is_subscribed = await database.check_if_user_subscribed(telegram_id)
    if is_subscribed or user.free_prompt_count > 0:
        return True
    return False


async def get_history_prompts(user: TelegramUser, message: types.Message) -> list[dict]:
    prompts = [*user.message_history, {"role": "user", "content": message.text}]
    return prompts


async def get_prompt(user: TelegramUser, message: types.Message, prompt_id: int):
    if not user.message_history:
        prompt = [{"role": "user",
                   "content": await get_first_prompt(message, prompt_id)}]
    else:
        prompt = await get_history_prompts(user, message)
    return prompt


async def process_dialog(message: types.Message, prompt_id: int, openai: AsyncOpenAI, bot: Bot) -> Optional[SendMessage]:
    if not await can_continue_dialog(message.chat.id):
        return message.answer("""
К сожалению, бесплатные промпты на сегодня закончились.        
Подожди до завтра, либо купи подписку
""", reply_markup=await keyboards.not_enough_trial_prompts())
    user = await database.get_user_by_telegram_id(message.chat.id)
    if not await database.check_if_user_subscribed(message.chat.id):
        await database.spend_free_prompt(message.chat.id)
    prompt = await get_prompt(user, message, prompt_id)
    await database.add_prompt_to_history(message.chat.id, {'role': 'user', 'content': message.text})
    asyncio.create_task(answer_task(openai, prompt, message, bot))


async def answer_task(openai: AsyncOpenAI, prompt: list[dict], message: types.Message, bot: Bot) -> None:
    stream = await openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=prompt,
        stream=True,
    )
    message_id = None
    output = ""
    next_print = 50
    async for chunk in stream:
        new_content = chunk.choices[0].delta.content
        if not new_content: continue
        output += new_content
        if not output or len(output) < next_print: continue
        next_print += 50
        if not message_id:
            msg = await bot.send_message(text=output, chat_id=message.chat.id)
            message_id = msg.message_id
        else:
            await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text=output)
    if not message_id:
        await bot.send_message(text=output, chat_id=message.chat.id)
    else:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text=output)
    await database.add_prompt_to_history(message.chat.id, {'role': 'system', 'content': output})


async def get_subscription_payment(days: int) -> PaymentResponse:
    payment = Payment.create({
        "amount": {
            "value": f"{TARIFFS[days]}.00",
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": f"Подписка на {days} дней",
        "save_payment_method": True
    })
    return payment


async def check_subscription(telegram_id: int, payment_id: str) -> bool:
    payment = Payment.find_one(payment_id)
    days = await get_subscription_days_by_price(round(float(payment.amount.value)))
    if payment.paid:
        await database.create_new_subscription(telegram_id=telegram_id, days=days)
        await database.add_payment_method_id(telegram_id=telegram_id, payment_method_id=payment.payment_method.id)
    return payment.paid


async def get_subscription_days_by_price(price: int) -> int:
    for key, val in TARIFFS.items():
        if val == price:
            return key


async def get_subscription_price_by_days(days: int) -> int:
    return TARIFFS[days]
