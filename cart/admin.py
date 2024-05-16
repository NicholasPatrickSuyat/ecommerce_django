from django.contrib import admin
from .models import Cart, PaymentMethod

admin.site.register(Cart)
admin.site.register(PaymentMethod)