from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('hello/', views.get_message),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('', views.home, name='home'),
]
