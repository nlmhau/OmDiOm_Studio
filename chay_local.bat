@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   OmDiOm Studio - HE THONG TONG HOP GIONG NOI TIENG VIET
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [X] Khong tim thay python. Vui long cai Python 3.10+ roi chay lai.
  pause
  exit /b 1
)

set OMDIOM_MOCK=0
set OMDIOM_API_KEY=testkey
set OMDIOM_PRELOAD=1
set OMDIOM_VOICES=%cd%\voices
set PYTHONIOENCODING=utf-8

echo [1/2] Thu vien giong doc cuc bo: %OMDIOM_VOICES%
if exist "%OMDIOM_VOICES%\*.pt" (
  for %%f in ("%OMDIOM_VOICES%\*.pt") do echo       - %%~nxf
) else (
  echo       [i] San sang nhan dang giong doc tu voices\
)

echo.
echo [2/2] Dang khoi dong may chu OmDiOm Backend...
echo   Dia chi : http://127.0.0.1:8000
echo   API key : testkey
echo   Giao dien: Mo file UI\index.html tren trinh duyet
echo ============================================================
echo.

cd server
python -m uvicorn app:app --host 127.0.0.1 --port 8000
