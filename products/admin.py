from django.contrib import admin
from .models import Products, ProductsPage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')
    search_fields = ('title',)

class ProductPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'quantity', 'total_price')
    search_fields = ('title', 'product__title')
    readonly_fields = ('total_price',)

admin.site.register(Products, ProductAdmin)
admin.site.register(ProductsPage, ProductPageAdmin)