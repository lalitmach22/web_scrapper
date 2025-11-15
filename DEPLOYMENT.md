# Deployment Guide 🚀

This guide covers multiple deployment options for your News Scraper with Sentiment Analysis.

## Table of Contents
1. [GitHub Deployment](#github-deployment)
2. [Local Server Deployment](#local-server-deployment)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [Heroku Deployment](#heroku-deployment)
5. [Python Anywhere Deployment](#pythonanywhere-deployment)
6. [Docker Deployment](#docker-deployment)

---

## 1. GitHub Deployment

### Initial Setup

1. **Initialize Git Repository**
   ```bash
   cd c:\Users\DELL\Documents\Vibe_coding
   git init
   ```

2. **Create GitHub Repository**
   - Go to https://github.com/new
   - Create a new repository (e.g., "news-sentiment-scraper")
   - Don't initialize with README (we already have one)

3. **Configure Git**
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

4. **Create config.py from template**
   ```bash
   copy config.py.template config.py
   # Edit config.py and add your API key
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Initial commit: News scraper with sentiment analysis"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/news-sentiment-scraper.git
   git push -u origin main
   ```

### Keep Your API Key Safe

**IMPORTANT:** Never commit `config.py` with your actual API key!

The `.gitignore` file already excludes `config.py`. Always use `config.py.template` in your repository.

---

## 2. Local Server Deployment

### Option A: Simple Python HTTP Server

```bash
# Start server
python -m http.server 8000

# Access dashboard at:
# http://localhost:8000/dashboard.html
```

### Option B: Flask Web App

Create `web_app.py`:

```python
from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return open('dashboard.html').read()

@app.route('/api/articles')
def get_articles():
    if os.path.exists('articles_historical.json'):
        with open('articles_historical.json') as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Install Flask:
```bash
pip install flask
```

Run:
```bash
python web_app.py
```

Access at: `http://localhost:5000`

---

## 3. Cloud Deployment Options

### Prerequisites

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m textblob.download_corpora
   ```

2. **Test locally first**
   ```bash
   python scrapper.py
   python dashboard.py
   ```

---

## 4. Heroku Deployment

### Setup

1. **Install Heroku CLI**
   Download from: https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create news-sentiment-scraper
   ```

4. **Create Procfile**
   Create `Procfile` (no extension):
   ```
   web: python -m http.server $PORT
   worker: python daily_scraper.py
   ```

5. **Create runtime.txt**
   ```
   python-3.12.0
   ```

6. **Set Environment Variables**
   ```bash
   heroku config:set NEWS_API_KEY=your_api_key_here
   ```

7. **Update config.py to use environment variables**
   ```python
   import os
   NEWS_API_KEY = os.environ.get('NEWS_API_KEY', 'YOUR_API_KEY_HERE')
   ```

8. **Deploy**
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```

9. **Set up Heroku Scheduler** (for daily runs)
   ```bash
   heroku addons:create scheduler:standard
   heroku addons:open scheduler
   ```
   Add job: `python daily_scraper.py` (Daily at 9:00 AM UTC)

---

## 5. PythonAnywhere Deployment

### Setup

1. **Create Account**
   - Go to https://www.pythonanywhere.com/
   - Sign up for free account

2. **Upload Files**
   - Use Files tab to upload your project
   - Or clone from GitHub

3. **Install Dependencies**
   ```bash
   pip3 install --user -r requirements.txt
   python3 -m textblob.download_corpora
   ```

4. **Set up Scheduled Task**
   - Go to "Tasks" tab
   - Add daily task: `python3 /home/yourusername/daily_scraper.py`
   - Set time: 09:00 UTC

5. **Set up Web App** (optional)
   - Create a new web app
   - Choose Flask
   - Configure WSGI file

---

## 6. Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m textblob.download_corpora

COPY . .

# Run scraper once on startup
CMD ["python", "daily_scraper.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  scraper:
    build: .
    environment:
      - NEWS_API_KEY=${NEWS_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Build and Run

```bash
# Build
docker build -t news-scraper .

# Run
docker run -e NEWS_API_KEY=your_key_here news-scraper

# Or with docker-compose
docker-compose up -d
```

### Schedule with Docker

Use cron or a scheduler service to run the container daily.

---

## 7. GitHub Actions (Automated Daily Runs)

Create `.github/workflows/daily-scraper.yml`:

```yaml
name: Daily News Scraper

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        python -m textblob.download_corpora
    
    - name: Run scraper
      env:
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
      run: python daily_scraper.py
    
    - name: Commit results
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add articles_historical.json articles_daily_*.json
        git commit -m "Daily scrape: $(date)" || exit 0
        git push
```

**Setup:**
1. Go to repository Settings → Secrets
2. Add `NEWS_API_KEY` secret
3. Enable GitHub Actions
4. Workflow runs automatically daily!

---

## 8. AWS Lambda (Serverless)

### Setup

1. **Create Lambda Function**
2. **Package dependencies**
   ```bash
   pip install -r requirements.txt -t package/
   cd package
   zip -r ../deployment-package.zip .
   cd ..
   zip -g deployment-package.zip *.py
   ```

3. **Upload to Lambda**
4. **Add EventBridge trigger** (daily schedule)

---

## Recommended Deployment Strategy

### For Personal Use:
- ✅ **Local + GitHub**: Run locally, push to GitHub for backup
- ✅ **Windows Task Scheduler**: Automated daily collection

### For Public Access:
- ✅ **GitHub + GitHub Pages**: Static dashboard
- ✅ **Heroku Free Tier**: Interactive web app
- ✅ **PythonAnywhere**: Easy Python hosting

### For Production:
- ✅ **GitHub Actions**: Automated, free, version controlled
- ✅ **AWS Lambda**: Serverless, scalable
- ✅ **Docker + Cloud**: Maximum control

---

## Post-Deployment Checklist

- [ ] API key stored securely (environment variable)
- [ ] .gitignore properly configured
- [ ] Requirements.txt up to date
- [ ] Daily scheduler configured
- [ ] Dashboard accessible
- [ ] Logs being written
- [ ] Historical data accumulating
- [ ] Backups configured

---

## Monitoring

### Check Logs
```bash
# Local
tail -f scraper_history.log

# Heroku
heroku logs --tail

# GitHub Actions
Check Actions tab in repository
```

### Verify Data Collection
```bash
# Check file sizes
ls -lh articles_*.json

# Count articles
python -c "import json; print(len(json.load(open('articles_historical.json'))))"
```

---

## Troubleshooting

### Issue: API Key Not Working
- Check environment variables are set
- Verify key is valid at newsapi.org

### Issue: No New Articles
- Check log files for errors
- Verify internet connection
- Check NewsAPI rate limits

### Issue: Dashboard Not Updating
- Regenerate dashboard: `python dashboard.py`
- Clear browser cache
- Check file permissions

---

## Support

For issues, please open an issue on GitHub or check the logs.

Happy Scraping! 🚀
