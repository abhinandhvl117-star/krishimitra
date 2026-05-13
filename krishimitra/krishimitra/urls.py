"""
URL configuration for krishimitra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    
    # farmer
    path('crop/', views.crop_view, name='crop'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('disease/', views.disease_view, name='disease'),
    path('price/', views.price_view, name='price'),
    path('weather/', views.weather_view, name='weather'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chatbot/ask/', views.chatbot_ask_view, name='chatbot_ask'),
    
    # admin
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/users/<int:user_id>/', views.admin_user_detail_view, name='admin_user_detail'),
    path('admin-panel/crops/', views.admin_crops_view, name='admin_crops'),
    path('admin-panel/diseases/', views.admin_diseases_view, name='admin_diseases'),
    path('admin-panel/prices/', views.admin_prices_view, name='admin_prices'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)