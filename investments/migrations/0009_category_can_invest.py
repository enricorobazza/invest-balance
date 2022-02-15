# Generated by Django 3.0.7 on 2022-02-15 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0008_auto_20220211_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='can_invest',
            field=models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=True, verbose_name='Can be Invested?'),
        ),
    ]
