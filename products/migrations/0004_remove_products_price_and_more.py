# Generated by Django 5.0.6 on 2024-06-16 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_products_comparison_chart_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='price',
        ),
        migrations.AlterField(
            model_name='products',
            name='comparison_chart_image',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/products/comparison_charts/'),
        ),
        migrations.AlterField(
            model_name='products',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
