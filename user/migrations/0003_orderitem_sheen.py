# Generated by Django 5.0.6 on 2024-06-30 06:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_sheen_remove_products_colors_products_sheens_and_more'),
        ('user', '0002_order_ordered_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='sheen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.sheen'),
        ),
    ]
