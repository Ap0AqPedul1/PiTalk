#!/bin/bash

# Nama folder virtual environment
VENV_DIR="venv"

# Cek apakah Python tersedia
if ! command -v python3 &> /dev/null; then
    echo "Python3 tidak ditemukan. Pastikan sudah diinstal dan tersedia di PATH."
    exit 1
fi

# Membuat virtual environment
echo "Membuat virtual environment di folder '$VENV_DIR'..."
python3 -m venv "$VENV_DIR"

# Mengaktifkan virtual environment
echo "Mengaktifkan virtual environment..."
source "$VENV_DIR/bin/activate"

# Memastikan pip terbaru
echo "Mengupdate pip..."
pip install --upgrade pip

echo "Virtual environment berhasil dibuat dan diaktifkan."
