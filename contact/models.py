from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    phone_number = models.CharField(max_length=15)

    
    def __str__(self):
        return self.name


