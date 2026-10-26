from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, CropRecommendation
from django.contrib.auth import password_validation
from django.db import transaction

class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False) 
    city = serializers.CharField(max_length=100, write_only=True)
    
    extra_kwargs = {
        'first_name': {'required': True},
        'email': {'required': True}
    }
        
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'city', 'password1', 'password2')
        
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email address is already exists")
        return value

    def validate_password1(self, value):
        password_validation.validate_password(value)
        return value
        
    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password2')
        password1 = validated_data.pop('password1')
        city = validated_data.pop('city')
        
        with transaction.atomic():
            user = User.objects.create_user(password=password1, **validated_data)
            UserProfile.objects.create(user=user, city=city)
        
        return user
    
class CropRecommendationSerializer(serializers.ModelSerializer):
    nitrogen = serializers.FloatField(min_value=0, max_value=300)
    phosphorus = serializers.FloatField(min_value=0, max_value=300)
    potassium = serializers.FloatField(min_value=0, max_value=300)
    temperature = serializers.FloatField(min_value=0, max_value=60)
    humidity = serializers.FloatField(min_value=0, max_value=100)
    ph = serializers.FloatField(min_value=0, max_value=14)
    rainfall = serializers.FloatField(min_value=0)
    class Meta:
        model = CropRecommendation
        fields = ('nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall')