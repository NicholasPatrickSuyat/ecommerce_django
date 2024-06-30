from django.contrib import admin
from django.utils.html import format_html
from .models import Products, ProductImage, ProductSize, ProductsPage, Section, Color

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_display')

    def color_display(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px;"></div>',
            obj.hex_code
        )
    color_display.short_description = 'Color'

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'section', 'display_colors')
    search_fields = ('title',)
    inlines = [ProductImageInline, ProductSizeInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'colors', 'comparison_chart_image', 'comparison_description', 'section')
        }),
    )

    def display_colors(self, obj):
        return format_html(', '.join(
            f'<div style="display:inline-block; width:15px; height:15px; background-color:{color.hex_code}; margin-right:2px;"></div>{color.name}'
            for color in obj.colors.all()
        ))
    display_colors.short_description = 'Colors'

@admin.register(ProductsPage)
class ProductsPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'quantity', 'total_price', 'shipping')
    search_fields = ('title', 'product__title')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(Color, ColorAdmin)
