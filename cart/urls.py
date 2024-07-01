from django.urls import path
from .views import (
    cart_view, add_to_cart, remove_from_cart, update_cart, checkout_view, payment_done, 
    payment_cancelled, guest_checkout_view, payment_error, order_list_view, 
    order_detail_view, order_update_view, custom_permission_denied_view, order_delete_view, paypal_webhook, test_logging_view, test_invoice_creation
)
from django.conf.urls import handler403

app_name = 'cart'
handler403 = custom_permission_denied_view

urlpatterns = [
    path('', cart_view, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', update_cart, name='update_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('payment-success/', payment_done, name='payment_done'),
    path('payment-cancelled/', payment_cancelled, name='payment_cancelled'),
    path('guest-checkout/', guest_checkout_view, name='guest_checkout'),
    path('payment-error/', payment_error, name='payment_error'),
    path('orders/', order_list_view, name='order_list'),
    path('orders/<int:id>/', order_detail_view, name='order_detail'),
    path('orders/<int:id>/update/', order_update_view, name='order_update'),
    path('orders/<int:id>/delete/', order_delete_view, name='order_delete'),
    path('permission-denied/', custom_permission_denied_view, name='permission_denied'),
    path('paypal-webhook/', paypal_webhook, name='paypal_webhook'),
    path('test-logging/', test_logging_view, name='test_logging'),
    path('cart/test-invoice-creation/', test_invoice_creation, name='test_invoice_creation'),
    
    
]
