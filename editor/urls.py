from django.urls import path

from . import views

app_name = "editor"
urlpatterns = [
    path("", views.PostIndexView.as_view(), name="index"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.logout, name="logout"),

    # Post section
    path("post/", views.PostIndexView.as_view(), name="post.list"),
    path("post/create/", views.PostCreateView.as_view(), name="post.create"),
    path("post/update/<slug:slug>/", views.PostUpdateView.as_view(), name="post.update"),
    path("post/view/<slug:slug>/", views.PostView.as_view(), name="post.view"),
    path("post/delete/<slug:slug>/", views.PostDeleteView.as_view(), name="post.delete"),

    # Comment section
    path("post/view/<slug:slug>/comment/create/", views.CommentCreate.as_view(), name="comment.create"),
    path("post/view/<slug:slug>/comment/delete/<int:pk>/", views.CommentDelete.as_view(), name="comment.delete"),

    # User section
    path("user/profile/", views.UserProfileView.as_view(), name="user.profile"),
]