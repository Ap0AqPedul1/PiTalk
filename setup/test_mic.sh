#!/bin/bash

echo "🎙️  Mendeteksi USB Microphone..."

# Ambil nomor card dari hasil arecord -l
mic_card=$(arecord -l | grep -i "usb" | head -n 1 | sed -n 's/card \([0-9]*\):.*/\1/p')

if [ -z "$mic_card" ]; then
    echo "❌ Microphone USB tidak ditemukan!"
    exit 1
fi

echo "✅ Ditemukan USB Microphone di card $mic_card"

# Tulis konfigurasi ke ~/.asoundrc
echo "⚙️  Mengatur ~/.asoundrc untuk input..."
cat > ~/.asoundrc <<EOF
defaults.pcm.card $mic_card
defaults.ctl.card $mic_card
EOF

echo "✅ Konfigurasi ~/.asoundrc selesai."

# Rekam 5 detik suara dan simpan ke mic_test.wav
echo "🎤 Merekam suara selama 5 detik..."
arecord -D plughw:$mic_card,0 -f cd -t wav -d 5 -r 44100 mic_test.wav

if [ -f mic_test.wav ]; then
    echo "🔊 Merekam selesai. Memutar hasil rekaman..."
    aplay mic_test.wav
else
    echo "❌ Rekaman gagal dibuat!"
fi

echo "✅ Tes mic selesai."
