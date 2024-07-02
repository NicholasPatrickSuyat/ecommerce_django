# Generated by Django 5.0.6 on 2024-07-02 20:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_remove_cart_sheen'),
        ('products', '0007_sheen_remove_products_colors_products_sheens_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='sheen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.sheen'),
        ),
    ]