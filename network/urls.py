
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/<str:profile_name>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("follow_unfollow/<str:profile_name>", views.follow_unfollow, name="follow_unfollow"),
    path("following", views.following, name="following"),
    path("edit", views.edit_post, name="edit"),
    path("like", views.like_unlike, name="like_unlike")
]
