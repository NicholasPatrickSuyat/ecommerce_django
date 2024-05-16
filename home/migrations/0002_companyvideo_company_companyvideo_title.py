# Generated by Django 5.0.6 on 2024-05-16 22:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyvideo',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='home.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companyvideo',
            name='title',
            field=models.CharField(default='Default Title', max_length=100),
            preserve_default=False,
        ),
    ]
