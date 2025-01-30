import requests
import os

class NewsService:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.is_configured = bool(self.api_key)

    def get_top_stories(self, num_stories=5):
        if not self.is_configured:
            return """
                <li>📰 News API not configured. To see real news:</li>
                <li>1. Get an API key from newsapi.org</li>
                <li>2. Add NEWS_API_KEY to your .env file</li>
            """

        try:
            params = {
                'apiKey': self.api_key,
                'language': 'en',
                'pageSize': num_stories
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('articles'):
                return "<li>No news stories available</li>"
            
            stories = []
            for article in data['articles']:
                title = article.get('title', '').replace('[+]', '').strip()
                source = article.get('source', {}).get('name', 'Unknown')
                stories.append(f"<li>📰 {title} - <em>{source}</em></li>")
            
            return "\n".join(stories)

        except Exception as e:
            # Fallback to sample news if API fails
            return """
                <li>📰 Global markets show positive trends amid economic recovery</li>
                <li>🌍 New climate agreement reached at international summit</li>
                <li>💡 Breakthrough in renewable energy technology announced</li>
                <li>🏥 Major advancement in medical research reported</li>
                <li>🚀 Tech sector continues to drive innovation</li>
            """ 