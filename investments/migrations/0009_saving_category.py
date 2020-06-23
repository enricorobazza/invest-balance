# Generated by Django 3.0.7 on 2020-06-23 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0008_assetpurchase_taxes_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='saving',
            name='category',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.PROTECT, related_name='saving_category', to='investments.Category'),
            preserve_default=False,
        ),
    ]