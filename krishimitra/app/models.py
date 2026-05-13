from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CropRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_recommendation')
    
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    
    recommended_crop = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.recommended_crop} ({self.created_at.date()})"
    

class PricePrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_predictions')

    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    commodity = models.CharField(max_length=100)

    predicted_price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.commodity} ₹{self.predicted_price} ({self.created_at.date()})"

    
class DiseaseDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disease_detection')
    
    image = models.ImageField(upload_to='disease_images')
    crop_type = models.CharField(max_length=100)
    affected_part = models.CharField(max_length=100)
    
    disease_name = models.CharField(max_length=200, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    description =  models.TextField(blank=True)
    treatments = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.disease_name} on {self.crop_type} ({self.created_at.date()})"


class WeatherCache(models.Model):
    city = models.CharField(max_length=100)
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now=True)
    
    class Meta():
        ordering = ['-fetched_at']
        
    def __str__(self):
        return f"{self.city} - {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"
    
class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('bot', 'Bot')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} [{self.role}]: {self.content[:60]}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    city = models.CharField(max_length=100, default='Palakkad')
    is_active_account = models.BooleanField(default=True)  # admin enable/disable
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.user.username} — {self.city}"