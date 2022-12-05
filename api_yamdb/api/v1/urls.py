from django.urls import path

from .views import token, signup

auth_url_pattern_list = [
    path('token/', token, name='token'),
    path('signup/', signup, name='signup'),
]
