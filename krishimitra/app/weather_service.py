import logging
from datetime import datetime, timedelta, timezone as dt_tz
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import WeatherCache

logger = logging.getLogger(__name__)

OWN_URL = "https://api.openweathermap.org/data/2.5"
CACHE_MINS = 30
WIND_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
ICON_MAP = {"Clear": "☀️", "Clouds": "⛅", "Rain": "🌧️", "Drizzle": "🌦️",
            "Thunderstorm": "⛈️", "Snow": "❄️", "Mist": "🌫️"}

def default_city():
    return getattr(settings, "DEFAULT_WEATHER_CITY", "Kerala")

def get_weather(city=None):
    city = (city or default_city()).strip().title()
    
    cutoff = timezone.now() - timedelta(minutes=CACHE_MINS)
    cached = WeatherCache.objects.filter(city=city, fetched_at__gte=cutoff).first()
    if cached:
        return cached.data
    
    api_key = getattr(settings, "OPENWEATHERMAP_API_KEY", "")
    if not api_key:
        return None
    
    try:
        resp = requests.get(f"{OWN_URL}/weather", timeout=10,
                            params={"q": city, "appid": api_key, "units":"metric"})
        resp.raise_for_status()
        raw = resp.json()
    except requests.RequestException:
        logger.exception("Weather fetch failed for %s", city)
        return None
    
    sunrise = datetime.fromtimestamp(raw["sys"]["sunrise"] + raw.get("timezone", 0), tz=dt_tz.utc)
    
    data = {
        "city": raw["name"],
        "temp": round(raw["main"]["temp"]),
        "feels_like": round(raw["main"]["feels_like"]),
        "humidity": raw["main"]["humidity"],
        "description": raw["weather"][0]["description"].title(),
        "wind": round(raw["wind"]["speed"] * 3.6),
        "wind_dir": WIND_DIRS[round(raw["wind"].get("deg", 0) / 45) % 8],
        "rainfall": round(raw.get("rain", {}).get("1h", 0), 1),
        "temp_min": round(raw["main"]["temp_min"]),
        "temp_max": round(raw["main"]["temp_max"]),
        "sunrise": sunrise.strftime("%I:%M %p")
    }
    
    WeatherCache.objects.update_or_create(city=city, defaults={"data": data})
    return data

def get_forecast(city=None):
    city = (city or default_city()).strip().title()
    cache_key = f"forecast:{city}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    api_key = getattr(settings, "OPENWEATHERMAP_API_KEY", "")
    if not api_key:
        return []
    
    try:
        resp = requests.get(f"{OWN_URL}/forecast", timeout=10,
                            params={"q": city, "appid": api_key, "units": "metric", "cnt": 40})
        resp.raise_for_status()
        raw = resp.json()
    except requests.RequestException:
        logger.exception("Forecast fetch failed for %s", city)
        return []
    
    days = {}
    for item in raw["list"]:
        day = days.setdefault(item["dt_txt"][:10], {"temps": [], "icons": []})
        day["temps"].append(item["main"]["temp"])
        day["icons"].append(item["weather"][0]["main"])
        
    forecast = []
    for date, vals in list(days.items())[:7]:
        common_icon = max(set(vals["icons"]), key=vals["icons"].count)
        forecast.append({
            "day": datetime.strptime(date, "%Y-%m-%d").strftime("%a"),
            "icon": ICON_MAP.get(common_icon, "🌤️"),
            "max": round(max(vals["temps"])),
            "min": round(min(vals["temps"]))
        })
        
    cache.set(cache_key, forecast, CACHE_MINS * 60)
    return forecast

def generate_advisory(weather):
    if not weather:
        return []
    
    tips = []
    if weather["rainfall"] > 5:
        tips.append("Heavy rain expected - avoid pesticide or fertilizer application today.")
    if weather["humidity"] > 80:
        tips.append("High humidity increases fungal disease risk, Inspect crops for early signs.")
    if weather["temp"] > 35:
        tips.append("very high temperature - irrigate early morning or evening only.")
    if not tips:
        tips.append("Good conditions for field work.")
    return tips