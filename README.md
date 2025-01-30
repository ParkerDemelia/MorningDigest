# Morning Digest Assistant

A personal assistant that sends daily morning digest emails containing:
- Apple Health data
- Google Calendar events
- Weather updates
- Notion to-do lists
- World news
- Daily tips and more

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following credentials:
```
NOTION_TOKEN=your_notion_token
GOOGLE_CALENDAR_CREDENTIALS=path_to_credentials.json
WEATHER_API_KEY=your_weather_api_key
EMAIL_ADDRESS=your_email
EMAIL_PASSWORD=your_app_specific_password
APPLE_ID=your_apple_id
APPLE_PASSWORD=your_apple_password
```

3. Set up API access:
- Google Calendar API: Enable and download credentials
- Notion API: Create an integration and get the token
- OpenWeatherMap: Sign up for an API key
- Apple ID: Generate an app-specific password

4. Run the assistant:
```bash
python main.py
```

The digest will be sent every morning at your configured time. 