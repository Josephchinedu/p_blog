from django.urls import path

from main.views import BlogPostApiView, BlogPostImageView, LoginView, RegisterView

ACCOUNT_URLS = [
    path("account/register/", RegisterView.as_view()),
    path("account/login/", LoginView.as_view()),
]

BLOG_URLS = [
    path("blog/", BlogPostApiView.as_view()),
    path("upload_image/", BlogPostImageView.as_view()),
]

urlpatterns = [
    *ACCOUNT_URLS,
    *BLOG_URLS,
]
