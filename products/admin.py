from django.contrib import admin
from .models import Products, ProductsPage

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'description')
    search_fields = ('title',)

@admin.register(ProductsPage)
class ProductPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'quantity', 'total_price', 'shipping')
    search_fields = ('title', 'product__title')
    readonly_fields = ('total_price',)
