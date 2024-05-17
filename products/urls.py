from django.urls import path
from .views import products_page

app_name = 'products'

urlpatterns = [
    path('', products_page, name='products'),
]