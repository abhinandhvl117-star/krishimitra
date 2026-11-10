from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegistrationSerializer, CropRecommendationSerializer
from rest_framework.permissions import AllowAny
import requests
from django.conf import settings
from .models import CropRecommendation, PricePrediction, DiseaseDetection, UserProfile
from .forms import STATE_DISTRICTS, COMMODITY_CHOICES
from .weather_service import default_city, get_weather, get_forecast, generate_advisory
import logging
from .chatbot_service import get_groq_reply
from .models import ChatMessage
from django.contrib.auth.models import User

FASTAPI_URL = getattr(settings, 'FASTAPI_URL')
MAX_IMAGE_MB = 10

COMMODITIES = [c[0] for c in COMMODITY_CHOICES]

logger = logging.getLogger(__name__)

def call_ml(path, timeout=15, **kwargs):
    try:
        resp = requests.post(f"{FASTAPI_URL}{path}",timeout=timeout, **kwargs)
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

        # FastAPI returns {"error": ...} with status 200 when something fails
        if "error" in body or "predicted crop" not in body:
            return Response({"detail": "Prediction failed. Please try again."}, status=502)

        predicted = body["predicted crop"]
        confidence = body.get("confidence")   # None if FastAPI didn't send it

        CropRecommendation.objects.create(user=request.user, recommended_crop=predicted, **data)

        return Response({
            "crop": predicted.title(),
            "confidence": confidence,
            "n": data["nitrogen"],
            "p": data["phosphorus"],
            "k": data["potassium"],
        })
        
class PriceOptionView(APIView):

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
    
class DiseaseSerializer(serializers.Serializer):
    image = serializers.ImageField()
    
    def validate_image(self, image):
        if image.size > MAX_IMAGE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"Image must be under {MAX_IMAGE_MB} MB.")
        return image
    
class DiseaseDetectionVIew(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = DiseaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data['image']
        
        image.seek(0)
        body, error = call_ml(
            "/disease", timeout=30,
            files = {"file": (image.name, image.read(), image.content_type)},
        )
        if error:
            return error
        if 'error' in body:
            return Response({"detail": body['error']}, status=status.HTTP_502_BAD_GATEWAY)
        
        prediction = body.get("prediction", "Unknown")
        cause = body.get("cause", "")
        cure = body.get("cure", "")
        
        if prediction == "Background_with_leaves":
            return Response(
                {"detail": "No plant leaf detected. Please upload a clear photo of the leave."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        
        if "___" in prediction:
            crop, condition = prediction.split("___", 1)
        else:
            crop, condition = "Unknown", prediction
        
        crop = crop.replace("_", " ")
        condition = condition.replace("_", " ").title()
        disease_name = f"{crop} - {condition}"
        
        image.seek(0)
        record = DiseaseDetection(
            user=request.user,
            crop_type=crop,
            disease_name=disease_name,
            description=f"Cause: {cause}",
            treatments=[cure] if cure else [],
        )
        record.image.save(image.name, image, save=True)
        
        return Response({
            "disease_name": disease_name,
            "crop": crop,
            "condition": condition,
            "healthy": condition.lower().startswith("healthy"),
            "cause": cause,
            "cure": cure,
        })
        
def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"city": default_city})
    return profile

def weather_payload(city):
    weather = get_weather(city)
    if not weather:
        return None
    return {
        "city": city,
        "weather": weather,
        "forecast": get_forecast(city),
        "advisory": generate_advisory(weather),
    }
    
class CitySerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100)
    
class WeatherView(APIView):
    def get(self, request):
        profile = get_or_create_profile(request.user)
        payload = weather_payload(profile.city)
        if payload is None:
            return Response(
                {"detail": f'Could not load weather for "{profile.city}"'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(payload)

    def post(self, request):
        serializer = CitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_city = serializer.validated_data["city"]
        
        payload = weather_payload(new_city)
        if payload is None:
            return Response(
                {"city": [f'Could not find "{new_city}". Please check the city name.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        profile = get_or_create_profile(request.user)
        profile.city = new_city
        profile.save()
        return Response(payload)
    
class ChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    
def recent_messages(user, limit=20):
    qs = ChatMessage.objects.filter(user=user).order_by("-created_at")[:limit]
    return list(qs)[::-1]

class ChatView(APIView):
    def get(self, request):
        return Response([
            {"id": m.id, "role": m.role, "content": m.content}
            for m in recent_messages(request.user)
        ])
    
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data["message"]
        
        history = recent_messages(request.user)
        city = get_or_create_profile(request.user).city
        
        try:
            reply = get_groq_reply(user_message=text, history=history, location=city)
        except (ValueError, ImportError):
            logger.exception("Chat service is not configured")
            return Response({"detail": "The chat service isn't configured yet"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            logger.exception("Groq API call failed")
            return Response({"detail": "Sorry, I'm having trouble responding right now. Please try again."},
                            status=status.HTTP_502_BAD_GATEWAY)
            
        ChatMessage.objects.create(user=request.user, role="user", content=text)
        ChatMessage.objects.create(user=request.user, role="bot", content=reply)
        return Response({"reply": reply})
    

def user_payload(user):
    profile = getattr(user, 'profile', None)
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "city": profile.city if profile else "",
        "is_staff": user.is_staff,
    }
    
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        extra_kwargs = {"email": {"required": True, "allow_blank": False}}
        
    def validate_email(self, value):
        taken = User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk)
        if taken.exists():
            raise serializers.ValidationError("That email is already registered to another account.")
        return value
    
class MeView(APIView):
    def get(self, request):
        return Response(user_payload(request.user))
    
    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(user_payload(request.user))
    
class DashboardView(APIView):
    def get(self, request):
        user = request.user
        city = get_or_create_profile(user).city
        
        crops = CropRecommendation.objects.filter(user=user)
        prices = PricePrediction.objects.filter(user=user)
        diseases = DiseaseDetection.objects.filter(user=user)
        
        latest_crop = crops.first()
        latest_price = prices.first()
        latest_disease = diseases.first()
        
        activity = []
        for c in crops[:2]:
            activity.append({"type": "crop", "title": "Crop recommendation generated",
                            "detail": f"{c.recommended_crop.title()} recommended",
                            "created_at": c.created_at})
        for d in diseases[:2]:
            activity.append({"type": "disease", "title": "Disease scan completed",
                             "detail": d.disease_name or "Analysis complete",
                             "created_at": d.created_at})   
        for p in prices[:1]:
            activity.append({"type": "price", "title": "Price prediction run",
                             "detail": f"{p.commodity} - ₹{round(p.predicted_price or 0)}/quintal",
                             "created_at": p.created_at})
        
        activity.sort(key=lambda a: a["created_at"], reverse=True)
        
        return Response({
            "weather": get_weather(city),
            "latest_crop": {"name": latest_crop.recommended_crop.title(),
                            "data": latest_crop.created_at} if latest_crop else None,
            "latest_price": {"commodity": latest_price.commodity, "price": latest_price.predicted_price,
                             "district": latest_price.district,
                             "date": latest_price.created_at} if latest_price else None,
            "lates_disease": {"name": latest_disease.disease_name,
                              "date": latest_disease.created_at} if latest_disease else None,
            "activity": activity[:5],
        })