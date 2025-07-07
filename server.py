import socket
import sounddevice as sd
import numpy as np
import threading

# === KONFIGURASI ===
# GANTI nilai-nilai ini sesuai perangkat
PEER_IP = '192.168.1.105'
PEER_PORT = 5002
MY_PORT = 5001

SAMPLE_RATE = 44100         # 44.1 kHz (standar audio)
CHUNK_SIZE = 1024           # jumlah frame yang dikirim per paket
CHANNELS = 1                # mono

# === SOCKET SETUP ===
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', MY_PORT))

# === TERIMA AUDIO DARI PEER ===
def receive_audio():
    print(f"[LISTENING] Menunggu audio di port {MY_PORT}")
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            if data:
                audio_data = np.frombuffer(data, dtype=np.int16)
                sd.play(audio_data, samplerate=SAMPLE_RATE, blocking=False)
        except Exception as e:
            print("[ERROR] saat menerima:", e)

# === KIRIM AUDIO KE PEER ===
def send_audio():
    print(f"[SENDING] Kirim audio ke {PEER_IP}:{PEER_PORT}")

    def callback(indata, frames, time, status):
        if status:
            print("[WARN]", status)
        try:
            sock.sendto(indata.tobytes(), (PEER_IP, PEER_PORT))
        except Exception as e:
            print("[ERROR] saat mengirim:", e)

    with sd.InputStream(samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        dtype='int16',
                        blocksize=CHUNK_SIZE,
                        callback=callback):
        print("[MIC ACTIVE] Tekan Ctrl+C untuk keluar.")
        threading.Event().wait()

# === MAIN ===
if __name__ == '__main__':
    recv_thread = threading.Thread(target=receive_audio, daemon=True)
    recv_thread.start()

    try:
        send_audio()
    except KeyboardInterrupt:
        print("\n[EXIT] Program dihentikan.")
