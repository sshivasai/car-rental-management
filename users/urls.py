

from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('register/', register_page, name='register_page'),
    path('api_register/', RegisterView.as_view(), name='api_register'),
    path('login/', login_page, name='login_page'),
    path('login-api/', LoginView.as_view(), name='login-api'),
    path('logout/', LogoutView.as_view(next_page='login_page'), name='logout'),
    path('profile/', profile_page, name='profile'),
    path('profile-api', ProfileView.as_view(), name='profile-api'),
    path('api/update-profile-picture/', update_profile_picture, name='update_profile_picture')
    
]
