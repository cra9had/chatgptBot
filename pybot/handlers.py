from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from pybot.keyboards import get_main_keyboard, subscription_keyboard, payment_keyboard, get_dialog_keyboard, cancel_auto_payments
from openai import AsyncOpenAI
import database
from pybot.utils import (process_dialog, get_subscription_payment,
                         get_subscription_price_by_days, check_subscription,)

router = Router()


@router.message(CommandStart())
@router.message(F.text == "💬 Новый диалог")
async def cmd_start(message: types.Message):
    await database.create_user(
        message.chat.id,
        message.chat.username
    )
    await message.answer("Привет! 👋 Я Саша, твой персональный помощник и друг!\nЧем могу помочь сегодня?",
                         reply_markup=await get_main_keyboard())


@router.callback_query(F.data.startswith("prompt_"))
async def start_dialog(call: types.CallbackQuery, state: FSMContext):
    prompt_id = int(call.data.replace("prompt_", ""))
    prompt = await database.get_start_prompt_by_id(prompt_id)
    await database.clear_prompt_history(call.message.chat.id)
    await call.answer()
    await call.message.answer(prompt.bot_answer, reply_markup=await get_dialog_keyboard())
    await state.set_data({
        "prompt_id": prompt_id
    })


@router.message(Command("subscribe"))
@router.message(F.text == "💎 Premium подписка")
async def subscription_handler(message: Message):
    await message.answer("""
Выбери подходящий тариф:\n\nПреимущества 💎 Premium подписки:\n🚀 Безлимитный доступ\n🧘 Неограниченное кол-во сеансов\n📱 Онлайн 24/7
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


@router.message(F.text == "👤 Личный кабинет")
async def dashboard(message: Message):
    user = await database.get_user_by_telegram_id(message.chat.id)
    subscription = await database.get_user_subscription(message.chat.id)
    kb = None
    if subscription and user.payment_method_id:
        kb = cancel_auto_payments()
    return await message.answer(f"""
🧑🏻‍💻 Личный кабинет

🆔 Ваш ID: {message.chat.id}
📅 Дата регистрации: {user.created_at.strftime("%d %B %Y г")}
💎 Premium статус: {'нет' if not subscription else subscription.end_at.strftime("до %d %B %Y г")}
""", reply_markup=kb)


@router.callback_query(F.data == "cancel_auto_payment")
async def cancel_auto_payment(call: CallbackQuery):
    user = await database.get_user_by_telegram_id(message.chat.id)
    user.payment_method_id = None
    user.save()
    await call.message.delete()
    await call.message.answer("Автосписание отключено")


@router.message(F.text == "🆘 Поддержка")
async def support(message: Message):
    await message.answer("✅ Основные положения:\nЧат-бот Саша предоставляет возможность общения с искусственным интеллектом на основе модели ChatGPT.\nКаждый пользователь имеет право на несколько бесплатных запросов к боту в сутки.\nДля неограниченного использования бота рекомендуем оформить Премиум-статус.\n\n✅ Платная Подписка:\nДля продолжения использования бота после исчерпания бесплатных запросов, пользователю необходимо приобрести Премиум-подписку.\nПриобретение подписки дает право на неограниченное количество запросов к боту в течение периода действия подписки.\n\n✅ Оплата:\nОплата платной подписки производится согласно тарифам и условиям, указанным на странице оплаты.\nПосле успешной оплаты подписки пользователь получает доступ к дополнительным функциям бота.\n\n✅ Отказ от ответственности:\nАдминистрация бота не несет ответственности за содержание и результаты коммуникации с ботом.\n\n✅ Конфиденциальность:\nБот не собирает и не хранит персональные данные пользователей.\nКоммуникация с ботом является конфиденциальной.\n\n✅ Изменения и Дополнения:\nАдминистрация оставляет за собой право вносить изменения и дополнения в эти правила без предварительного уведомления пользователей.\n\n✅ Контакты:\nДля связи с администрацией бота или в случае возникновения вопросов по использованию бота: @Sasha_supp.")


@router.message()
async def dialog(message: Message, state: FSMContext, bot: Bot, openai: AsyncOpenAI):
    prompt_id = (await state.get_data())["prompt_id"]
    return await process_dialog(message, prompt_id, openai, bot)
