"""Weather tool using OpenWeatherMap API."""

import aiohttp
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    """Input schema for weather tool."""

    city: str = Field(description="Name of the city to get weather for")


@tool(args_schema=WeatherInput)
async def get_weather(city: str) -> str:
    """Fetch current weather data for a given city using OpenWeatherMap API.
    
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
    if not api_key or any(marker in normalized_key for marker in placeholder_markers):
        return (
            "OpenWeatherMap is not configured. Add a valid OPENWEATHERMAP_API_KEY to your "
            ".env file to enable live weather lookups."
        )

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        async with aiohttp.ClientSession() as session:
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
                else:
                    return f"Error fetching weather data: HTTP {response.status}"
    except aiohttp.ClientError as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
