# Generated by Django 3.0.7 on 2020-06-24 17:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investments', '0010_saving_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfer',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transfer_user', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
