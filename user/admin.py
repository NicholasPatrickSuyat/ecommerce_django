from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Order

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'shipping_address', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'shipping_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'shipping_address')
    search_fields = ('user__username', 'bio')

admin.site.register(UserProfile, UserProfileAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'guest_email', 'product', 'quantity', 'total_cost', 'order_date')
    search_fields = ('user__username', 'guest_email', 'product__title')

admin.site.register(Order, OrderAdmin)