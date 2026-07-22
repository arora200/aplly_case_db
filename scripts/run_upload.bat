@echo off
REM Plato the Archivist — Smart Upload Runner
REM Scheduled: Daily at 5:00 AM and 3:00 PM
REM Only runs Python if files have changed (checksum mismatch)

set SCRIPT_DIR=%~dp0
set CASES_DIR=%SCRIPT_DIR%..\case-studies-in
set CHECKSUMS=%SCRIPT_DIR%case_checksums.json
set LOG_DIR=%SCRIPT_DIR%logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

if not exist "%CHECKSUMS%" goto :run

set CHANGED=0
for %%f in ("%CASES_DIR%\*.md") do (
    for /f "usebackq tokens=*" %%a in (
        `powershell -NoProfile -Command "Get-FileHash '%%f' -Algorithm SHA256 | Select-Object -ExpandProperty Hash"`
    ) do (
        findstr /C:"%%~nxf" "%CHECKSUMS%" >nul || set CHANGED=1
    )
)

if "%CHANGED%"=="0" (
    echo [%date% %time%] No changes detected — skipping.
    exit /b 0
)

:run
echo [%date% %time%] Changes detected — running Plato upload...
python "%SCRIPT_DIR%\upload_case_studies.py" --publish >> "%LOG_DIR%\scheduler_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log" 2>&1
echo [%date% %time%] Plato check complete.
