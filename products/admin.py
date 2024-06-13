# products/admin.py

from django.contrib import admin
from .models import Products, ProductImage, ProductSize, ProductsPage, ShippingOption

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)
    inlines = [ProductImageInline, ProductSizeInline]
    filter_horizontal = ('shipping_options',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'shipping_options', 'comparison_chart_image', 'comparison_description')
        }),
    )

@admin.register(ShippingOption)
class ShippingOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')

@admin.register(ProductsPage)
class ProductsPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'quantity', 'total_price', 'shipping')
    search_fields = ('title', 'product__title')
