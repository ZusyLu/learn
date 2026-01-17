@echo off
title Git Setup Tool

echo ============================================
echo         Git First-Time Setup
echo ============================================
echo.
echo Run this script ONLY ONCE!
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found!
    echo.
    echo Please install Git first:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [OK] Git found
echo.

set /p username=Enter your GitHub username: 
git config --global user.name "%username%"

echo.
set /p email=Enter your GitHub email: 
git config --global user.email "%email%"

echo.
echo [OK] User info saved
echo.

if exist ".git" (
    echo [OK] Git repo already exists
    echo.
) else (
    echo Initializing Git repo...
    git init
    echo.
)

echo Enter your GitHub repo URL
echo Example: https://github.com/ZusyLu/learn.git
echo.
set /p repourl=URL: 

git remote -v 2>nul | findstr "origin" >nul 2>&1
if errorlevel 1 (
    git remote add origin %repourl%
) else (
    git remote set-url origin %repourl%
)

echo.
echo [OK] Remote repo configured
echo.

echo Syncing with remote repo...
git fetch origin 2>nul
git pull origin master --allow-unrelated-histories 2>nul
git pull origin main --allow-unrelated-histories 2>nul

echo.
echo ============================================
echo [DONE] Setup complete!
echo ============================================
echo.
echo Username: %username%
echo Email: %email%
echo Repo: %repourl%
echo.
echo Next steps:
echo   1. Fill in about_me.md and portfolio.md
echo   2. Run run_fetch.bat to get market data
echo   3. Run git_push.bat to upload files
echo.
pause
