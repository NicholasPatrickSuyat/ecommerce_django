from django.urls import path
from .views import home_view, learn_more_1

app_name = 'home'

urlpatterns = [
    path('', home_view, name='home'),
    path('learn_1/', learn_more_1, name='learn-more-1'),
    path('learn_2/', learn_more_1, name='learn-more-2'),
    path('learn_3/', learn_more_1, name='learn-more-3'),
    path('learn_4/', learn_more_1, name='learn-more-4'),
]