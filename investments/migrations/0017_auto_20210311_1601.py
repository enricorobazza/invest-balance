# Generated by Django 3.1.7 on 2021-03-11 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0016_asset_can_invest'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='invest_type',
            field=models.CharField(choices=[('S', 'Ação'), ('F', 'Fundo')], default='S', max_length=1, verbose_name='Tipo de Investimento'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='can_invest',
            field=models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=True, verbose_name='Can be Invested?'),
        ),
    ]
