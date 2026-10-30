from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    LoginView, 
    MeView, 
    RegisterView, 
    CropRecommendationView,
    PriceOptionView,
    PricePredictionView
)

urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/refreash/", TokenRefreshView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/register/", RegisterView.as_view()),
    path("crop/", CropRecommendationView.as_view()),
    path("price/options/", PriceOptionView.as_view()),
    path("price/", PricePredictionView.as_view()),
]