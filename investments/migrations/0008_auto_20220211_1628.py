# Generated by Django 3.0.7 on 2022-02-11 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0007_guiabolsotransaction_exclude_from_variable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guiabolsocategorybudget',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budget', to='investments.GuiaBolsoCategory'),
        ),
    ]
