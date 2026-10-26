from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegistrationSerializer, CropRecommendationSerializer
from rest_framework.permissions import AllowAny
import requests
from django.conf import settings

FASTAPI_URL = getattr(settings, 'FASTAPI_URL')
class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile = getattr(user, "profile", None)
        
        if profile and not profile.is_active_account:
            raise serializers.ValidationError("user profile has been disabled")
        
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'is_staff': user.is_staff
        }
        
        return data
    
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    
class MeView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'email': user.email,
            'place': user.profile.city if hasattr(user, 'profile') else None,
            'is_staff': user.is_staff
        })
        
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {'message': 'The registration was successful'},
            status=status.HTTP_201_CREATED
        )
        
class CropRecommendationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CropRecommendationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        payload = {
            "N": data['nitrogen'],
            "P": data['phosphorus'],
            "K": data['potassium'],
            "temperature": data['temperature'],
            "humidity": data['humidity'],
            "ph": data['ph'],
            "rainfall": data['rainfall']    
        }
        resp = requests.post(f"{FASTAPI_URL}/crop", json=payload, timeout=15)
        resp.raise_for_status()
        api_result = resp.json()
        print(api_result)
        # data = serializer.save()
        
        
        return Response(
            {'message': 'Successfully received the values'},
            status=status.HTTP_202_ACCEPTED
        )