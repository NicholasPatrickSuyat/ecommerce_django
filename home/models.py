from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos', blank=True, null=True)

    def __str__(self):
        return self.name

class CompanyVideo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=100)  # Ensure this field is present
    youtube_url = models.URLField()

    def __str__(self):
        return f"Video for {self.company.name}"
