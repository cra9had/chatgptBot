# Generated by Django 4.2.10 on 2024-02-18 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_telegramuser_message_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='days',
            field=models.IntegerField(default=7, verbose_name='Дней подписки'),
            preserve_default=False,
        ),
    ]