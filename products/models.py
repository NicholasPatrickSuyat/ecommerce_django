from django.db import models

class Products(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
    desciption = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

class ProductPage(models.Model):
    title = models.CharField(max_length=100)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    shipping = models.TextField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    order_image = models.ImageField(upload_to='order_images', blank=True, null=True)

# Add similar items inside and "buy with items"