import socket
import pyaudio
import threading
import keyboard  # Untuk mendeteksi tombol spasi

# Konfigurasi audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# IP server dan port
SERVER_IP = "127.0.0.1"  # Ganti dengan IP server di jaringan lokal jika perlu
SERVER_PORT = 5005

# Buat socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inisialisasi audio
audio = pyaudio.PyAudio()

# Input dari mikrofon
stream_in = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                       input=True, frames_per_buffer=CHUNK)

# Output ke speaker
stream_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        output=True, frames_per_buffer=CHUNK)

# Thread untuk mengirim audio saat PTT ditekan
def send_audio():
    print("🎙️ Tekan dan tahan [spasi] untuk berbicara...")
    ptt_active = False
    while True:
        if keyboard.is_pressed('space'):
            data = stream_in.read(CHUNK, exception_on_overflow=False)
            client_socket.sendto(data, (SERVER_IP, SERVER_PORT))
            if not ptt_active:
                print("🎤 [PTT AKTIF] Anda sedang bicara...")
                ptt_active = True
        else:
            stream_in.read(CHUNK, exception_on_overflow=False)
            if ptt_active:
                print("🔇 [PTT NONAKTIF] Anda berhenti bicara.")
                ptt_active = False

# Thread untuk menerima audio dari server
def receive_audio():
    while True:
        try:
            data, _ = client_socket.recvfrom(2048)
            stream_out.write(data)
        except:
            break

# Jalankan kedua thread
threading.Thread(target=send_audio, daemon=True).start()
threading.Thread(target=receive_audio, daemon=True).start()

# Jaga agar program tetap berjalan
try:
    while True:
        pass
except KeyboardInterrupt:
    print("❌ Client dihentikan.")
finally:
    stream_in.close()
    stream_out.close()
    audio.terminate()
    client_socket.close()
          