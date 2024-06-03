from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Products(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='static/images/products/', blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

class ProductsPage(models.Model):
    title = models.CharField(max_length=100)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    shipping = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    order_image = models.ImageField(upload_to='static/images/products/', blank=True, null=True)
    buy_with_items = models.ManyToManyField(Products, related_name='bought_with', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

@receiver(post_save, sender=Products)
def create_product_page(sender, instance, created, **kwargs):
    if created:
        ProductsPage.objects.create(
            title=instance.title,
            product=instance,
            shipping='Default shipping information'
        )
