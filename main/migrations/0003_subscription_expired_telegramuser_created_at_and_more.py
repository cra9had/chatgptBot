# Generated by Django 5.0.2 on 2024-02-17 19:39

import django.contrib.postgres.fields
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_telegramuser_message_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='expired',
            field=models.BooleanField(default=False, verbose_name='Истекла'),
        ),
        migrations.AddField(
            model_name='telegramuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Присоединился'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subscription',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата покупки'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='message_history',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=4096, verbose_name='История промптов'), default=list, size=None, verbose_name='История промптов'),
        ),
    ]
