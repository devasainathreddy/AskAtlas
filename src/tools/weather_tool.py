"""Weather tool supporting OpenWeatherMap with free Open-Meteo fallback."""

import aiohttp
from langchain_core.tools import tool
from pydantic import BaseModel, Field


WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherInput(BaseModel):
    """Input schema for weather tool."""

    city: str = Field(description="Name of the city to get weather for")


async def _get_weather_open_meteo(session: aiohttp.ClientSession, city: str) -> str:
    """Fetch weather data from Open-Meteo (free, zero API key required)."""
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    async with session.get(geocode_url) as geo_res:
        if geo_res.status != 200:
            return f"Error resolving city '{city}': HTTP {geo_res.status}"
        geo_data = await geo_res.json()
        results = geo_data.get("results")
        if not results:
            return f"City '{city}' not found. Please check the city name and try again."

        location = results[0]
        lat = location.get("latitude")
        lon = location.get("longitude")
        city_name = location.get("name", city)
        country = location.get("country", "")

    forecast_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
    )
    async with session.get(forecast_url) as forecast_res:
        if forecast_res.status != 200:
            return f"Error fetching forecast for '{city}': HTTP {forecast_res.status}"
        forecast_data = await forecast_res.json()
        current = forecast_data.get("current", {})

        temp = current.get("temperature_2m", "N/A")
        feels_like = current.get("apparent_temperature", temp)
        humidity = current.get("relative_humidity_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        code = current.get("weather_code", 0)
        condition = WMO_WEATHER_CODES.get(code, "Clear")

        loc_str = f"{city_name}, {country}" if country else city_name
        return (
            f"### Weather in {loc_str}\n"
            f"* **Temperature:** {temp}°C (feels like {feels_like}°C)\n"
            f"* **Conditions:** {condition}\n"
            f"* **Humidity:** {humidity}%\n"
            f"* **Wind Speed:** {wind_speed} km/h"
        )


@tool(args_schema=WeatherInput)
async def get_weather(city: str) -> str:
    """Fetch current weather data for a given city.
    
    Uses OpenWeatherMap if configured, or falls back automatically to
    Open-Meteo (free, zero API key required).
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        Formatted string with weather information
    """
    from src.config import get_settings

    settings = get_settings()
    api_key = (settings.openweathermap_api_key or "").strip()
    normalized_key = api_key.lower()

    placeholder_markers = (
        "your_",
        "placeholder",
        "changeme",
        "<your_key>",
        "example",
        "todo",
    )
    has_valid_owm_key = api_key and not any(marker in normalized_key for marker in placeholder_markers)

    try:
        async with aiohttp.ClientSession() as session:
            if has_valid_owm_key:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_info = {
                            "city": data["name"],
                            "country": data["sys"]["country"],
                            "temperature": data["main"]["temp"],
                            "feels_like": data["main"]["feels_like"],
                            "humidity": data["main"]["humidity"],
                            "description": data["weather"][0]["description"],
                            "wind_speed": data["wind"]["speed"],
                        }
                        return (
                            f"### Weather in {weather_info['city']}, {weather_info['country']}\n"
                            f"* **Temperature:** {weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C)\n"
                            f"* **Conditions:** {weather_info['description'].capitalize()}\n"
                            f"* **Humidity:** {weather_info['humidity']}%\n"
                            f"* **Wind Speed:** {weather_info['wind_speed']} m/s"
                        )
                    elif response.status == 404:
                        return f"City '{city}' not found. Please check the city name and try again."
                    # If 401/error on OpenWeatherMap, fallback to Open-Meteo
                    return await _get_weather_open_meteo(session, city)

            # If no OpenWeatherMap key, use Open-Meteo directly
            return await _get_weather_open_meteo(session, city)

    except aiohttp.ClientError as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
