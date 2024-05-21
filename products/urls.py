from django.urls import path
from .views import product_list, add_to_cart, checkout

app_name = 'products'

urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
]