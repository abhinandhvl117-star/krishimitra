from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .api_views import get_or_create_profile
from .models import CropRecommendation, DiseaseDetection, PricePrediction

class AdminUserRowSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    joined = serializers.DateTimeField(source="date_joined", read_only=True)
    crops = serializers.IntegerField(read_only=True)
    scans = serializers.IntegerField(read_only=True)
    prices = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "city", "joined",
                  "active", "crops", "scans", "prices"]
    
    def get_full_name(self, user):
        return user.get_full_name()
    
    def get_city(self, user):
        profile = getattr(user, "profile", None)
        return profile.city if profile else ""
    
    def get_active(self, user):
        profile = getattr(user, "profile", None)
        return profile.is_active_account if profile else True 
    
class CropRowSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    crop = serializers.CharField(source="recommeded_crop", read_only=True)
    
    class Meta:
        model = CropRecommendation
        fields = ["id", "username", "crop", "nitrogen", "phosphorous", "potassium",
                  "temperature", "humidity", "ph", "rainfall", "created_at"]
        
class DiseaseRowSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    
    class meta:
        model = DiseaseDetection
        fields = ["id", "username", "disease_name", "crop_type", "affected_part", "created_at"]
        
class PriceRowSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    price = serializers.FloatField(source="user.username", read_only=True)
    
    class Meta:
        model = PricePrediction
        fields = ["id", "username", "commodity", "state", "district", "price", "created_at"]
        
def annotated_farmers():
    return (
        User.objects.filter(is_staff=False)
        .select_related("profile")
        .annotate(
            crops=Count("crop_recommendation", distinct=True),
            scans=Count("disease_detection", distinct=True),
            prices=Count("price_predictions", distinct=True),
        )
    )

def latest(model, n):
    return model.objects.select_related("user").order_by("-created_at")[:n]

class AdminOverviewView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        recent_users = annotated_farmers().order_by("-date_joined")[:10]
        return Response ({
            "total": {
                "users": User.objects.filter(is_staff=False).count(),
                "crops": CropRecommendation.objects.count(),
                "diseases": DiseaseDetection.objects.count(),
                "prices": PricePrediction.objects.count(),
            },
            "recent_users": AdminUserRowSerializer(recent_users, many=True).data,
            "recent_crops": CropRowSerializer(latest(CropRecommendation, 10), many=True).data,
            "recent_diseases": DiseaseRowSerializer(latest(DiseaseDetection, 10), many=True).data,
            "recent_prices": PricePrediction(latest(PricePrediction, 10), many=True).data,
        })
        
class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]
    SORTS = {
        "date_desc": "-date_joined",
        "date_asc": "date_joined",
        "alpha_asc": "username",
        "alpha_desc": "-username",
    }
    
    def get(self, request):
        qs = annotated_farmers()
        q = request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(first_name__icontains=q)
                | Q(last_name__icontains=q) | Q(email__icontains=q)
            )
        qs = qs.order_by(self.SORTS.get(request.query_params.get("sort"), "-date_joined"))
        return Response({
            "total": User.objects.filter(is_staff=False).count(),
            "result": AdminUserRowSerializer(qs, many=True).data,
        })
        
class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, user_id):
        target = get_object_or_404(annotated_farmers(), pk=user_id)
        recent = lambda related: related.select_related("user").order_by("-created_at")[:10]
        return Response({
            "user": AdminUserRowSerializer(target).data,
            "crops": CropRowSerializer(recent(target.crop_recommendation), many=True).data,
            "diseases": DiseaseRowSerializer(recent(target.disease_detection), many=True).data,
            "prices": PriceRowSerializer(recent(target.price_predictions), many=True).data,
        })
        
class AdminUserToggleView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id, is_staff=False)
        profile = get_or_create_profile(target)
        profile.is_active_account = not profile.is_active_account
        profile.save()
        return Response({"id": target.id, "active": profile.is_active_account})
    
class AdminListView(APIView):
    permission_classes = [IsAdminUser]
    model = None
    serializer_class = None
    limit = 200
    
    def get(self, request):
        qs = self.model.objects.select_related("user").order_by("-created_at")
        return Response({
            "total": qs.count(),
            "results": self.serializer_class(qs[: self.limit], many=True).data,
        })
        
class AdminCropListView(AdminListView):
    model = CropRecommendation
    serializer_class = CropRowSerializer
    
class AdminDiseaseListView(AdminListView):
    model = DiseaseDetection
    serializer_class = DiseaseRowSerializer
    
class AdminPriceListView(AdminListView):
    model = PricePrediction
    serializer_class = PriceRowSerializer