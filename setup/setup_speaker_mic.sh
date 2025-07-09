#!/bin/bash

# Cari card number dari USB Audio
card_num=$(aplay -l | grep -i "usb" | head -n 1 | sed -n 's/card \([0-9]*\):.*/\1/p')

if [ -z "$card_num" ]; then
    echo "Perangkat USB tidak ditemukan!"
    exit 1
fi

# Tampilkan card yang dipilih
echo "Mengatur ~/.asoundrc ke card $card_num"

# Tulis ke ~/.asoundrc
cat > ~/.asoundrc <<EOF
defaults.pcm.card $card_num
defaults.ctl.card $card_num
EOF

echo "Selesai! File ~/.asoundrc telah diperbarui."
