from django.urls import path
from .views import user_view

app_name = 'user'

urlpatterns = [
    path('', user_view, name='user'),
]