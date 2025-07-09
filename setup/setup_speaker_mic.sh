#!/bin/bash

echo "🔍 Mendeteksi USB Sound Card..."

# Ambil nomor card pertama yang mengandung kata 'usb'
card_num=$(aplay -l | grep -i "usb" | head -n 1 | sed -n 's/card \([0-9]*\):.*/\1/p')

if [ -z "$card_num" ]; then
    echo "❌ USB soundcard tidak ditemukan!"
    exit 1
fi

echo "✅ Ditemukan USB soundcard di card $card_num"

# Tulis konfigurasi ke ~/.asoundrc
echo "⚙️  Mengatur ~/.asoundrc..."
cat > ~/.asoundrc <<EOF
defaults.pcm.card $card_num
defaults.ctl.card $card_num
EOF

echo "✅ Konfigurasi ~/.asoundrc selesai."

# Tes suara
if [ -f "test.wav" ]; then
    echo "🔊 Memutar test.wav..."
    aplay test.wav
else
    echo "⚠️  test.wav tidak ditemukan. Menggunakan speaker-test sebagai alternatif."
    speaker-test -t sine -f 440 -l 1
fi

echo "✅ Tes selesai."
