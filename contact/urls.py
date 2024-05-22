from django.urls import path
from .views import contact_view, contact_success

app_name = 'contact'

urlpatterns = [
    path('', contact_view, name='contact'),
    path('success/', contact_success, name='contact_success'),
]