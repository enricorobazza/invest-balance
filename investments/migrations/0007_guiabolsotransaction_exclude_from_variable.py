# Generated by Django 3.0.7 on 2022-01-21 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0006_auto_20220115_0156'),
    ]

    operations = [
        migrations.AddField(
            model_name='guiabolsotransaction',
            name='exclude_from_variable',
            field=models.BooleanField(default=False),
        ),
    ]