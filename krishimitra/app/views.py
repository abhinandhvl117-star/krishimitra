import json
import base64
import logging
import random
import random
from datetime import datetime, timedelta
 
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from app.chatbot_service import get_groq_reply
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from app.models import (
    WeatherCache,
    CropRecommendation, 
    DiseaseDetection, 
    PricePrediction,
    ChatMessage,
    UserProfile,
)

from app.forms import( 
    RegisterForm,
    CropRecommendationForm,
    DiseaseDetectionForm,
    PricePredictionForm,
    UpdateCityForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    OTPForm
)


logger = logging.getLogger(__name__)

FASTAPI_URL = getattr(settings, 'FASTAPI_URL')
OWM_API_KEY = getattr(settings, 'OPENWEATHERMAP_API_KEY')
DEFAULT_CITY = getattr(settings, 'DEFAULT_WEATHER_CITY', '')


# helper functions
def get_time_of_day():
    
    hour = datetime.now().hour
    
    if hour < 12:
        return "Good Morning"
    if hour < 17:
        return "Good Afternoon"

    return "Good Evening"

def get_user_city(user):
    try:
        return user.profile.city or DEFAULT_CITY
    except UserProfile.DoesNotExist:
        return DEFAULT_CITY
    
def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'city': DEFAULT_CITY})
    return profile

    
def get_weather(city: str = DEFAULT_CITY):
    city = city or DEFAULT_CITY
    cache_cutoff = timezone.now() - timedelta(minutes=30)
    city = city.strip().title()
    cached = WeatherCache.objects.filter(city=city, fetched_at__gte=cache_cutoff).first()
    if cached:
        return cached.data
    if not OWM_API_KEY:
        return None
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        dirs = ['N','NE','E','SE','S','SW','W','NW']
        wind_dir = dirs[round(raw['wind'].get('deg', 0) / 45) % 8]
        data = {
            'city': raw['name'],
            'temp': round(raw['main']['temp']),
            'feels_like': round(raw['main']['feels_like']),
            'humidity': raw['main']['humidity'],
            'description': raw['weather'][0]['description'].title(),
            'wind': round(raw['wind']['speed'] * 3.6),
            'wind_dir': wind_dir,
            'rainfall': round(raw.get('rain', {}).get('1h', 0), 1),
            'temp_min': round(raw['main']['temp_min']),
            'temp_max': round(raw['main']['temp_max']),
            'uv': 'N/A',
            'sunrise': datetime.fromtimestamp(raw['sys']['sunrise']).strftime('%I:%M %p'),
        }
        WeatherCache.objects.update_or_create(city=city, defaults={'data': data})
        return data
    except Exception:
        logger.exception("Weather fetch failed")
        return None


def _get_forecast(city: str = DEFAULT_CITY):
    if not OWM_API_KEY:
        return []

    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OWM_API_KEY}&units=metric&cnt=56"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        days = {}
        for item in raw['list']:
            date = item['dt_txt'][:10]
            if date not in days:
                days[date] = {'temps': [], 'icons': []}
            days[date]['temps'].append(item['main']['temp'])
            days[date]['icons'].append(item['weather'][0]['main'])
        ICON_MAP = {'Clear':'☀️','Clouds':'⛅','Rain':'🌧️','Drizzle':'🌦️','Thunderstorm':'⛈️','Snow':'❄️','Mist':'🌫️'}
        forecast = []
        for date, vals in list(days.items())[:7]:
            day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%a')
            icon_key = max(set(vals['icons']), key=vals['icons'].count)
            forecast.append({
                'day': day_name,
                'icon': ICON_MAP.get(icon_key, '🌤️'),
                'max': round(max(vals['temps'])),
                'min': round(min(vals['temps'])),
            })
        return forecast
    except Exception:
        logger.exception("Forecast fetch failed")
        return []
    
def generate_advisory(weather):
    
    if not weather:
        return []
    
    tips = []
    rain = weather.get('rainfall', 0)
    hum = weather.get('humidity',0)
    temp = weather.get('temp',25)
    
    if rain > 5:
        tips.append("Heavy rain excepted - avoid pesticide or fertilizer application today.")
    if hum > 80:
        tips.append("High humidity increases fungal disease risk. Inspect crops for early signs")
    if temp > 35:
        tips.append("Very high temperature - irrigate early morning or evening only")
    if not tips:
        tips.append("Good conditions for field work. Ideal for transplanting and top-dressing")
        
    return ''.join(tips)

# enable and disable user 
def _check_account_active(user):
    try:
        return user.profile.is_active_account
    except Exception:
        return True

# auth
def landing_view(request):
    return render(request, 'landing.html')
 
 
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()

        if not _check_account_active(user):
            messages.error(request, "Your account has been disabled. Please contact support.")
            return render(request, 'login.html', {'form': form})

        login(request, user)

        if user.is_staff:
            return redirect('admin_dashboard')

        return redirect(request.GET.get('next', 'dashboard'))

    return render(request, 'login.html', {'form': form})
 
 
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        # Create profile with city from registration form
        city = form.cleaned_data.get('city', DEFAULT_CITY)
        UserProfile.objects.create(user=user, city=city)
        login(request, user)
        messages.success(request, f'Welcome to KrishiMitra, {user.first_name}! 🌿')
        return redirect('dashboard')
    return render(request, 'register.html', {'form': form})
 
 
def logout_view(request):
    logout(request)
    return redirect('landing')

# forgot password
otp_storage = {}


def forgot_password_view(request):

    form = CustomPasswordResetForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        email = form.cleaned_data['email']

        users = User.objects.filter(email=email)

        if users.exists():

            user = users.first()

            otp = str(random.randint(100000, 999999))

            otp_storage[email] = otp

            try:

                send_mail(
                    subject='KrishiMitra OTP Verification',
                    message=(
                        f"Hi {user.first_name or user.username},\n\n"
                        f"Your OTP for password reset is:\n\n"
                        f"{otp}\n\n"
                        f"This OTP expires in 5 minutes."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

                request.session['reset_email'] = email

                return redirect('verify_otp')

            except Exception as e:
                print(e)
                messages.error(request, 'Failed to send OTP.')

        else:
            messages.error(request, 'No account found.')

    return render(request, 'forgot_password.html', {
        'form': form
    })

def verify_otp_view(request):

    form = OTPForm(request.POST or None)

    email = request.session.get('reset_email')

    if not email:
        return redirect('forgot_password')

    if request.method == 'POST' and form.is_valid():

        entered_otp = form.cleaned_data['otp']

        real_otp = otp_storage.get(email)

        if entered_otp == real_otp:

            request.session['otp_verified'] = True

            return redirect('reset_password')

        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'verify_otp.html', {
        'form': form
    }) 
 
def reset_password_view(request):

    email = request.session.get('reset_email')
    verified = request.session.get('otp_verified')

    if not email or not verified:
        return redirect('forgot_password')

    user = User.objects.get(email=email)

    form = CustomSetPasswordForm(user, request.POST or None)

    if request.method == 'POST' and form.is_valid():

        form.save()

        otp_storage.pop(email, None)

        request.session.flush()

        messages.success(
            request,
            'Password reset successful!'
        )

        return redirect('login')

    return render(request, 'reset_password.html', {
        'form': form
    })


# dashboard
@login_required
def dashboard_view(request):
    weather = get_weather()
    latest_crop = CropRecommendation.objects.filter(user=request.user).first()
    latest_price = PricePrediction.objects.filter(user=request.user).first()
    latest_disease = DiseaseDetection.objects.filter(user=request.user).first()

    activity = []
    for obj in CropRecommendation.objects.filter(user=request.user)[:2]:
        activity.append({'color':'var(--green-400)','badge':'green','tag':'Crop',
            'title':'Crop recommendation generated','detail':f"{obj.recommended_crop} recommended",
            'time': timezone.localtime(obj.created_at).strftime('%b %d, %I:%M %p')})
    for obj in DiseaseDetection.objects.filter(user=request.user)[:2]:
        activity.append({'color':'var(--coral-400)','badge':'coral','tag':'Disease',
            'title':'Disease scan completed','detail':obj.disease_name or 'Analysis complete',
            'time': timezone.localtime(obj.created_at).strftime('%b %d, %I:%M %p')})
    for obj in PricePrediction.objects.filter(user=request.user)[:1]:
        activity.append({'color':'var(--amber-400)','badge':'amber','tag':'Price',
            'title':'Price prediction run','detail':f"{obj.commodity} — ₹{obj.predicted_price}/quintal",
            'time': timezone.localtime(obj.created_at).strftime('%b %d, %I:%M %p')})
    activity.sort(key=lambda x: x['time'], reverse=True)

    return render(request, 'dashboard.html', {
        'time_of_day': get_time_of_day(),
        'weather': weather,
        'latest_crop': latest_crop.recommended_crop if latest_crop else None,
        'crop_confidence': f"Last: {latest_crop.created_at.strftime('%b %d')}" if latest_crop else None,
        'latest_price': f"{latest_price.predicted_price:.0f}" if latest_price else None,
        'latest_price_crop': latest_price.commodity if latest_price else 'Commodity',
        'district': latest_price.district if latest_price else None,
        'price_trend': 'View prediction',
        'plant_health': latest_disease.disease_name if latest_disease else None,
        'last_scan': f"Last scan: {latest_disease.created_at.strftime('%b %d')}" if latest_disease else None,
        'health_status': latest_disease.disease_name if latest_disease else None,
        'recent_activity': activity[:5],
    })
    
# edit profile

@login_required
@require_POST
def edit_profile_view(request):
    user = request.user
    first_name = request.POST.get('first_name', '').strip()
    last_name  = request.POST.get('last_name', '').strip()
    username   = request.POST.get('username', '').strip()
    email      = request.POST.get('email', '').strip()
 
    errors = []
 
    if not username:
        errors.append('Username cannot be empty.')
    elif username != user.username and User.objects.filter(username=username).exists():
        errors.append('That username is already taken.')
 
    if email and email != user.email and User.objects.filter(email=email).exists():
        errors.append('That email is already registered to another account.')
 
    if errors:
        for e in errors:
            messages.error(request, e)
    else:
        user.first_name = first_name
        user.last_name  = last_name
        user.username   = username
        user.email      = email
        user.save()
        messages.success(request, 'Profile updated successfully! ✅')
 
    return redirect('dashboard')
    
# crop
@login_required
def crop_view(request):
    form = CropRecommendationForm(request.POST or None)
    result = None

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        payload = {
            "N": data['nitrogen'],
            "P": data['phosphorus'],
            "K": data['potassium'],
            "temperature": data['temperature'],
            "humidity": data['humidity'],
            "ph": data['ph'],
            "rainfall": data['rainfall'],
        }

        try:
            resp = requests.post(f"{FASTAPI_URL}/crop", json=payload, timeout=15)
            resp.raise_for_status()
            api_result = resp.json()

            predicted_crop = api_result.get('predicted crop', 'Unknown')

            obj = CropRecommendation.objects.create(
                user=request.user,
                nitrogen=data['nitrogen'],
                phosphorus=data['phosphorus'],
                potassium=data['potassium'],
                temperature=data['temperature'],
                humidity=data['humidity'],
                ph=data['ph'],
                rainfall=data['rainfall'],
                recommended_crop=predicted_crop,
            )

            result = {
                'crop': predicted_crop.title(),
                'n': data['nitrogen'],
                'p': data['phosphorus'],
                'k': data['potassium'],
            }

        except requests.exceptions.ConnectionError:
            messages.error(request, "Could not connect to the AI service. Make sure FastAPI is running on port 8001.")
        except requests.exceptions.Timeout:
            messages.error(request, "The AI service took too long. Please try again.")
        except Exception as e:
            logger.exception("Crop prediction failed")
            messages.error(request, f"Prediction failed: {str(e)}")

    return render(request, 'crop.html', {'form': form, 'result': result})

# disease
@login_required
def disease_view(request):
    form = DiseaseDetectionForm(request.POST or None, request.FILES or None)
    result = None

    if request.method == 'POST' and form.is_valid():
        image_file = request.FILES['image']

        try:
            image_file.seek(0)
            files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
            resp = requests.post(
                f"{FASTAPI_URL}/disease",
                files=files,
                timeout=30,
            )

            resp.raise_for_status()
            api_result = resp.json()

            prediction = api_result.get('prediction', 'Unknown')
            cause = api_result.get('cause', '')
            cure = api_result.get('cure', '')

            if '___' in prediction:
                parts = prediction.split('___')
                display_name = f"{parts[0]} — {parts[1].replace('_', ' ').title()}"
            else:
                display_name = prediction.replace('_', ' ').title()

            image_file.seek(0)
            obj = DiseaseDetection(
                user=request.user,
                crop_type='unknown',
                affected_part='unknown',
                disease_name=display_name,
                description=f"Cause: {cause}",
                treatments=[cure] if cure else [],
            )
            obj.image.save(image_file.name, image_file, save=True)

            result = {
                'disease_name': display_name,
                'cause': cause,
                'cure': cure,
            }

        except requests.exceptions.ConnectionError:
            messages.error(request, "Could not connect to FastAPI. Make sure it is running on port 8001.")
        except requests.exceptions.Timeout:
            messages.error(request, "Image analysis took too long. Please try again.")
        except Exception as e:
            logger.exception("Disease detection failed")
            messages.error(request, f"Detection failed: {str(e)}")

    return render(request, 'disease.html', {'form': form, 'result': result})


# price prediction
@login_required
def price_view(request):
    from .forms import STATE_CHOICES, DISTRICT_CHOICES, COMMODITY_CHOICES, STATE_DISTRICTS
    now          = datetime.now()
    month_choices = []
    for i in range(4):
        dt = (now.replace(day=1) + timedelta(days=32 * i)).replace(day=1)
        month_choices.append({'value': dt.strftime('%Y-%m'), 'label': dt.strftime('%B %Y')})
 
    form      = PricePredictionForm(request.POST or None)
    result    = None
    form_data = request.POST if request.method == 'POST' else {}
 
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        try:
            resp = requests.post(f"{FASTAPI_URL}/mandi", json={
                "State": data['state'], "District": data['district'], "Commodity": data['commodity'],
            }, timeout=15)
            resp.raise_for_status()
            api_result = resp.json()
            predicted_price = api_result.get('predicted_price', 0)
            PricePrediction.objects.create(
                user=request.user, state=data['state'], district=data['district'],
                commodity=data['commodity'], predicted_price=predicted_price,
            )
            result = {
                'predicted_price': f"{predicted_price:.2f}",
                'state': data['state'], 'district': data['district'], 'commodity': data['commodity'],
            }
        except requests.exceptions.ConnectionError:
            messages.error(request, "Could not connect to FastAPI. Make sure it is running on port 8001.")
        except Exception as e:
            logger.exception("Price prediction failed")
            messages.error(request, f"Prediction failed: {str(e)}")
 
    return render(request, 'price.html', {
        'form': form, 'form_data': form_data, 'result': result,
        'states':               sorted(STATE_DISTRICTS.keys()),
        'commodities':          [c[0] for c in COMMODITY_CHOICES],
        'months':               month_choices,
        'state_districts_json': json.dumps(STATE_DISTRICTS),
    })
 
    
# weather
@login_required
def weather_view(request):
    profile = get_or_create_profile(request.user)
    city    = profile.city or DEFAULT_CITY
    error   = None
 
    if request.method == 'POST':
        city_form = UpdateCityForm(request.POST)
        if city_form.is_valid():
            new_city = city_form.cleaned_data['city'].strip()
            test = get_weather(new_city)
            if test:
                WeatherCache.objects.filter(city__iexact=city).delete()
                profile.city = new_city
                profile.save()
                city = new_city
                messages.success(request, f"Location updated to {new_city}.")
            else:
                messages.error(request, f'Could not find "{new_city}". Please check the city name.')
    else:
        city_form = UpdateCityForm(initial={'city': city})
 
    WeatherCache.objects.filter(city__iexact=city, fetched_at__lt=timezone.now() - timedelta(minutes=30)).delete()
    weather  = get_weather(city)
    forecast = _get_forecast(city) if weather else []
 
    return render(request, 'weather.html', {
        'weather':      weather,
        'forecast':     forecast,
        'advisory':     generate_advisory(weather),
        'current_city': city,
        'city_form':    city_form,
        'error':        error,
    })
    
# chatbot
@login_required
def chatbot_view(request):
    chat_history = list(reversed(
        ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:20]
    ))
    return render(request, 'chatbot.html', {'chat_history': chat_history})


@login_required
@require_POST
def chatbot_ask_view(request):
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    ChatMessage.objects.create(user=request.user, role='user', content=user_message)

    history = list(reversed(
        ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:20]
    ))

    try:
        reply = get_groq_reply(user_message=user_message, history=history, location=DEFAULT_CITY)
    except ValueError as e:
        logger.error("Groq config error: %s", e)
        reply = "The AI service is not configured. Please set the GROQ_API_KEY in settings.py."
    except ImportError:
        reply = "The groq package is not installed. Run: pip install groq"
    except Exception:
        logger.exception("Groq API call failed")
        reply = "Sorry, I'm having trouble responding right now. Please try again."

    ChatMessage.objects.create(user=request.user, role='bot', content=reply)
    return JsonResponse({'reply': reply})


# admin and admin helper
def is_admin(user):
    return user.is_authenticated and user.is_staff
 
 
def _build_user_list(queryset):
    result = []
    for u in queryset:
        profile = get_or_create_profile(u)
        result.append({
            'user':    u,
            'profile': profile,
            'active':  profile.is_active_account,
            'crops':   u.crop_recommendation.count(),
            'scans':   u.disease_detection.count(),
            'prices':  u.price_predictions.count(),
        })
    return result

# admin dash 
@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_dashboard_view(request):
    recent_users_qs = User.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    return render(request, 'admin_dashboard.html', {
        'total_users':    User.objects.filter(is_staff=False).count(),
        'total_crops':    CropRecommendation.objects.count(),
        'total_diseases': DiseaseDetection.objects.count(),
        'total_prices':   PricePrediction.objects.count(),
        'recent_users':   _build_user_list(recent_users_qs),
        'recent_crops':   CropRecommendation.objects.select_related('user').order_by('-created_at')[:10],
        'recent_diseases':DiseaseDetection.objects.select_related('user').order_by('-created_at')[:10],
        'recent_prices':  PricePrediction.objects.select_related('user').order_by('-created_at')[:10],
    })
    
# admin user 
@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_users_view(request):
    sort  = request.GET.get('sort', 'date_desc')
    search = request.GET.get('q', '').strip()
    order = {
        'date_desc':  '-date_joined',
        'date_asc':   'date_joined',
        'alpha_asc':  'username',
        'alpha_desc': '-username',
    }.get(sort, '-date_joined')
 
    if request.method == 'POST':
        user_id = request.POST.get('toggle_user_id')
        if user_id:
            target = get_object_or_404(User, pk=user_id, is_staff=False)
            profile = get_or_create_profile(target)
            profile.is_active_account = not profile.is_active_account
            profile.save()
            status = "enabled" if profile.is_active_account else "disabled"
            messages.success(request, f"Account '{target.username}' has been {status}.")
        return redirect(f'/admin-panel/users/?sort={sort}')
 
    qs = User.objects.filter(is_staff=False).order_by(order)
    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
 
    return render(request, 'admin_user.html', {
        'user_list':    _build_user_list(qs),
        'total_users':  User.objects.filter(is_staff=False).count(),
        'current_sort': sort,
        'search':       search,
    })
    
# adim user details
@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_user_detail_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id, is_staff=False)
    profile     = get_or_create_profile(target_user)
 
    if request.method == 'POST' and request.POST.get('action') == 'toggle':
        profile.is_active_account = not profile.is_active_account
        profile.save()
        status = "enabled" if profile.is_active_account else "disabled"
        messages.success(request, f"Account '{target_user.username}' has been {status}.")
        return redirect('admin_user_detail', user_id=user_id)
 
    return render(request, 'admin_user_details.html', {
        'target_user':    target_user,
        'profile':        profile,
        'crop_count':     target_user.crop_recommendation.count(),
        'disease_count':  target_user.disease_detection.count(),
        'price_count':    target_user.price_predictions.count(),
        'crop_history':   target_user.crop_recommendation.order_by('-created_at')[:10],
        'disease_history':target_user.disease_detection.order_by('-created_at')[:10],
        'price_history':  target_user.price_predictions.order_by('-created_at')[:10],
    })
    
# admin data
@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_crops_view(request):
    return render(request, 'admin_crop.html', {
        'objects': CropRecommendation.objects.select_related('user').order_by('-created_at'),
        'total':   CropRecommendation.objects.count(),
    })
 
 
@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_diseases_view(request):
    return render(request, 'admin_disease.html', {
        'objects': DiseaseDetection.objects.select_related('user').order_by('-created_at'),
        'total':   DiseaseDetection.objects.count(),
    })
 
 
@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_prices_view(request):
    return render(request, 'admin_price.html', {
        'objects': PricePrediction.objects.select_related('user').order_by('-created_at'),
        'total':   PricePrediction.objects.count(),
    })