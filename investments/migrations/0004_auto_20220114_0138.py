# Generated by Django 3.0.7 on 2022-01-14 04:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investments', '0003_guiabolsotransaction_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guiabolsotoken',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.expressions.Case, related_name='guiabolso_token_user', to=settings.AUTH_USER_MODEL),
        ),
    ]