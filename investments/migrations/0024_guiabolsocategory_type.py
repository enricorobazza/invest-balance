# Generated by Django 3.0.7 on 2022-01-13 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0023_auto_20220113_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='guiabolsocategory',
            name='type',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
