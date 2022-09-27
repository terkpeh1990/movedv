# Generated by Django 3.2.6 on 2021-09-17 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0015_auto_20210916_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.CharField(max_length=250, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='historicalcustomer',
            name='id',
            field=models.CharField(db_index=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='historicalorder',
            name='id',
            field=models.CharField(db_index=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='id',
            field=models.CharField(db_index=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='id',
            field=models.CharField(max_length=250, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.CharField(max_length=250, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.CharField(max_length=250, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='pv',
            name='description',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='pv_details',
            name='description',
            field=models.CharField(max_length=250),
        ),
    ]