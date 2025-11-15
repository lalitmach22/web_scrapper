# News Scraper with Sentiment Analysis 📰

A Python-based news scraper that fetches articles from multiple sources, performs sentiment analysis, and builds a historical database over time.

## Features

- 📰 **Multiple Data Sources**: 
  - RSS feeds (Reuters, BBC, Washington Post, CNN)
  - NewsAPI for recent data (last 30 days with free tier)
  - Historical database that grows over time
- 🎭 **Sentiment Analysis**: Analyzes polarity and subjectivity of articles
- 🔍 **Customizable Search**: Filter by keywords and date range
- 💾 **JSON Output**: Results saved in a structured format
- 📊 **Interactive Dashboard**: Visual analytics with charts and statistics
- 🤖 **Automated Daily Collection**: Build historical data automatically
- 📈 **Deduplication**: Automatically removes duplicate articles

## Setup

### 1. Install Dependencies

```bash
pip install --user requests beautifulsoup4 lxml pytz textblob
python -m textblob.download_corpora
```

### 2. Get NewsAPI Key (for historical articles)

1. Visit [https://newsapi.org/register](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your API key
4. Open `config.py` and replace `YOUR_API_KEY_HERE` with your actual API key

**Free tier limitations:**
- 100 requests per day
- Articles from last 30 days only
- 100 articles per request

**Note:** For truly historical data (beyond 30 days), you would need a paid NewsAPI plan or use other services.

### 3. Configure the Scraper

Edit `config.py`:

```python
# Set to True to use NewsAPI, False to use RSS feeds
USE_NEWS_API = True

# Your search query
SEARCH_QUERY = "India"

# Date range in years
DATE_RANGE_YEARS = 10
```

## Usage

### One-Time Scraping

Run the scraper once:

```bash
python scrapper.py
```

Results will be saved to `articles.json`.

### Daily Historical Collection

Build a historical database by running daily:

**Option 1: Manual**
```bash
python daily_scraper.py
```

Or double-click `run_daily_scraper.bat`

**Option 2: Automated (Windows Task Scheduler)**
```powershell
# Run PowerShell as Administrator, then:
.\setup_daily_task.ps1
```

This will automatically run the scraper daily at 9:00 AM.

### View Dashboard

Generate and view the dashboard:

```bash
python dashboard.py
```

Then open `dashboard.html` in your browser or navigate to `http://localhost:8000/dashboard.html`

### Files Generated

- `articles.json` - Latest scraping results
- `articles_historical.json` - Accumulated historical data
- `articles_daily_YYYYMMDD.json` - Daily snapshots
- `scraper_history.log` - Log of all scraper runs
- `dashboard.html` - Interactive visualization

## Output Format

Each article includes:

```json
{
    "source": "BBC News",
    "title": "Article title",
    "description": "Article description",
    "link": "https://...",
    "pubDate": "2025-11-15T10:04:06Z",
    "sentiment": {
        "polarity": -0.2,
        "subjectivity": 0.0,
        "label": "negative"
    }
}
```

### Sentiment Scores

- **Polarity**: -1 (very negative) to +1 (very positive)
- **Subjectivity**: 0 (objective) to 1 (subjective)
- **Label**: "positive", "negative", or "neutral"

## Configuration Options

### RSS Mode (USE_NEWS_API = False)
- Fetches latest articles from RSS feeds
- No API key required
- Limited to recent articles only

### NewsAPI Mode (USE_NEWS_API = True)
- Access to historical articles (up to 30 days with free tier)
- Larger article volume
- Requires API key

## Project Structure

```
Vibe_coding/
├── scrapper.py      # Main scraper logic
├── config.py        # Configuration settings
├── articles.json    # Output file (generated)
└── README.md        # This file
```

## Extending the Scraper

### Add More RSS Sources

Edit `NEWS_SOURCES` in `config.py`:

```python
NEWS_SOURCES = {
    "source_name": "https://rss-feed-url.xml",
}
```

### Add More NewsAPI Sources

Edit `NEWS_API_SOURCES` in `config.py`:

```python
NEWS_API_SOURCES = [
    "bbc-news",
    "cnn",
    # Add more from: https://newsapi.org/sources
]
```

## Troubleshooting

### "Import textblob could not be resolved"
Run: `pip install --user textblob`

### "NewsAPI key not configured"
Update `NEWS_API_KEY` in `config.py` with your actual API key

### No articles found
- Check your search query
- Verify the date range
- Ensure RSS feeds/API sources are accessible

## License

This project is for educational purposes.
