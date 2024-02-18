# Generated by Django 5.0.2 on 2024-02-17 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StartPrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Например, консультация фитнес-тренера', max_length=32, verbose_name='Название кнопки в главном меню')),
                ('bot_answer', models.CharField(max_length=4096, verbose_name='Ответ бота')),
                ('openai_prompt', models.CharField(max_length=1028, verbose_name='Промпт к chatgpt')),
            ],
            options={
                'verbose_name': 'Начальный промпт',
                'verbose_name_plural': 'Начальные промты',
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(verbose_name='ID телеграм')),
                ('telegram_username', models.CharField(blank=True, max_length=64, null=True, verbose_name='Username телеграм')),
                ('free_prompt_count', models.IntegerField(default=5, verbose_name='Бесплатных промптов сегодня')),
            ],
            options={
                'verbose_name': 'Пользователь бота',
                'verbose_name_plural': 'Пользователи бота',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='Дата покупки')),
                ('end_at', models.DateTimeField(verbose_name='Дата окончания')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.telegramuser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
    ]
