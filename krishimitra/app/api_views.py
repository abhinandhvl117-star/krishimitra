from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegistrationSerializer, CropRecommendationSerializer
from rest_framework.permissions import AllowAny
import requests
from django.conf import settings
from .models import CropRecommendation, PricePrediction
from .forms import STATE_DISTRICTS, COMMODITY_CHOICES

FASTAPI_URL = getattr(settings, 'FASTAPI_URL')

COMMODITIES = [c[0] for c in COMMODITY_CHOICES]

def call_ml(path, **kwargs):
    try:
        resp = requests.post(f"{FASTAPI_URL}{path}",timeout=15, **kwargs)
        resp.raise_for_status()
        return resp.json(), None
        
    except requests.exceptions.Timeout:
        return None, Response({"detail": "The AI service took too long. Please try again"},
                        status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return None, Response({"detail": "Could not connect to the AI service."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except requests.exceptions.RequestException:
        return None, Response({"detail": "The AI service returned an error."},
                        status=status.HTTP_502_BAD_GATEWAY)
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
    # permission_classes = [AllowAny]
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
        
        body, error = call_ml("/crop", json=payload)
        if error:
            return error
        
        predicted = body.get("predicted crop", "unknown")

        CropRecommendation.objects.create(user=request.user, recommended_crop=predicted, **data)
        
        return Response({
            "crop": predicted.title(),
            "n": data["nitrogen"],
            "p": data["phosphorus"],
            "k": data["potassium"]
        })
        
class PriceOptionView(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "state": {s: sorted(d) for s, d in sorted(STATE_DISTRICTS.items())},
            "commodities": COMMODITIES
        })        

class PricePredictionSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=sorted(STATE_DISTRICTS))
    district = serializers.CharField(max_length=100)
    commodity = serializers.ChoiceField(choices=COMMODITIES)
    
    class Meta:
        model = PricePrediction
        fields = ['state', 'district', 'commodity']
    
    def validate(self, attrs):
        if attrs['district'] not in STATE_DISTRICTS[attrs['state']]:
            raise serializers.ValidationError(
                {"district": "This district does not belong in the selected state."}
            )
        return attrs 
    
class PricePredictionView(APIView):
    # permission_classes = [AllowAny]
    def post(self, request):
        serializer = PricePredictionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        payload = {
            "State": data["state"],
            "District": data["district"],
            "Commodity": data["commodity"]
        }
        
        body, error = call_ml("/mandi", json=payload)
        if error:
            return error
        if "error" in body:
            return Response({"detail": body["error"]}, status=status.HTTP_400_BAD_REQUEST)
        
        price = body.get("predicted_price", 0)
        PricePrediction.objects.create(user=request.user, predicted_price=price, **data)
        
        return Response({"predicted_price": round(price, 2), **data})