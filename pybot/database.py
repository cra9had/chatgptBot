import os
from datetime import datetime, timedelta

import django
from asgiref.sync import sync_to_async
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from main.models import StartPrompt, TelegramUser, Subscription


@sync_to_async
def get_start_prompts() -> list[StartPrompt]:
    prompts = StartPrompt.objects.all()
    return prompts


@sync_to_async
def get_start_prompt_by_id(prompt_id: int) -> StartPrompt:
    return StartPrompt.objects.get(
        id=prompt_id
    )


@sync_to_async
def create_user(telegram_id: int, username: str) -> None:
    if not TelegramUser.objects.filter(telegram_id=telegram_id).exists():
        TelegramUser.objects.create(
            telegram_id=telegram_id,
            telegram_username=username
        )


@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> TelegramUser:
    return _get_user_by_telegram_id(telegram_id)


def _get_user_by_telegram_id(telegram_id: int) -> TelegramUser:
    return TelegramUser.objects.get(telegram_id=telegram_id)


@sync_to_async
def check_if_user_subscribed(telegram_id: int) -> bool:
    user = _get_user_by_telegram_id(telegram_id)
    return Subscription.objects.filter(user=user).exists()


@sync_to_async
def spend_free_prompt(telegram_id: int) -> None:
    user = _get_user_by_telegram_id(telegram_id)
    user.free_prompt_count -= 1
    user.save()


@sync_to_async
def add_prompt_to_history(telegram_id: int, prompt: dict) -> None:
    user = _get_user_by_telegram_id(telegram_id)
    user.message_history.append(prompt)
    user.save()


@sync_to_async
def clear_prompt_history(telegram_id: int) -> None:
    user = _get_user_by_telegram_id(telegram_id)
    user.message_history = []
    user.save()


@sync_to_async
def create_new_subscription(telegram_id: int, days: int) -> None:
    user = _get_user_by_telegram_id(telegram_id)
    Subscription.objects.create(
        user=user,
        days=days,
        end_at=timezone.now() + timezone.timedelta(days=days)
    )


@sync_to_async
def add_payment_method_id(telegram_id: int, payment_method_id: str) -> None:
    user = _get_user_by_telegram_id(telegram_id)
    user.payment_method_id = payment_method_id
    user.save()
