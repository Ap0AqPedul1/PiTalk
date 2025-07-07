import socket
import pyaudio
import threading

# ====== Konfigurasi IP dan PORT ======
LOCAL_IP = "192.168.0.101"   # Ganti dengan IP Pi atau PC ini
PEER_IP = "192.168.0.104"    # IP lawan
PORT = 5005

# ====== Konfigurasi Audio ======
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# ====== Setup UDP socket ======
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LOCAL_IP, PORT))

# ====== PyAudio setup ======
p = pyaudio.PyAudio()

# 🔊 OUTPUT stream (speaker)
output_stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       output=True,
                       frames_per_buffer=CHUNK)

# 🎙️ INPUT stream (mic)
input_stream = p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      input=True,
                      frames_per_buffer=CHUNK)

# ====== Fungsi terima audio ======
def receive_audio():
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            output_stream.write(data)
        except Exception as e:
            print("[❌ RECV ERROR]", e)

# ====== Fungsi kirim audio ======
def send_audio():
    while True:
        try:
            data = input_stream.read(CHUNK, exception_on_overflow=False)
            sock.sendto(data, (PEER_IP, PORT))
        except Exception as e:
            print("[❌ SEND ERROR]", e)

# ====== Jalankan dua thread ======
threading.Thread(target=receive_audio, daemon=True).start()
threading.Thread(target=send_audio, daemon=True).start()

print(f"[✅] Voice Chat Aktif {LOCAL_IP} ⇄ {PEER_IP}")
while True:
    pass
