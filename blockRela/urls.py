"""blockRela URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("blocks/", views.get_all_blocks),
    path("now_block/", views.now_block),
    path("all_follow_block/", views.all_follow_block),
    path("follow_block/", views.follow_block),
    path("apply_block/", views.apply_block),
    path("leave_block/", views.leave_block),
    path("get_block_requests/", views.get_block_requests),
    path("approve_block_request/", views.approve_block_request),
]
