# PowerShell script to run the Mindmap Agent application

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
} elseif (Test-Path "..\venv\Scripts\Activate.ps1") {
    ..\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Please create it first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Change to app directory
Set-Location mindmap_agent\app

Write-Host ""
Write-Host "Starting Mindmap Agent on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Access the web interface at: http://localhost:8000/app" -ForegroundColor Cyan
Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
