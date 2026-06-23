@echo off
REM Start full stack with Docker Compose
cd /d "%~dp0"
if not exist .env (
    copy .env.example .env
    echo Created .env from template. Edit POSTGRES_PASSWORD before production use.
)
docker compose up --build -d
echo.
echo Frontend: http://localhost
echo API:      http://localhost:8000/docs
pause
