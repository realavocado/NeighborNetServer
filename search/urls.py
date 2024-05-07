from django.urls import path
from . import views

urlpatterns = [
    path('search_keyword/', views.get_message_with_keyword)
]
