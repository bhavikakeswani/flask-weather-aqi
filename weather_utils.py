from dotenv import load_dotenv
import requests
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

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
