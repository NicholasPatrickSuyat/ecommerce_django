from django.urls import path
from .views import cart_view, add_to_cart, remove_from_cart, update_cart, checkout_view, payment_done, payment_canceled, guest_checkout_success_view, payment_error

app_name = 'cart'

urlpatterns = [
    path('', cart_view, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', update_cart, name='update_cart'),
    path('checkout/', checkout_view, name='checkout'),
    # path('process-payment/', process_payment, name='process_payment'),
    path('payment-success/', payment_done, name='payment_done'),
    path('payment-cancelled/', payment_canceled, name='payment_canceled'),
    path('guest-checkout/success/', guest_checkout_success_view, name='guest_checkout_success'),
    path('payment-error/', payment_error, name='payment_error'),
]
