# Generated by Django 5.0.6 on 2024-06-15 06:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('youtube_url', models.URLField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='home.company')),
            ],
        ),
    ]
