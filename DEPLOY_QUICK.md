# Quick Deployment Steps 🚀

## 1. Deploy to GitHub (Recommended First Step)

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `news-sentiment-scraper`
3. Description: `News scraper with sentiment analysis and historical data collection`
4. Make it Public or Private (your choice)
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Connect and Push
```bash
# Configure Git (replace with your info)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Commit your code
git commit -m "Initial commit: News scraper with sentiment analysis"

# Connect to GitHub (replace YOUR_USERNAME and REPO_NAME)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/news-sentiment-scraper.git
git push -u origin main
```

✅ **Your code is now on GitHub!**

---

## 2. Setup Local Automated Collection

Already done! Just run PowerShell as Administrator:

```powershell
.\setup_daily_task.ps1
```

This will run the scraper daily at 9:00 AM automatically.

---

## 3. Deploy Dashboard Online (Free Options)

### Option A: GitHub Pages (Easiest)

1. **Generate dashboard with historical data:**
   ```bash
   python dashboard.py
   ```

2. **Commit and push:**
   ```bash
   git add dashboard.html
   git commit -m "Add dashboard"
   git push
   ```

3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: main branch
   - Save

4. **Access your dashboard at:**
   `https://YOUR_USERNAME.github.io/news-sentiment-scraper/dashboard.html`

### Option B: Netlify (Simple Drag & Drop)

1. Go to https://app.netlify.com/drop
2. Drag and drop your `dashboard.html` file
3. Get instant URL!

---

## 4. Automated Cloud Collection (Free)

### GitHub Actions (Recommended)

1. **Create workflow file:**

Create `.github/workflows/daily-scraper.yml`:

```yaml
name: Daily News Scraper

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
  workflow_dispatch:

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
    
    - name: Copy config template
      run: |
        cp config.py.template config.py
        sed -i "s/YOUR_API_KEY_HERE/${{ secrets.NEWS_API_KEY }}/" config.py
    
    - name: Run scraper
      run: python daily_scraper.py
    
    - name: Generate dashboard
      run: python dashboard.py
    
    - name: Commit results
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add articles_historical.json articles_daily_*.json dashboard.html
        git commit -m "Auto-update: $(date)" || exit 0
        git push
```

2. **Add your API key as secret:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `NEWS_API_KEY`
   - Value: Your NewsAPI key
   - Click "Add secret"

3. **Enable Actions:**
   - Go to Actions tab
   - Enable workflows

✅ **Now runs automatically every day and commits results!**

---

## 5. Full Web Application (Optional)

### Heroku Deployment

```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-news-scraper

# Set API key
heroku config:set NEWS_API_KEY=your_actual_api_key

# Deploy
git push heroku main

# Set up daily scheduler
heroku addons:create scheduler:standard
heroku addons:open scheduler
# Add: python daily_scraper.py at 09:00 UTC
```

---

## Summary of Deployment Options

| Option | Cost | Difficulty | Best For |
|--------|------|------------|----------|
| **GitHub** | Free | Easy | Code backup & sharing |
| **Local + Task Scheduler** | Free | Easy | Personal use |
| **GitHub Pages** | Free | Very Easy | Static dashboard |
| **GitHub Actions** | Free | Medium | Automated collection |
| **Netlify** | Free | Very Easy | Quick dashboard hosting |
| **Heroku** | Free tier | Medium | Full web app |
| **PythonAnywhere** | Free tier | Easy | Python hosting |

---

## Recommended Setup

For best results, combine:

1. ✅ **GitHub** - Store your code
2. ✅ **Local Task Scheduler** - Collect data daily
3. ✅ **GitHub Actions** - Backup automation
4. ✅ **GitHub Pages** - Public dashboard

This gives you:
- 📦 Version control
- 🤖 Automated collection
- 📊 Public dashboard
- 💾 Data backup
- 💰 100% FREE!

---

## Next Steps

1. [ ] Push code to GitHub
2. [ ] Set up local Task Scheduler
3. [ ] Add GitHub Actions workflow
4. [ ] Enable GitHub Pages for dashboard
5. [ ] Let it collect data for a few days
6. [ ] Share your dashboard URL!

---

## Need Help?

Check `DEPLOYMENT.md` for detailed instructions on each option.

Happy deploying! 🎉
