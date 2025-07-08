#!/bin/bash

VENV_DIR="venv"

# Cek Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 tidak ditemukan. Pastikan Python sudah terinstal."
    exit 1
fi

# Buat venv
echo "Membuat virtual environment di folder '$VENV_DIR'..."
python3 -m venv "$VENV_DIR"

# Aktifkan venv
source "$VENV_DIR/bin/activate"
echo "Virtual environment diaktifkan."

# Cek dan tanya untuk install requirements
if [ -f "requirements.txt" ]; then
    read -p "requirements.txt ditemukan. Install dependensi? (y/n): " jawab
    if [[ "$jawab" == "y" || "$jawab" == "Y" ]]; then
        pip install -r requirements.txt
        echo "Dependensi berhasil diinstal."
    else
        echo "Instalasi requirements dibatalkan."
    fi
else
    echo "Tidak ada file requirements.txt"
fi

echo "Selesai."