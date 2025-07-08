@echo off
set VENV_DIR=venv

REM Cek apakah Python tersedia
where python >nul 2>nul
if errorlevel 1 (
    echo Python tidak ditemukan. Pastikan sudah diinstal dan ditambahkan ke PATH.
    exit /b 1
)

REM Buat virtual environment
python -m venv %VENV_DIR%

REM Info sukses
echo Virtual environment telah dibuat di folder "%VENV_DIR%"
echo Aktifkan dengan perintah berikut:
echo %VENV_DIR%\Scripts\activate.bat