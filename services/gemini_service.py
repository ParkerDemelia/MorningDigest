import os
import google.generativeai as genai
import re
import logging

# Configure logging to suppress gRPC warnings
logging.basicConfig(level=logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not set, using default formatting")
            self.model = None
            return
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _clean_data(self, text):
        if not text:
            return ""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove extra spaces around HTML tags
        text = re.sub(r'\s*(<[^>]+>)\s*', r'\1', text)
        return text

    def generate_email(self, health_data, events, weather, news, assignments):
        if not self.model:
            return None
            
        # Clean all input data
        health_data = self._clean_data(health_data)
        events = self._clean_data(events)
        weather = self._clean_data(weather)
        news = self._clean_data(news)
        assignments = self._clean_data(assignments)
            
        prompt = f"""You are a personal assistant writing a morning digest email. Write a friendly, concise email that includes all the data provided.

IMPORTANT: Return ONLY valid HTML that follows this exact structure:
<html><body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0; padding: 0; background-color: #ffffff; color: #000000;">[Your content here, using h1, h2, p, and div tags with inline styles]</body></html>

Use these styles:
- h1: style="font-size: 24px; margin: 0 0 15px 0; color: #000000;"
- h2: style="font-size: 18px; margin: 15px 0 5px 0; color: #000000;"
- p: style="margin: 0 0 10px 0; color: #000000;"
- div: style="margin: 0; padding: 0; background: none;"
- ul: style="margin: 0 0 15px 0; padding-left: 20px;"

Data to include:
ASSIGNMENTS: {assignments}
HEALTH: {health_data}
CALENDAR: {events}
WEATHER: {weather}
NEWS: {news}

Guidelines:
1. Keep the emojis from the original data
2. Add 1-2 brief suggestions about which assignments to prioritize
3. Return a single line of HTML with NO extra spaces or newlines
4. Use ONLY the styles specified above
5. Keep the tone friendly but professional and motivating
6. If there are assignments due today, emphasize their urgency
7. Suggest a study schedule if there are multiple assignments"""
        
        try:
            response = self.model.generate_content(prompt)
            content = self._clean_data(response.text)
            if not content.startswith('<html>'):
                content = f'<html><body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0; padding: 0; background-color: #ffffff; color: #000000;">{content}</body></html>'
            return content
        except Exception as e:
            print(f"Gemini generation failed: {str(e)}")
            return None 