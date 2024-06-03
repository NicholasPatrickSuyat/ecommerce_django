from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Products, ProductsPage

@receiver(post_save, sender=Products)
def create_product_page(sender, instance, created, **kwargs):
    if created:
        ProductsPage.objects.create(
            title=instance.title,
            product=instance,
            shipping='Default shipping information'
        )
