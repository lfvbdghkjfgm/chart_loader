@echo off
setlocal enabledelayedexpansion

echo.
echo =====================================================
echo   CHART LOADER - Installation Wizard
echo =====================================================
echo.

REM Check for admin privileges (required for Program Files + system PATH)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Administrator privileges required
    echo Please run this installer as Administrator.
    echo.
    pause
    exit /b 1
)

set "DEFAULT_REPO_ZIP_URL=https://github.com/lfvbdghkjfgm/chart_loader/archive/refs/heads/main.zip"
set "REPO_ZIP_URL=%DEFAULT_REPO_ZIP_URL%"
if not "%CHART_LOADER_REPO_ZIP_URL%"=="" set "REPO_ZIP_URL=%CHART_LOADER_REPO_ZIP_URL%"
set "REMOTE_TMP_DIR="
set "REMOTE_ZIP="
set "REMOTE_BASE_DIR="
set "SRC_PATH="

set "INSTALL_ROOT=%ProgramFiles%\ChartLoader"
set "INSTALL_PATH=!INSTALL_ROOT!\current"
set "RUN_TARGET=!INSTALL_PATH!\ChartLoader.bat"
set "COMMAND_NAME=chart-loader"
set "COMMAND_PATH=!INSTALL_PATH!\!COMMAND_NAME!.bat"

echo Installation details:
echo   Source URL: !REPO_ZIP_URL!
echo   Target: !INSTALL_PATH!
echo   Command: !COMMAND_NAME!
echo.
set /p CONFIRM="Continue install/reinstall? (Y/N): "
if /i "!CONFIRM!"=="n" (
    echo Installation cancelled.
    call :CLEANUP_REMOTE
    pause
    exit /b 0
)
if /i "!CONFIRM!"=="no" (
    echo Installation cancelled.
    call :CLEANUP_REMOTE
    pause
    exit /b 0
)

echo.
echo Downloading required files from internet...
call :FETCH_REMOTE_REPO
if errorlevel 1 (
    echo Error: Failed to download or prepare repository files.
    echo You can override source URL via CHART_LOADER_REPO_ZIP_URL.
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)
set "SRC_PATH=!REMOTE_BASE_DIR!\src"

if not exist "!SRC_PATH!\main.py" (
    echo Error: source entry point not found:
    echo !SRC_PATH!\main.py
    echo.
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

echo.
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Install Python 3.8+ and run installer again.
    echo.
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

echo Preparing installation directory...
if exist "!INSTALL_PATH!" (
    rmdir /s /q "!INSTALL_PATH!" >nul 2>&1
    if exist "!INSTALL_PATH!" (
        echo Error: Failed to clean existing installation directory:
        echo !INSTALL_PATH!
        echo.
        call :CLEANUP_REMOTE
        pause
        exit /b 1
    )
)
mkdir "!INSTALL_PATH!"
if errorlevel 1 (
    echo Error: Failed to create installation directory.
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

echo Copying source files...
xcopy "!SRC_PATH!\*" "!INSTALL_PATH!\source\" /E /I /Y >nul
if errorlevel 1 (
    echo Error: Failed to copy source files.
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv "!INSTALL_PATH!\venv"
if errorlevel 1 (
    echo Error: Failed to create virtual environment.
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

if exist "!INSTALL_PATH!\source\requirements.txt" (
    echo Installing dependencies...
    "!INSTALL_PATH!\venv\Scripts\python.exe" -m pip install --progress-bar on -r "!INSTALL_PATH!\source\requirements.txt"
    if errorlevel 1 (
        echo Error: Failed to install dependencies.
        call :CLEANUP_REMOTE
        pause
        exit /b 1
    )
) else (
    echo Warning: requirements.txt not found, dependency installation skipped.
)

echo Creating local launcher...
(
    echo @echo off
    echo setlocal
    echo set "ROOT_DIR=%%~dp0"
    echo if "%%ROOT_DIR:~-1%%"=="\" set "ROOT_DIR=%%ROOT_DIR:~0,-1%%"
    echo set "PY_EXE=%%ROOT_DIR%%\venv\Scripts\python.exe"
    echo set "SRC_DIR=%%ROOT_DIR%%\source"
    echo if not exist "%%PY_EXE%%" ^(
    echo   echo Error: Python runtime not found: %%PY_EXE%%
    echo   endlocal ^& exit /b 1
    echo ^)
    echo if not exist "%%SRC_DIR%%\main.py" ^(
    echo   echo Error: main.py not found in %%SRC_DIR%%
    echo   endlocal ^& exit /b 1
    echo ^)
    echo "%%PY_EXE%%" "%%SRC_DIR%%\main.py" %%*
    echo set "EXIT_CODE=%%ERRORLEVEL%%"
    echo endlocal ^& exit /b %%EXIT_CODE%%
) > "!RUN_TARGET!"
if errorlevel 1 (
    echo Error: Failed to create launcher:
    echo !RUN_TARGET!
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

echo Creating global command: !COMMAND_NAME!
(
    echo @echo off
    echo call "%%~dp0ChartLoader.bat" %%*
    echo exit /b %%ERRORLEVEL%%
) > "!COMMAND_PATH!"
if errorlevel 1 (
    echo Error: Failed to create command launcher:
    echo !COMMAND_PATH!
    call :CLEANUP_REMOTE
    pause
    exit /b 1
)

echo Updating system PATH...
call :ADD_TO_SYSTEM_PATH "!INSTALL_PATH!"
if errorlevel 1 (
    echo Warning: Failed to update system PATH automatically.
    echo Add this path manually to PATH:
    echo !INSTALL_PATH!
) else (
    set "PATH=!INSTALL_PATH!;!PATH!"
    echo PATH updated. Open a new console to use the command globally.
)

echo Creating uninstaller...
call :WRITE_UNINSTALLER "!INSTALL_PATH!"
if errorlevel 1 (
    echo Warning: Failed to create uninstall.bat
)

echo.
echo =====================================================
echo   Installation Complete
echo =====================================================
echo.
echo Command:
echo   !COMMAND_NAME!
echo.
echo Install path:
echo   !INSTALL_PATH!
echo.
echo To uninstall:
echo   "!INSTALL_PATH!\uninstall.bat"
echo.
call :CLEANUP_REMOTE
pause
exit /b 0

:FETCH_REMOTE_REPO
set "REMOTE_TMP_DIR=%TEMP%\chart_loader_repo_%RANDOM%_%RANDOM%"
set "REMOTE_ZIP=%TEMP%\chart_loader_repo_%RANDOM%_%RANDOM%.zip"
if exist "!REMOTE_TMP_DIR!" rmdir /s /q "!REMOTE_TMP_DIR!" >nul 2>&1
if exist "!REMOTE_ZIP!" del /f /q "!REMOTE_ZIP!" >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "Invoke-WebRequest -Uri '!REPO_ZIP_URL!' -OutFile '!REMOTE_ZIP!';" ^
  "Expand-Archive -Path '!REMOTE_ZIP!' -DestinationPath '!REMOTE_TMP_DIR!' -Force"
if errorlevel 1 exit /b 1

set "REMOTE_BASE_DIR="
for /d %%D in ("!REMOTE_TMP_DIR!\*") do (
    if not defined REMOTE_BASE_DIR set "REMOTE_BASE_DIR=%%~fD"
)
if not defined REMOTE_BASE_DIR exit /b 1
if not exist "!REMOTE_BASE_DIR!\src" exit /b 1
if not exist "!REMOTE_BASE_DIR!\src\main.py" exit /b 1
exit /b 0

:CLEANUP_REMOTE
if defined REMOTE_ZIP if exist "!REMOTE_ZIP!" del /f /q "!REMOTE_ZIP!" >nul 2>&1
if defined REMOTE_TMP_DIR if exist "!REMOTE_TMP_DIR!" rmdir /s /q "!REMOTE_TMP_DIR!" >nul 2>&1
exit /b 0

:ADD_TO_SYSTEM_PATH
set "PATH_ENTRY=%~1"
if "%PATH_ENTRY%"=="" exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$entry='%PATH_ENTRY%';" ^
  "$existing=[Environment]::GetEnvironmentVariable('Path','Machine');" ^
  "if(-not $existing){$existing=''};" ^
  "$items=$existing -split ';' | Where-Object { $_ -and ($_ -ne $entry) };" ^
  "$updated=((@($entry)+$items) -join ';');" ^
  "[Environment]::SetEnvironmentVariable('Path',$updated,'Machine');"
if errorlevel 1 exit /b 1
exit /b 0

:WRITE_UNINSTALLER
set "UNINSTALL_DIR=%~1"
if not exist "%UNINSTALL_DIR%" exit /b 1
(
    echo @echo off
    echo setlocal
    echo net session ^>nul 2^>^&1
    echo if %%errorlevel%% neq 0 ^(
    echo   echo Error: Administrator privileges required
    echo   echo Please run uninstall.bat as Administrator.
    echo   pause
    echo   exit /b 1
    echo ^)
    echo set "TARGET_DIR=%%~dp0"
    echo if "%%TARGET_DIR:~-1%%"=="\" set "TARGET_DIR=%%TARGET_DIR:~0,-1%%"
    echo echo Removing PATH entry: %%TARGET_DIR%%
    echo powershell -NoProfile -ExecutionPolicy Bypass -Command "$target='%%TARGET_DIR%%'; $existing=[Environment]::GetEnvironmentVariable('Path','Machine'); if($existing){ $items=@(); foreach($p in ($existing -split ';')){ if($p -and ($p -ne $target)){ $items += $p } }; [Environment]::SetEnvironmentVariable('Path', ($items -join ';'), 'Machine') }"
    echo echo Removing files...
    echo set "TMP_CMD=%%TEMP%%\chart_loader_uninstall_%%RANDOM%%.cmd"
    echo ^> "%%TMP_CMD%%" echo @echo off
    echo ^>^> "%%TMP_CMD%%" echo timeout /t 2 /nobreak ^^^^>nul
    echo ^>^> "%%TMP_CMD%%" echo rmdir /s /q "%%TARGET_DIR%%"
    echo ^>^> "%%TMP_CMD%%" echo del /f /q "%%TMP_CMD%%" ^^^^>nul 2^^^^>^^^^^&1
    echo start "" cmd /c "%%TMP_CMD%%"
    echo echo Uninstallation started. This window can be closed.
    echo exit /b 0
) > "%UNINSTALL_DIR%\uninstall.bat"
exit /b 0
