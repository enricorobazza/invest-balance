# Generated by Django 3.0.7 on 2020-06-23 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0007_auto_20200623_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetpurchase',
            name='taxes_value',
            field=models.FloatField(default=0),
        ),
    ]
