from django.contrib import admin
from .models import StartPrompt, TelegramUser, Subscription


@admin.register(StartPrompt)
class StartPromptAdmin(admin.ModelAdmin):
    ...


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    ...


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    ...
