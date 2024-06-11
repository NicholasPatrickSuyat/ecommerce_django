from django.db import models
from django.conf import settings
from user.models import Order
from products.models import Products, ProductSize, ShippingOption

class DeliveryAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"

class DeliveryStatus(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order.id} - {self.get_status_display()}"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    guest_email = models.EmailField(null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)  # Ensure size is added
    quantity = models.PositiveIntegerField(default=1)
    shipping_option = models.ForeignKey(ShippingOption, on_delete=models.SET_NULL, null=True, blank=True)  # New field
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart {self.id} for {self.user.username}"
        else:
            return f"Cart {self.id} for guest {self.guest_email}"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
