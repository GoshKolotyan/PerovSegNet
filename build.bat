@echo off
REM Build script for PerovSegNet Desktop Application (Windows)
REM This ensures the virtual environment is used

echo ==================================
echo Building PerovSegNet Desktop App
echo ==================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please create it first: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install project dependencies
echo Installing/updating project dependencies...
pip install -e . >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Dependencies installed
) else (
    echo [WARNING] Could not install dependencies
)

REM Verify PyInstaller is installed
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo.
echo Building executable...
echo (This may take 1-2 minutes)
echo.
pyinstaller PerovSegNet.spec

REM Check if build succeeded
if exist "dist\PerovSegNet.exe" (
    echo.
    echo ==================================
    echo [OK] Build completed successfully!
    echo ==================================
    echo.
    echo Executable location: dist\PerovSegNet.exe
    for %%A in (dist\PerovSegNet.exe) do echo Size: %%~zA bytes
    echo.
    echo To test it, run:
    echo   dist\PerovSegNet.exe
    echo.
) else (
    echo.
    echo [ERROR] Build failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)

pause
