from datetime import datetime, timedelta

import yookassa
from django_q.models import Schedule

from .models import TelegramUser, Subscription
from django.utils import timezone
from pybot.utils import TARIFFS
from yookassa import Payment


def renew_subscription(user_id: int):
    today_date = timezone.now().date()
    subscription = Subscription.objects.filter(user__pk=user_id, end_at__date=today_date).first()
    if not subscription:
        return
    subscription.expired = True
    subscription.save()
    user = TelegramUser.objects.get(pk=user_id)
    if user.payment_method_id:
        yookassa.Configuration.configure(account_id="335627",
                                         secret_key="test_pUPQfB_8TMktgDuw_xtbkWtwmxV_SpT2_ylO-t6YEJQ")
        payment = Payment.create({
            "amount": {
                "value": f"{TARIFFS[subscription.days]}.00",
                "currency": "RUB"
            },
            "capture": True,
            "payment_method_id": user.payment_method_id,
            "description": f"Подписка на {subscription.days} дней"
        })
        Schedule.objects.create(func='main.tasks.check_payment', name='Автосписание за подписку',
                                schedule_type=Schedule.ONCE,
                                next_run=timezone.now() + timezone.timedelta(minutes=1),
                                args=(payment.id, user_id))


def check_payment(payment_id: str, user_pk: int):
    yookassa.Configuration.configure(account_id="335627",
                                     secret_key="test_pUPQfB_8TMktgDuw_xtbkWtwmxV_SpT2_ylO-t6YEJQ")
    payment = Payment.find_one(payment_id)
    days = get_subscription_days_by_price(round(float(payment.amount.value)))
    if payment.paid:
        Subscription.objects.create(
            days=days,
            user=TelegramUser.objects.get(pk=user_pk),
            end_at=timezone.now() + timezone.timedelta(days=days)
        )


def get_subscription_days_by_price(price: int) -> int:
    for key, val in TARIFFS.items():
        if val == price:
            return key


def renew_free_prompt():
    for user in TelegramUser.objects.all():
        user.free_prompt_count = 2
        user.save()

