# Command Center

Personal intelligence dashboard that aggregates multiple APIs and uses AI to generate personalized daily briefings.

## What It Does

- **Aggregates 5+ data sources** concurrently (weather, news, stocks, GitHub, quotes)
- **AI-powered briefings** that synthesize all data into actionable insights
- **Real-time dashboard** with live updates
- **Demo mode** works without any API keys

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Command Center                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Weather    │  │    News      │  │   Stocks     │       │
│  │  (OpenWeather)│  │  (NewsAPI)   │  │(AlphaVantage)│       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │               │
│         └────────────────┼─────────────────┘               │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │   Data Aggregator     │  ← Async/Concurrent  │
│              │   (aiohttp)           │                      │
│              └───────────┬───────────┘                      │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │  AI Briefing Generator│  ← OpenAI GPT        │
│              │                       │                      │
│              └───────────┬───────────┘                      │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │   Dashboard UI        │  ← Real-time updates │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Multi-Source Data Aggregation
- **Weather**: Current conditions from OpenWeatherMap
- **News**: Top headlines by category from NewsAPI
- **Stocks**: Real-time quotes from Alpha Vantage
- **GitHub**: Trending repositories
- **Quotes**: Daily inspiration from Quotable API

### AI-Powered Briefings
Uses OpenAI GPT to synthesize all data into a personalized morning briefing:
- Highlights what's most relevant
- Provides actionable insights
- Conversational, engaging tone

### Async Architecture
All API calls happen concurrently using `aiohttp` for fast page loads.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run (demo mode - no API keys needed)
python app.py

# Open http://localhost:5020
```

## Full Setup (with APIs)

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - [OpenAI](https://platform.openai.com) - AI briefings
   - [OpenWeatherMap](https://openweathermap.org/api) - Weather (free tier)
   - [NewsAPI](https://newsapi.org) - Headlines (free tier)
   - [Alpha Vantage](https://www.alphavantage.co/support/#api-key) - Stocks (free tier)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main dashboard |
| `GET /api/data` | All aggregated data |
| `GET /api/briefing` | AI-generated briefing |
| `GET /api/widget/:type` | Individual widget data |

## Tech Stack

- **Backend**: Python, Flask, aiohttp (async HTTP)
- **AI**: OpenAI GPT-3.5
- **APIs**: OpenWeatherMap, NewsAPI, Alpha Vantage, GitHub, Quotable
- **Frontend**: Vanilla JS with real-time updates

## Why This Matters

This project demonstrates:
1. **Multi-service integration** - Connecting 5+ external APIs
2. **Async programming** - Concurrent API calls for performance
3. **AI orchestration** - Using LLMs to synthesize data
4. **Graceful degradation** - Demo mode when APIs unavailable
5. **Real-time dashboards** - Live updating UI

---

*Aggregating intelligence, one API at a time.*
