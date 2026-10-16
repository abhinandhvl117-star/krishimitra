from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import LoginSerializer, LoginView, MeView, RegisterView

urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/refreash/", TokenRefreshView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/register/", RegisterView.as_view())
]