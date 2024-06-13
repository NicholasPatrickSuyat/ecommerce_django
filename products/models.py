# products/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class ShippingOption(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Products(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    shipping_options = models.ManyToManyField(ShippingOption, related_name='products')
    comparison_chart_image = models.ImageField(upload_to='static/images/products/comparison_charts/', blank=True, null=True)
    comparison_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='static/images/products/')

    def __str__(self):
        return f"{self.product.title} Image"

class ProductSize(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size_image = models.ImageField(upload_to='static/images/products/sizes/', blank=True, null=True)

    def __str__(self):
        return f"{self.product.title} - {self.size}"

class ProductsPage(models.Model):
    title = models.CharField(max_length=100)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    shipping = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True)
    order_image = models.ImageField(upload_to='static/images/products/', blank=True, null=True)
    buy_with_items = models.ManyToManyField(Products, related_name='bought_with', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Use the first size's price for total_price if it exists
        first_size = self.product.sizes.first()
        if first_size:
            self.total_price = first_size.price * self.quantity
        super().save(*args, **kwargs)

@receiver(post_save, sender=Products)
def create_product_page(sender, instance, created, **kwargs):
    if created:
        first_size = instance.sizes.first()
        total_price = first_size.price if first_size else 0
        ProductsPage.objects.create(
            title=instance.title,
            product=instance,
            shipping='Default shipping information',
            total_price=total_price
        )
