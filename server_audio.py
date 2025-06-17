# server_audio.py
import socket
import pyaudio
import threading

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def recv_audio(conn, stream):
    while True:
        try:
            data = conn.recv(CHUNK)
            if not data:
                break
            stream.write(data)
        except:
            break

def server_program():
    host = "0.0.0.0"
    port = 50007

    p = pyaudio.PyAudio()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Menunggu koneksi client...")
    conn, addr = server_socket.accept()
    print(f"Koneksi dari {addr}")

    stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    threading.Thread(target=recv_audio, args=(conn, stream_out)).start()

    try:
        while True:
            data = stream_in.read(CHUNK)
            conn.sendall(data)
    except KeyboardInterrupt:
        pass

    stream_in.stop_stream()
    stream_in.close()
    stream_out.stop_stream()
    stream_out.close()
    p.terminate()
    conn.close()

if __name__ == "__main__":
    server_program()
