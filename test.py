import socket
import sounddevice as sd
import numpy as np
import threading

UDP_IP = "192.168.0.105"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Server UDP berjalan di {UDP_IP}:{UDP_PORT}")

samplerate = 44100
channels = 1
dtype = 'int16'

# Simpan alamat terakhir masing-masing klien untuk relay
clients = {}

def audio_playback():
    with sd.OutputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while True:
            if 'audio_buffer' in globals():
                if audio_buffer.size > 0:
                    stream.write(audio_buffer.copy())
                    # Kosongkan buffer setelah diputar
                    audio_buffer.resize(0)

# Buffer untuk audio yang akan diputar lokal di server (opsional)
audio_buffer = np.array([], dtype=dtype)

def server_loop():
    global audio_buffer
    while True:
        data, addr = sock.recvfrom(65535)
        # Simpan alamat klien jika belum ada
        if addr not in clients.values():
            if len(clients) < 2:
                # Simpan alamat unik clients
                clients[len(clients)] = addr
                print(f"Klien baru terdaftar: {addr}")

        # Set audio buffer untuk diputar di server
        new_audio = np.frombuffer(data, dtype=dtype)
        if audio_buffer.size == 0:
            audio_buffer = new_audio
        else:
            # Gabungkan potongan audio jika buffer belum kosong
            audio_buffer = np.concatenate((audio_buffer, new_audio))

        # Relay audio ke client lain
        # Cari klien receiver yang bukan sender
        for c_id, c_addr in clients.items():
            if c_addr != addr:
                sock.sendto(data, c_addr)
                print(f"Meneruskan data audio dari {addr} ke {c_addr}")

if __name__ == '__main__':
    threading.Thread(target=audio_playback, daemon=True).start()
    server_loop()
