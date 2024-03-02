from django.urls import path

from . import views

app_name = "editor"
urlpatterns = [
    path("", views.PostIndexView.as_view(), name="index"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.logout, name="logout"),

    # Post section
    # path("post/create/", views.Post.create, name="post.create"),
    path("post/<slug:slug>/", views.PostView.as_view(), name="post.view"),

    # User section
    path("user/profile/", views.UserProfileView.as_view(), name="user.profile"),
]