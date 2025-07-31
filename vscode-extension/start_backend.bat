@echo off
echo 🐾 Starting VoidCat VS Code Extension Backend Server...
echo ============================================================

cd /d "d:\03_Development\Active_Projects\voidcat-reasoning-core"

echo 🚀 Starting server on localhost:8003...
echo 📚 API Documentation will be available at: http://localhost:8003/docs
echo 🏥 Health Check: http://localhost:8003/health
echo ============================================================
echo Press Ctrl+C to stop the server
echo.

uvicorn api_gateway:app --host localhost --port 8003 --reload

pause