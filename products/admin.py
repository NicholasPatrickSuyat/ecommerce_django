from django.contrib import admin
from .models import Products, ProductImage, ProductSize, ProductsPage, Section, Sheen

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class SheenAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'section', 'display_sheens')
    search_fields = ('title',)
    inlines = [ProductImageInline, ProductSizeInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'sheens', 'comparison_chart_image', 'comparison_description', 'section')
        }),
    )

    def display_sheens(self, obj):
        return ', '.join(sheen.name for sheen in obj.sheens.all())
    display_sheens.short_description = 'Sheens'

@admin.register(ProductsPage)
class ProductsPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'quantity', 'total_price', 'shipping')
    search_fields = ('title', 'product__title')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(Sheen, SheenAdmin)
