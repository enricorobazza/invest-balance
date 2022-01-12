# Generated by Django 3.0.7 on 2022-01-12 02:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investments', '0019_auto_20220112_0215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guiabolsotoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guiabolso_token_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='GuiaBolsoTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('value', models.FloatField()),
                ('label', models.TextField()),
                ('description', models.TextField()),
                ('category', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guiabolso_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
