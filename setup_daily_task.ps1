# Daily News Scraper - Windows Task Scheduler Setup
# This script sets up automatic daily execution

$taskName = "DailyNewsScraper"
$scriptPath = "C:\Users\DELL\Documents\Vibe_coding\daily_scraper.py"
$pythonPath = "C:\ProgramData\anaconda3\python.exe"
$workingDir = "C:\Users\DELL\Documents\Vibe_coding"

# Create the action (what to run)
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $workingDir

# Create the trigger (when to run) - Daily at 9:00 AM
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily news scraper to accumulate historical data" -Force
    Write-Host "✓ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "  Task name: $taskName" -ForegroundColor Cyan
    Write-Host "  Schedule: Daily at 9:00 AM" -ForegroundColor Cyan
    Write-Host "  Script: $scriptPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can view/modify this task in Task Scheduler (taskschd.msc)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To run manually now, use:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "To remove the task, use:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor White
}
catch {
    Write-Host "✗ Error creating scheduled task: $_" -ForegroundColor Red
    Write-Host "You may need to run PowerShell as Administrator" -ForegroundColor Yellow
}
