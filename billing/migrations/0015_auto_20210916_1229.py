# Generated by Django 3.2.6 on 2021-09-16 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0014_auto_20210909_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='correction',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='correction',
            field=models.BooleanField(default=False),
        ),
    ]
