# Generated by Django 3.1.7 on 2022-01-12 14:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0004_auto_20220112_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripesubscription',
            name='expires',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
