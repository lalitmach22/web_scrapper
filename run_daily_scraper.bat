@echo off
REM Daily News Scraper - Manual Run
echo ========================================
echo Running Daily News Scraper
echo ========================================
echo.

cd /d "C:\Users\DELL\Documents\Vibe_coding"
"C:\ProgramData\anaconda3\python.exe" daily_scraper.py

echo.
echo ========================================
echo Scraper completed!
echo ========================================
pause
