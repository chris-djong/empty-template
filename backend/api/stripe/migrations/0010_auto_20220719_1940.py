# Generated by Django 3.1.7 on 2022-07-19 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0009_auto_20220719_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripesubscription',
            name='stripe_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
