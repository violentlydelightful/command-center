#!/usr/bin/env python3
"""
Command Center - Personal Intelligence Dashboard
Aggregates multiple APIs and uses AI to generate personalized briefings
"""

import os
import asyncio
import aiohttp
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

# API Keys (set in .env)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")  # openweathermap.org
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")  # newsapi.org
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY")  # alphavantage.co


class DataAggregator:
    """Fetches data from multiple APIs concurrently."""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    async def fetch_weather(self, session, city="New York"):
        """Fetch current weather from OpenWeatherMap."""
        if not WEATHER_API_KEY:
            return {"source": "weather", "error": "API key not configured", "demo": True,
                    "data": {"city": city, "temp": 72, "condition": "Partly Cloudy", "humidity": 45}}

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=imperial"
        try:
            async with session.get(url) as response:
                data = await response.json()
                return {
                    "source": "weather",
                    "data": {
                        "city": data.get("name", city),
                        "temp": round(data["main"]["temp"]),
                        "condition": data["weather"][0]["description"].title(),
                        "humidity": data["main"]["humidity"],
                        "feels_like": round(data["main"]["feels_like"]),
                    }
                }
        except Exception as e:
            return {"source": "weather", "error": str(e)}

    async def fetch_news(self, session, category="technology"):
        """Fetch top headlines from NewsAPI."""
        if not NEWS_API_KEY:
            return {"source": "news", "error": "API key not configured", "demo": True,
                    "data": [
                        {"title": "AI Continues to Transform Industries", "source": "Tech Daily"},
                        {"title": "New Framework Released for Web Development", "source": "Dev News"},
                        {"title": "Cloud Computing Costs Drop 20%", "source": "Business Insider"},
                    ]}

        url = f"https://newsapi.org/v2/top-headlines?category={category}&country=us&pageSize=5&apiKey={NEWS_API_KEY}"
        try:
            async with session.get(url) as response:
                data = await response.json()
                articles = [{"title": a["title"], "source": a["source"]["name"]}
                           for a in data.get("articles", [])[:5]]
                return {"source": "news", "data": articles}
        except Exception as e:
            return {"source": "news", "error": str(e)}

    async def fetch_stocks(self, session, symbols=["AAPL", "GOOGL", "MSFT"]):
        """Fetch stock data from Alpha Vantage."""
        if not ALPHA_VANTAGE_KEY:
            return {"source": "stocks", "error": "API key not configured", "demo": True,
                    "data": [
                        {"symbol": "AAPL", "price": 178.52, "change": 2.34, "change_pct": 1.32},
                        {"symbol": "GOOGL", "price": 141.23, "change": -0.87, "change_pct": -0.61},
                        {"symbol": "MSFT", "price": 378.91, "change": 4.56, "change_pct": 1.22},
                    ]}

        stocks = []
        for symbol in symbols[:3]:  # Limit API calls
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    quote = data.get("Global Quote", {})
                    if quote:
                        stocks.append({
                            "symbol": symbol,
                            "price": float(quote.get("05. price", 0)),
                            "change": float(quote.get("09. change", 0)),
                            "change_pct": float(quote.get("10. change percent", "0%").replace("%", ""))
                        })
            except Exception as e:
                pass
        return {"source": "stocks", "data": stocks if stocks else "Rate limited"}

    async def fetch_github_trending(self, session):
        """Fetch trending repos from GitHub."""
        url = "https://api.github.com/search/repositories?q=created:>2024-01-01&sort=stars&order=desc&per_page=5"
        try:
            async with session.get(url) as response:
                data = await response.json()
                repos = [{"name": r["full_name"], "stars": r["stargazers_count"], "description": r["description"][:80] if r["description"] else ""}
                        for r in data.get("items", [])[:5]]
                return {"source": "github", "data": repos}
        except Exception as e:
            return {"source": "github", "error": str(e), "demo": True,
                    "data": [{"name": "cool/project", "stars": 1234, "description": "Something interesting"}]}

    async def fetch_quote(self, session):
        """Fetch inspirational quote."""
        url = "https://api.quotable.io/random"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                data = await response.json()
                return {"source": "quote", "data": {"text": data["content"], "author": data["author"]}}
        except:
            quotes = [
                {"text": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
                {"text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
                {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
            ]
            import random
            return {"source": "quote", "data": random.choice(quotes), "demo": True}

    async def gather_all(self, city="New York", news_category="technology"):
        """Fetch all data sources concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_weather(session, city),
                self.fetch_news(session, news_category),
                self.fetch_stocks(session),
                self.fetch_github_trending(session),
                self.fetch_quote(session),
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return {r["source"]: r for r in results if isinstance(r, dict)}


class AIBriefingGenerator:
    """Generates AI-powered daily briefings from aggregated data."""

    def __init__(self):
        self.api_key = OPENAI_API_KEY

    async def generate_briefing(self, data):
        """Generate a personalized briefing using OpenAI."""
        if not self.api_key:
            return self._generate_mock_briefing(data)

        import openai
        client = openai.OpenAI(api_key=self.api_key)

        # Build context from aggregated data
        context = self._build_context(data)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a personal intelligence briefing assistant.
                    Generate a concise, engaging morning briefing based on the provided data.
                    Be conversational but professional. Highlight what's most relevant.
                    Include 2-3 actionable insights or things to watch today.
                    Keep it under 200 words."""},
                    {"role": "user", "content": f"Generate my morning briefing based on this data:\n\n{context}"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return {
                "briefing": response.choices[0].message.content,
                "generated_at": datetime.now().isoformat(),
                "ai_powered": True
            }
        except Exception as e:
            return self._generate_mock_briefing(data)

    def _build_context(self, data):
        """Build context string from aggregated data."""
        parts = []

        if "weather" in data and "data" in data["weather"]:
            w = data["weather"]["data"]
            parts.append(f"Weather in {w['city']}: {w['temp']}°F, {w['condition']}")

        if "news" in data and "data" in data["news"]:
            headlines = [n["title"] for n in data["news"]["data"][:3]]
            parts.append(f"Top headlines: {'; '.join(headlines)}")

        if "stocks" in data and "data" in data["stocks"] and isinstance(data["stocks"]["data"], list):
            stocks = [f"{s['symbol']}: ${s['price']:.2f} ({s['change_pct']:+.1f}%)" for s in data["stocks"]["data"]]
            parts.append(f"Markets: {', '.join(stocks)}")

        if "quote" in data and "data" in data["quote"]:
            q = data["quote"]["data"]
            parts.append(f"Quote of the day: \"{q['text']}\" - {q['author']}")

        return "\n".join(parts)

    def _generate_mock_briefing(self, data):
        """Generate a mock briefing when OpenAI is not available."""
        context = self._build_context(data)

        briefing = f"""Good morning! Here's your intelligence briefing for {datetime.now().strftime('%A, %B %d')}:

**Weather & Environment**
"""
        if "weather" in data and "data" in data["weather"]:
            w = data["weather"]["data"]
            briefing += f"It's {w['temp']}°F and {w['condition'].lower()} in {w['city']}. "

        briefing += "\n\n**What's Moving**\n"
        if "stocks" in data and "data" in data["stocks"] and isinstance(data["stocks"]["data"], list):
            for s in data["stocks"]["data"]:
                direction = "up" if s["change_pct"] > 0 else "down"
                briefing += f"• {s['symbol']} is {direction} {abs(s['change_pct']):.1f}% at ${s['price']:.2f}\n"

        briefing += "\n**Headlines to Watch**\n"
        if "news" in data and "data" in data["news"]:
            for n in data["news"]["data"][:3]:
                briefing += f"• {n['title']}\n"

        if "quote" in data and "data" in data["quote"]:
            q = data["quote"]["data"]
            briefing += f"\n**Thought for Today**\n\"{q['text']}\" — {q['author']}"

        return {
            "briefing": briefing,
            "generated_at": datetime.now().isoformat(),
            "ai_powered": False,
            "demo_mode": True
        }


# Initialize services
aggregator = DataAggregator()
briefing_generator = AIBriefingGenerator()


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/data")
def get_data():
    """Fetch all aggregated data."""
    city = request.args.get("city", "New York")
    category = request.args.get("category", "technology")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(aggregator.gather_all(city, category))
    loop.close()

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@app.route("/api/briefing")
def get_briefing():
    """Generate AI briefing from current data."""
    city = request.args.get("city", "New York")
    category = request.args.get("category", "technology")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(aggregator.gather_all(city, category))
    briefing = loop.run_until_complete(briefing_generator.generate_briefing(data))
    loop.close()

    return jsonify(briefing)


@app.route("/api/widget/<widget_type>")
def get_widget(widget_type):
    """Fetch data for a specific widget."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def fetch():
        async with aiohttp.ClientSession() as session:
            if widget_type == "weather":
                return await aggregator.fetch_weather(session, request.args.get("city", "New York"))
            elif widget_type == "news":
                return await aggregator.fetch_news(session, request.args.get("category", "technology"))
            elif widget_type == "stocks":
                symbols = request.args.get("symbols", "AAPL,GOOGL,MSFT").split(",")
                return await aggregator.fetch_stocks(session, symbols)
            elif widget_type == "github":
                return await aggregator.fetch_github_trending(session)
            elif widget_type == "quote":
                return await aggregator.fetch_quote(session)
            return {"error": "Unknown widget type"}

    result = loop.run_until_complete(fetch())
    loop.close()
    return jsonify(result)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Command Center - Personal Intelligence Dashboard")
    print("=" * 60)
    print("\n  Dashboard: http://localhost:5020")
    print("\n  Configure API keys in .env for full functionality:")
    print("    - OPENAI_API_KEY (AI briefings)")
    print("    - OPENWEATHER_API_KEY (weather)")
    print("    - NEWS_API_KEY (headlines)")
    print("    - ALPHA_VANTAGE_KEY (stocks)")
    print("\n  Demo mode works without API keys!")
    print("\n  Press Ctrl+C to stop\n")
    app.run(debug=True, port=5020)
