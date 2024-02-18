from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_q.models import Schedule


class StartPrompt(models.Model):
    name = models.CharField(verbose_name="Название кнопки в главном меню",
                            help_text="Например, консультация фитнес-тренера", max_length=32)
    bot_answer = models.CharField(verbose_name="Ответ бота", max_length=4096)
    openai_prompt = models.CharField(verbose_name="Промпт к chatgpt", max_length=1028)

    class Meta:
        verbose_name = "Начальный промпт"
        verbose_name_plural = "Начальные промты"

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    created_at = models.DateTimeField(verbose_name="Присоединился", auto_now_add=True)
    telegram_id = models.BigIntegerField(verbose_name="ID телеграм")
    telegram_username = models.CharField(verbose_name="Username телеграм", max_length=64, null=True, blank=True)
    free_prompt_count = models.IntegerField(verbose_name="Бесплатных промптов сегодня", default=5)
    payment_method_id = models.CharField(verbose_name="Идентификатор для автоплатежа", max_length=1024, default="")
    message_history = ArrayField(
        models.JSONField(verbose_name="История промптов"),
        verbose_name="История промптов",
        default=list,
        blank=True
    )

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"

    def __str__(self):
        return f"@{self.telegram_username}" if self.telegram_username else f"ID: {self.telegram_id}"


class Subscription(models.Model):
    created_at = models.DateTimeField(verbose_name="Дата покупки", auto_now_add=True)
    days = models.IntegerField(verbose_name="Дней подписки")
    end_at = models.DateTimeField(verbose_name="Дата окончания")
    user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, verbose_name="Пользователь")
    expired = models.BooleanField(verbose_name="Истекла", default=False)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def save(self, *args, **kwargs):
        # If the object is being created (not updated)
        if not self.pk:
            Schedule.objects.create(func='main.tasks.renew_subscription', name='Автосписание за подписку',
                                    schedule_type=Schedule.ONCE,
                                    next_run=self.end_at,
                                    args=(self.user.pk,))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Подписка: {self.user}"
