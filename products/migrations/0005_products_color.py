# Generated by Django 5.0.6 on 2024-06-30 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_products_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]