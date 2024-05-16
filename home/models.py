from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos', blank=True, null=True)


class CompanyVideo(models.Model):
    youtube_url = models.URLField()

