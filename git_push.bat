@echo off
title Git Push Tool

echo ============================================
echo         Git Push Tool
echo ============================================
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found!
    echo.
    echo Please install Git:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

if not exist ".git" (
    echo [ERROR] Not a Git repo!
    echo.
    echo Please run git_setup.bat first.
    echo.
    pause
    exit /b 1
)

echo [OK] Checking files...
echo.
git status --short
echo.

echo ============================================
echo Ready to commit above files
echo ============================================
echo.

git add .

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set datetime=%%I
if defined datetime (
    set mydate=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
    set mytime=%datetime:~8,2%:%datetime:~10,2%
) else (
    set mydate=%date%
    set mytime=%time:~0,5%
)

set commitmsg=Update %mydate% %mytime%
echo Commit message: %commitmsg%
echo.

git commit -m "%commitmsg%"

if errorlevel 1 (
    echo.
    echo [INFO] No changes to commit or commit failed.
    echo.
    pause
    exit /b 0
)

echo.
echo Pushing to GitHub...
echo.

git push -u origin master 2>nul || git push -u origin main 2>nul || git push

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed!
    echo.
    echo Possible reasons:
    echo   1. Network issue - check your connection
    echo   2. First time - GitHub login window should appear
    echo   3. Wrong repo URL - run git_setup.bat again
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo [DONE] Push successful!
echo ============================================
echo.
echo Now send this link to Claude for analysis:
echo https://github.com/ZusyLu/learn
echo.
pause
