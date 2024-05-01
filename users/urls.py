from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.get_message),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.home, name='home'),
]
