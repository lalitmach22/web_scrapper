import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import json
import logging
from textblob import TextBlob
import sys
import os

# Add current directory to path to ensure local config is imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_within_date_range(pub_date_str):
    """
    Checks if an article's publication date is within the last 12 years.
    """
    if not pub_date_str:
        return False
        
    try:
        pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        try:
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')
        except ValueError:
            logging.warning(f"Could not parse date: {pub_date_str}")
            return False

    if pub_date.tzinfo is None:
        pub_date = pub_date.replace(tzinfo=pytz.UTC)
        
    twelve_years_ago = datetime.now(pub_date.tzinfo) - timedelta(days=365 * config.DATE_RANGE_YEARS)
    
    return pub_date > twelve_years_ago

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using TextBlob.
    Returns a dictionary with polarity and subjectivity scores.
    
    Polarity: ranges from -1 (negative) to 1 (positive)
    Subjectivity: ranges from 0 (objective) to 1 (subjective)
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Categorize sentiment
    if polarity > 0.1:
        sentiment_label = "positive"
    elif polarity < -0.1:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    return {
        "polarity": round(polarity, 3),
        "subjectivity": round(subjectivity, 3),
        "label": sentiment_label
    }

def scrape_with_newsapi():
    """
    Fetches articles using NewsAPI for historical data access with pagination.
    """
    if not config.NEWS_API_KEY or config.NEWS_API_KEY == "YOUR_API_KEY_HERE":
        logging.error("NewsAPI key not configured. Please set NEWS_API_KEY in config.py")
        logging.info("Get your free API key from: https://newsapi.org/register")
        return []
    
    all_articles = []
    logging.info("Fetching articles from NewsAPI...")
    
    # Calculate date range - Free tier only allows 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=min(30, 365 * config.DATE_RANGE_YEARS))
    
    # Format dates for API (YYYY-MM-DD)
    from_date = start_date.strftime('%Y-%m-%d')
    to_date = end_date.strftime('%Y-%m-%d')
    
    logging.info(f"Searching from {from_date} to {to_date} (Note: Free tier limited to 30 days)")
    if config.DATE_RANGE_YEARS > 1/12:  # More than 1 month
        logging.warning(f"Requested {config.DATE_RANGE_YEARS} years, but free tier only allows 30 days")
    
    # NewsAPI endpoint
    url = "https://newsapi.org/v2/everything"
    
    # Calculate number of pages needed
    page_size = 100  # Max per request
    max_articles = getattr(config, 'MAX_ARTICLES', 300)
    total_pages = min(3, (max_articles + page_size - 1) // page_size)  # Max 3 pages to avoid rate limits
    
    for page in range(1, total_pages + 1):
        logging.info(f"Fetching page {page}/{total_pages}...")
        
        params = {
            'q': config.SEARCH_QUERY,
            'domains': getattr(config, 'NEWS_API_DOMAINS', None),
            'from': from_date,
            'to': to_date,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': page_size,
            'page': page,
            'apiKey': config.NEWS_API_KEY
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'ok':
                if page == 1:
                    logging.info(f"Total available: {data['totalResults']} articles")
                    logging.info(f"Will fetch up to {max_articles} articles")
                
                articles_in_page = len(data['articles'])
                logging.info(f"Retrieved {articles_in_page} articles from page {page}")
                
                if articles_in_page == 0:
                    logging.info("No more articles available")
                    break
                
                for article in data['articles']:
                    title = article.get('title', '')
                    description = article.get('description', '')
                    
                    # Skip if already added (deduplication)
                    if any(a['link'] == article.get('url', '') for a in all_articles):
                        continue
                    
                    # Analyze sentiment on title (or title + description)
                    text_to_analyze = f"{title}. {description}" if description else title
                    sentiment = analyze_sentiment(text_to_analyze)
                    
                    all_articles.append({
                        'source': article['source']['name'],
                        'title': title,
                        'description': description,
                        'link': article.get('url', ''),
                        'pubDate': article.get('publishedAt', ''),
                        'author': article.get('author', ''),
                        'sentiment': sentiment
                    })
                    
                    if len(all_articles) >= max_articles:
                        logging.info(f"Reached maximum of {max_articles} articles")
                        break
                
                if len(all_articles) >= max_articles:
                    break
                    
            else:
                logging.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                break
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching from NewsAPI: {e}")
            break
    
    logging.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles

def scrape_news_sources():
    """
    Scrapes articles from the configured RSS feeds, filters them, and saves them to a JSON file.
    """
    articles = []
    logging.info("Starting scraper...")
    for source_name, rss_url in config.NEWS_SOURCES.items():
        logging.info(f"Scraping {source_name}...")
        try:
            response = requests.get(rss_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching RSS feed from {rss_url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        
        for item in items:
            title = item.find('title').text
            link = item.find('link').text if item.find('link') else ''
            pub_date_str = item.find('pubDate').text if item.find('pubDate') else None
            
            if config.SEARCH_QUERY.lower() in title.lower() and is_within_date_range(pub_date_str):
                # Perform sentiment analysis on the title
                sentiment = analyze_sentiment(title)
                
                articles.append({
                    'source': source_name,
                    'title': title,
                    'link': link,
                    'pubDate': pub_date_str,
                    'sentiment': sentiment
                })
    
    return articles

def save_articles(articles):
    """
    Saves articles to JSON file.
    """
    with open(config.OUTPUT_FILE, 'w') as f:
        json.dump(articles, f, indent=4)
        
    logging.info(f"Scraped {len(articles)} articles and saved them to {config.OUTPUT_FILE}")
    logging.info("Scraper finished.")

if __name__ == "__main__":
    if config.USE_NEWS_API:
        articles = scrape_with_newsapi()
    else:
        articles = scrape_news_sources()
    
    save_articles(articles)
