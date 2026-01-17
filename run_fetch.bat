@echo off
title Stock Data Fetcher

echo ============================================
echo         Stock Data Fetcher
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python first:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" when installing!
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.
echo Running script, please wait...
echo First run may take 1-2 minutes to install packages.
echo.

python "%~dp0fetch_market.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Script failed. Check error message above.
    echo.
)

pause
