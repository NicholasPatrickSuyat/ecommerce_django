from django.urls import path
from .views import training_view

app_name = 'training'

urlpatterns = [
    path('', training_view, name='training'),
]