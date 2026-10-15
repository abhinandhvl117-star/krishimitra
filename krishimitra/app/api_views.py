from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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
    pass