@echo off
echo ========================================
echo Love Is Complicated - GitHub Setup
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
)

echo Adding files to Git...
git add .
echo.

echo Enter commit message (or press Enter for default):
set /p commit_msg="Commit message: "
if "%commit_msg%"=="" set commit_msg=Deploy Love Is Complicated challenge

echo.
echo Committing changes...
git commit -m "%commit_msg%"
echo.

echo Setting main branch...
git branch -M main
echo.

echo Enter your GitHub repository URL:
echo Example: https://github.com/username/love-is-complicated.git
set /p repo_url="Repository URL: "

if "%repo_url%"=="" (
    echo ERROR: Repository URL is required!
    pause
    exit /b 1
)

echo.
echo Adding remote origin...
git remote remove origin 2>nul
git remote add origin %repo_url%
echo.

echo Pushing to GitHub...
git push -u origin main
echo.

echo ========================================
echo SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Next steps:
echo 1. Go to render.com
echo 2. Click "New +" - "Web Service"
echo 3. Connect your GitHub repository
echo 4. Render will auto-detect render.yaml
echo 5. Click "Apply" to deploy
echo.
echo Your app will be live at:
echo https://love-is-complicated.onrender.com
echo.
pause
