"""message URL Configuration

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
from . import views
from django.urls import path

urlpatterns = [
    path("friends/", views.get_all_friends_sql),
    path("neighbors/", views.get_follow_neighbors_sql),
    # path("all_neighbors/", views.get_all_neighbors),
    path("get_friend_request/", views.get_friend_request_sql),
    path("add_friend/", views.add_friend_sql),
    path("accept_friend/", views.accept_friend_sql),
    path("reject_friend/", views.reject_friend_sql),
    path("follow_neighbor/", views.follow_neighbor_sql),
    # path("remove_friend/", views.remove_friend),
    # path("unfollow_neighbor/", views.unfollow_neighbor),
]
