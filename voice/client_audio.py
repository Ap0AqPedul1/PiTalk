import socket
import pyaudio
import threading

# Konfigurasi
SERVER_IP = '127.0.0.1'  # Ganti IP sesuai server
PORT = 12345
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Siapkan Audio
p = pyaudio.PyAudio()
stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Siapkan Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def receive_audio():
    while True:
        try:
            data, _ = client_socket.recvfrom(CHUNK)
            stream_out.write(data)
        except Exception as e:
            print(f"[RECEIVE ERROR] {e}")
            break

# Jalankan penerima
threading.Thread(target=receive_audio, daemon=True).start()

print("[VOICE CHAT] Tekan Ctrl+C untuk keluar.")
try:
    while True:
        data = stream_in.read(CHUNK, exception_on_overflow=False)
        client_socket.sendto(data, (SERVER_IP, PORT))
except KeyboardInterrupt:
    print("\n[EXIT] Keluar dari voice chat.")
except Exception as e:
    print(f"[SEND ERROR] {e}")
finally:
    client_socket.close()
    stream_in.stop_stream()
    stream_out.stop_stream()
    stream_in.close()
    stream_out.close()
    p.terminate()
