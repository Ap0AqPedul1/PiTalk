import socket
import pyaudio
import threading
import keyboard  # pip install keyboard

SERVER_IP = "129.10.10.186"  # ← Ganti dengan IP server kamu
PORT = 5005

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()

def receive_audio(sock):
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
    while True:
        try:
            data, _ = sock.recvfrom(2048)
            stream.write(data)
        except Exception as e:
            print(f"[ERROR RECEIVE] {e}")

def send_audio(sock, server_address):
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    print("[INFO] Tekan <spasi> untuk bicara.")
    while True:
        if keyboard.is_pressed('space'):
            data = stream.read(CHUNK, exception_on_overflow=False)
            sock.sendto(data, server_address)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))  # Bind ke port lokal acak agar bisa menerima audio

    threading.Thread(target=receive_audio, args=(sock,), daemon=True).start()
    send_audio(sock, (SERVER_IP, PORT))

if __name__ == '__main__':
    main()
