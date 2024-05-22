from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)  # New phone number field
    message = models.TextField()

    def __str__(self):
        return self.name
