# Generated by Django 5.0.6 on 2024-06-07 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_remove_products_default_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productspage',
            name='total_price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True),
        ),
    ]