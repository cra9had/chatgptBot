# Generated by Django 4.2.10 on 2024-02-18 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_subscription_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='payment_method_id',
            field=models.CharField(default='', max_length=1024, verbose_name='Идентификатор для автоплатежа'),
        ),
    ]