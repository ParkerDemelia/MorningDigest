import requests
import os

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self.location = os.getenv('ZIP_CODE', '10001')  # Default to NYC if not set
        self.is_configured = bool(api_key)
        
        if not self.is_configured:
            print("Weather API key not configured")

    def get_daily_forecast(self):
        if not self.is_configured:
            return """
                <div class="weather-info">
                    <p>⚠️ Weather service not configured. To see weather:</p>
                    <p>1. Get an API key from visualcrossing.com</p>
                    <p>2. Add WEATHER_API_KEY to your .env file</p>
                </div>
            """
            
        try:
            url = f"{self.base_url}/{self.location}/today"
            params = {
                "unitGroup": "us",
                "key": self.api_key,
                "contentType": "json",
                "include": "current,days"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            current = data.get('currentConditions', {})
            today = data.get('days', [{}])[0]

            return f"""
                <div class="weather-info">
                    <p><strong>Current Weather in {data.get('resolvedAddress')}:</strong></p>
                    <p>🌡️ Temperature: {current.get('temp', 'N/A')}°F</p>
                    <p>🌤️ Conditions: {current.get('conditions', 'N/A')}</p>
                    <p>💨 Wind: {current.get('windspeed', 'N/A')} mph</p>
                    <p>⬆️ High: {today.get('tempmax', 'N/A')}°F</p>
                    <p>⬇️ Low: {today.get('tempmin', 'N/A')}°F</p>
                </div>
            """

        except Exception as e:
            return f"<div>Unable to fetch weather data: {str(e)}</div>" 