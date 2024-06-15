from django.contrib import admin
from .models import CustomUser, UserProfile, Order, OrderItem

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj and not hasattr(obj, 'profile'):
            UserProfile.objects.create(user=obj)
        return obj

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shipping_address')
    search_fields = ('user__username', 'user__email')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ordered_date', 'order_date', 'shipping_address', 'total_cost')
    search_fields = ('user__username', 'user__email', 'items__product__title', 'items__size__size')
    list_filter = ('ordered_date',)
    inlines = [OrderItemInline]

    def total_cost(self, obj):
        return obj.total_cost()

    total_cost.short_description = 'Total Cost'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'size', 'quantity', 'total_cost')
    search_fields = ('order__user__username', 'product__title', 'size__size')

    def total_cost(self, obj):
        return obj.total_cost()

    total_cost.short_description = 'Total Cost'
