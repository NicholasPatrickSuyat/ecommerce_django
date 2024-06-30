from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Section(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name

class Products(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    comparison_chart_image = models.ImageField(upload_to='static/images/products/comparison_charts/', blank=True, null=True)
    comparison_description = models.TextField(blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    colors = models.ManyToManyField(Color, blank=True, related_name='products')  # Updated to many-to-many

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
