@echo off
tasklist /FI "WINDOWTITLE eq trigger.py" 2>NUL | find /I /N "trigger.py">NUL
if "%ERRORLEVEL%"=="1" (
    echo Python script is not running. Starting it now...
    python D:\Price_Transparency_work\trigger.py
) else (
    echo Python script is already running.
)
