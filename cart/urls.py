from django.urls import path
from .views import cart_view, add_to_cart, remove_from_cart, update_cart, checkout_view, guest_checkout_view, guest_checkout_success_view, payment_success, payment_cancel

app_name = 'cart'

urlpatterns = [
    path('', cart_view, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', update_cart, name='update_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('guest-checkout/', guest_checkout_view, name='guest_checkout'),
    path('guest-checkout/success/', guest_checkout_success_view, name='guest_checkout_success'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-cancel/', payment_cancel, name='payment_cancel'),
]
