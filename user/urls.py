from django.urls import path
from .views import profile, register, login_view, logout_view, order_history

app_name = 'user'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('order-history/', order_history, name='order_history'),
]
