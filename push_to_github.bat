@echo off
setlocal
echo =========================================================================
echo  THE INITIATIVE 2.0 - Push to GitHub Repository
echo =========================================================================
echo.
set "PATH=C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.6.4\resources\app\git\cmd;%PATH%"

set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/repo.git): "
if "%REPO_URL%"=="" (
    echo [ERROR] No repository URL entered. Exiting...
    pause
    exit /b 1
)

echo.
echo [1/3] Adding / Updating remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo [2/3] Verifying branch 'main'...
git branch -M main

echo.
echo [3/3] Pushing codebase to %REPO_URL%...
git push -u origin main --force

echo.
echo =========================================================================
echo  Upload complete! Check your repository on GitHub.
echo =========================================================================
pause
