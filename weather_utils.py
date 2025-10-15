from dotenv import load_dotenv
import requests
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def get_weather(city, units="metric"):
    """Fetch current weather for a given city."""
    url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units={units}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_forecast(city, units="metric"):
    """Fetch 5-day / 3-hour forecast for a given city."""
    url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units={units}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_uv_index(lat, lon):
    """Fetch current UV index using One Call API (free tier)."""
    url = (
        f"{BASE_URL}/onecall"
        f"?lat={lat}&lon={lon}"
        f"&exclude=minutely,hourly,daily,alerts"
        f"&appid={API_KEY}"
    )

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("current", {}).get("uvi")  
    return None

def get_city_image(city):
    """Fetch a photo URL for the given city."""
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": city,
        "orientation": "landscape",
        "client_id": UNSPLASH_KEY,
        "per_page": 1
    }
    r = requests.get(url, params=params)
    if r.status_code == 200 and r.json()["results"]:
        return r.json()["results"][0]["urls"]["regular"]
    return None

def get_air_quality(lat, lon):
    """Fetch current air quality index for given coordinates."""
    url = f"{BASE_URL}/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("list"):
            return data["list"][0]["main"]["aqi"]
    return None

def aqi_category(aqi):
    """Convert numeric AQI (1–5) to descriptive label."""
    if aqi is None:
        return "Not available"
    if aqi == 1:
        return "Good"
    elif aqi == 2:
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4:
        return "Poor"
    else:  
        return "Very Poor"