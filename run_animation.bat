@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if not errorlevel 1 (
    python launcher.py %*
) else (
    where py >nul 2>nul
    if errorlevel 1 (
        echo Python 3.10+ is required for the launcher. Install Python or run Blender with --python main.py.
        pause
        exit /b 1
    )
    py -3 launcher.py %*
)
if errorlevel 1 pause
endlocal
