from django.urls import path
from .views import home_view, learn_more_1, learn_more_2, learn_more_3, learn_more_4, about, terms, privacy, patents, warranty, search, search_recommendations, user_manuals, faq_view, order_status_view

app_name = 'home'

urlpatterns = [
    path('', home_view, name='home'),
    path('learn_1/', learn_more_1, name='learn-more-1'),
    path('learn_2/', learn_more_2, name='learn-more-2'),
    path('learn_3/', learn_more_3, name='learn-more-3'),
    path('learn_4/', learn_more_4, name='learn-more-4'),
    path('about/', about, name='about'),
    path('terms/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('patents/', patents, name='patents'),
    path('warranty/', warranty, name='warranty'),
    path('search/', search, name='search'),
    path('search/recommendations/', search_recommendations, name='search_recommendations'),
    path('user-manuals/', user_manuals, name='user_manuals'),
    path('faqs/', faq_view, name='faqs'),
    path('order_status/', order_status_view, name='order_status'),

]
