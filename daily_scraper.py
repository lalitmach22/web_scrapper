import json
import os
from datetime import datetime
import logging
import config
from scrapper import scrape_with_newsapi, scrape_news_sources

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_history.log'),
        logging.StreamHandler()
    ]
)

# Historical data file
HISTORICAL_FILE = "articles_historical.json"

def load_historical_data():
    """
    Load existing historical data if it exists.
    """
    if os.path.exists(HISTORICAL_FILE):
        try:
            with open(HISTORICAL_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"Loaded {len(data)} existing articles from historical data")
                return data
        except Exception as e:
            logging.error(f"Error loading historical data: {e}")
            return []
    else:
        logging.info("No historical data file found. Starting fresh.")
        return []

def save_historical_data(articles):
    """
    Save articles to historical data file.
    """
    try:
        with open(HISTORICAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4)
        logging.info(f"Saved {len(articles)} articles to {HISTORICAL_FILE}")
    except Exception as e:
        logging.error(f"Error saving historical data: {e}")

def merge_articles(existing_articles, new_articles):
    """
    Merge new articles with existing ones, avoiding duplicates.
    """
    # Create a set of existing article links for fast lookup
    existing_links = {article['link'] for article in existing_articles}
    
    # Count duplicates
    duplicates = 0
    new_count = 0
    
    # Add only new articles
    for article in new_articles:
        if article['link'] not in existing_links:
            existing_articles.append(article)
            existing_links.add(article['link'])
            new_count += 1
        else:
            duplicates += 1
    
    logging.info(f"Added {new_count} new articles, skipped {duplicates} duplicates")
    return existing_articles

def sort_articles_by_date(articles):
    """
    Sort articles by publication date (newest first).
    """
    def get_date(article):
        try:
            pub_date = article.get('pubDate', '')
            if pub_date:
                # Handle both formats
                if 'T' in pub_date:  # ISO format from NewsAPI
                    return datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                else:  # RSS format
                    from email.utils import parsedate_to_datetime
                    return parsedate_to_datetime(pub_date)
        except:
            return datetime.min
        return datetime.min
    
    return sorted(articles, key=get_date, reverse=True)

def get_statistics(articles):
    """
    Get statistics about the historical data.
    """
    if not articles:
        return {}
    
    from collections import Counter
    
    # Date range
    dates = []
    for article in articles:
        try:
            pub_date = article.get('pubDate', '')
            if pub_date:
                if 'T' in pub_date:
                    date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                else:
                    from email.utils import parsedate_to_datetime
                    date_obj = parsedate_to_datetime(pub_date)
                dates.append(date_obj)
        except:
            pass
    
    stats = {
        'total_articles': len(articles),
        'sources': len(set(article['source'] for article in articles)),
        'oldest_article': min(dates).strftime('%Y-%m-%d') if dates else 'N/A',
        'newest_article': max(dates).strftime('%Y-%m-%d') if dates else 'N/A',
        'sentiment_distribution': Counter(article['sentiment']['label'] for article in articles),
        'top_sources': Counter(article['source'] for article in articles).most_common(5)
    }
    
    return stats

def run_daily_collection():
    """
    Main function to run daily article collection.
    """
    logging.info("=" * 60)
    logging.info(f"Starting daily collection at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    # Load existing historical data
    historical_articles = load_historical_data()
    initial_count = len(historical_articles)
    
    # Fetch new articles
    logging.info("\nFetching new articles...")
    if config.USE_NEWS_API:
        new_articles = scrape_with_newsapi()
    else:
        new_articles = scrape_news_sources()
    
    if not new_articles:
        logging.warning("No new articles fetched!")
        return
    
    # Merge with historical data
    logging.info("\nMerging with historical data...")
    historical_articles = merge_articles(historical_articles, new_articles)
    
    # Sort by date
    historical_articles = sort_articles_by_date(historical_articles)
    
    # Save updated historical data
    save_historical_data(historical_articles)
    
    # Save today's articles separately
    today_file = f"articles_daily_{datetime.now().strftime('%Y%m%d')}.json"
    with open(today_file, 'w', encoding='utf-8') as f:
        json.dump(new_articles, f, indent=4)
    logging.info(f"Saved today's {len(new_articles)} articles to {today_file}")
    
    # Display statistics
    logging.info("\n" + "=" * 60)
    logging.info("COLLECTION STATISTICS")
    logging.info("=" * 60)
    stats = get_statistics(historical_articles)
    
    logging.info(f"Total articles in database: {stats['total_articles']}")
    logging.info(f"New articles added today: {stats['total_articles'] - initial_count}")
    logging.info(f"Number of sources: {stats['sources']}")
    logging.info(f"Date range: {stats['oldest_article']} to {stats['newest_article']}")
    logging.info(f"\nSentiment distribution:")
    for sentiment, count in stats['sentiment_distribution'].items():
        logging.info(f"  {sentiment.capitalize()}: {count}")
    logging.info(f"\nTop 5 sources:")
    for source, count in stats['top_sources']:
        logging.info(f"  {source}: {count} articles")
    
    logging.info("\n" + "=" * 60)
    logging.info("Daily collection completed successfully!")
    logging.info("=" * 60)

if __name__ == "__main__":
    try:
        run_daily_collection()
    except Exception as e:
        logging.error(f"Error during daily collection: {e}")
        import traceback
        traceback.print_exc()
