import socket
import sounddevice as sd
import threading
import numpy as np

SERVER_IP = '192.168.1.113'  # ganti dengan IP server Anda
SERVER_PORT = 5005

SAMPLE_RATE = 44100
CHANNELS = 1
BLOCKSIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)

def send_audio():
    def callback(indata, frames, time, status):
        if status:
            print(status)
        sock.sendto(indata.tobytes(), (SERVER_IP, SERVER_PORT))

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, blocksize=BLOCKSIZE, callback=callback):
        threading.Event().wait()  # keep thread alive

def receive_audio():
    with sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, blocksize=BLOCKSIZE) as stream:
        while True:
            try:
                data, _ = sock.recvfrom(4096)
                audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                stream.write(audio)
            except BlockingIOError:
                continue
            except Exception as e:
                print("Error receiving audio:", e)

if __name__ == '__main__':
    threading.Thread(target=send_audio, daemon=True).start()
    receive_audio()
