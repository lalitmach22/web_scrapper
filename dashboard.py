import json
import config
from collections import Counter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_dashboard():
    """
    Generates an interactive HTML dashboard with news statistics and sentiment analysis.
    """
    try:
        with open(config.OUTPUT_FILE, 'r') as f:
            articles = json.load(f)
    except FileNotFoundError:
        logging.error(f"File {config.OUTPUT_FILE} not found. Please run scrapper.py first.")
        return
    
    if not articles:
        logging.warning("No articles found in the file.")
        return
    
    # Analyze data
    total_articles = len(articles)
    
    # Count by source
    source_counts = Counter(article['source'] for article in articles)
    
    # Count by sentiment
    sentiment_counts = Counter(article['sentiment']['label'] for article in articles)
    
    # Calculate average sentiment scores
    avg_polarity = sum(article['sentiment']['polarity'] for article in articles) / total_articles
    avg_subjectivity = sum(article['sentiment']['subjectivity'] for article in articles) / total_articles
    
    # Get top sources
    top_sources = source_counts.most_common(10)
    
    # Prepare data for charts
    source_names = [source for source, _ in top_sources]
    source_values = [count for _, count in top_sources]
    
    sentiment_labels = list(sentiment_counts.keys())
    sentiment_values = list(sentiment_counts.values())
    
    # Sentiment distribution by source
    source_sentiment = {}
    for article in articles:
        source = article['source']
        sentiment = article['sentiment']['label']
        if source not in source_sentiment:
            source_sentiment[source] = {'positive': 0, 'negative': 0, 'neutral': 0}
        source_sentiment[source][sentiment] += 1
    
    # Generate HTML Dashboard
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Sentiment Dashboard - {config.SEARCH_QUERY}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.2em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}
        
        .articles-table {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .sentiment-positive {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .sentiment-negative {{
            color: #ef4444;
            font-weight: bold;
        }}
        
        .sentiment-neutral {{
            color: #6b7280;
            font-weight: bold;
        }}
        
        .article-link {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .article-link:hover {{
            text-decoration: underline;
        }}
        
        footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 News Sentiment Dashboard</h1>
            <p class="subtitle">Analysis of "{config.SEARCH_QUERY}" articles</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Articles</div>
                <div class="stat-number">{total_articles}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">News Sources</div>
                <div class="stat-number">{len(source_counts)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Polarity</div>
                <div class="stat-number">{avg_polarity:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Subjectivity</div>
                <div class="stat-number">{avg_subjectivity:.3f}</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <h3 class="chart-title">Articles by News Source</h3>
                <div class="chart-wrapper">
                    <canvas id="sourceChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h3 class="chart-title">Sentiment Distribution</h3>
                <div class="chart-wrapper">
                    <canvas id="sentimentChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3 class="chart-title">Sentiment Polarity Distribution</h3>
            <div class="chart-wrapper">
                <canvas id="polarityChart"></canvas>
            </div>
        </div>
        
        <div class="articles-table">
            <h3 class="chart-title">Recent Articles</h3>
            <table>
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Title</th>
                        <th>Date</th>
                        <th>Sentiment</th>
                        <th>Polarity</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add article rows (first 20)
    for article in articles[:20]:
        sentiment_class = f"sentiment-{article['sentiment']['label']}"
        pub_date = article.get('pubDate', 'N/A')[:10]  # Just the date part
        
        html_content += f"""
                    <tr>
                        <td>{article['source']}</td>
                        <td><a href="{article['link']}" target="_blank" class="article-link">{article['title'][:100]}...</a></td>
                        <td>{pub_date}</td>
                        <td class="{sentiment_class}">{article['sentiment']['label'].upper()}</td>
                        <td>{article['sentiment']['polarity']:.3f}</td>
                    </tr>
"""
    
    html_content += f"""
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated from {config.OUTPUT_FILE} | Total Articles Analyzed: {total_articles}</p>
            <p>Search Query: "{config.SEARCH_QUERY}" | Date Range: Last {config.DATE_RANGE_YEARS} years</p>
        </footer>
    </div>
    
    <script>
        // Source Chart
        const sourceCtx = document.getElementById('sourceChart').getContext('2d');
        new Chart(sourceCtx, {{
            type: 'bar',
            data: {{
                labels: {source_names},
                datasets: [{{
                    label: 'Number of Articles',
                    data: {source_values},
                    backgroundColor: 'rgba(102, 126, 234, 0.7)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Sentiment Chart
        const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(sentimentCtx, {{
            type: 'doughnut',
            data: {{
                labels: {sentiment_labels},
                datasets: [{{
                    data: {sentiment_values},
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(107, 114, 128, 0.7)'
                    ],
                    borderColor: [
                        'rgba(16, 185, 129, 1)',
                        'rgba(239, 68, 68, 1)',
                        'rgba(107, 114, 128, 1)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Polarity Distribution Chart
        const polarityCtx = document.getElementById('polarityChart').getContext('2d');
        const polarityData = {[article['sentiment']['polarity'] for article in articles]};
        
        // Create histogram bins
        const bins = {{}};
        polarityData.forEach(value => {{
            const bin = Math.round(value * 10) / 10;
            bins[bin] = (bins[bin] || 0) + 1;
        }});
        
        const binLabels = Object.keys(bins).sort((a, b) => a - b);
        const binValues = binLabels.map(label => bins[label]);
        
        new Chart(polarityCtx, {{
            type: 'bar',
            data: {{
                labels: binLabels,
                datasets: [{{
                    label: 'Article Count',
                    data: binValues,
                    backgroundColor: 'rgba(118, 75, 162, 0.7)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Polarity Score (-1 to +1)'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Save dashboard
    dashboard_file = "dashboard.html"
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logging.info(f"Dashboard generated successfully: {dashboard_file}")
    logging.info(f"Open {dashboard_file} in your browser to view the dashboard")
    
    return dashboard_file

if __name__ == "__main__":
    generate_dashboard()
