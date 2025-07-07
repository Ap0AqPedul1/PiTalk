import socket
import pyaudio
import threading

SERVER_IP = '192.168.0.103'  # Ganti dengan IP server Anda
SERVER_PORT = 50007

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Kirim identitas ke server saat connect
client_socket.sendall(b'client_a')

p = pyaudio.PyAudio()

stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
stream_out = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)

def send_audio():
    try:
        while True:
            data = stream_in.read(1024)
            client_socket.sendall(data)
    except Exception as e:
        print(f"Error kirim audio: {e}")

def receive_audio():
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            stream_out.write(data)
    except Exception as e:
        print(f"Error terima audio: {e}")

print("Client A siap, streaming audio dua arah...")

thread_send = threading.Thread(target=send_audio, daemon=True)
thread_receive = threading.Thread(target=receive_audio, daemon=True)

thread_send.start()
thread_receive.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    pass

stream_in.stop_stream()
stream_in.close()
stream_out.stop_stream()
stream_out.close()
p.terminate()
client_socket.close()
