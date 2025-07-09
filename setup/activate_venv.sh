#!/bin/bash

# Nama folder virtual environment
VENV_DIR="venv"

# Cek apakah folder venv ada
if [ ! -d "$VENV_DIR" ]; then
    echo "Folder virtual environment '$VENV_DIR' tidak ditemukan!"
    echo "Silakan buat terlebih dahulu dengan script create_venv.sh"
    exit 1
fi

# Aktifkan virtual environment
echo "Mengaktifkan virtual environment..."
source "$VENV_DIR/bin/activate"

# Cek apakah aktivasi berhasil (cek $VIRTUAL_ENV)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Gagal mengaktifkan virtual environment."
    exit 1
else
    echo "Virtual environment aktif: $VIRTUAL_ENV"
fi
