from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('set_csrf_token/', views.set_csrf_token, name='set_csrf_token'),
    path('', views.home, name='home'),
    path('is_logged_in/', views.is_logged_in, name='is_logged_in'),
]
