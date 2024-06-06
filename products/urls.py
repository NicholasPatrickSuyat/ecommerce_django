from django.urls import path
from .views import product_list, product_detail, add_to_cart, checkout

app_name = 'products'

urlpatterns = [
    path('', product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
]
