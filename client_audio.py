# client_audio.py
import socket
import pyaudio
import threading

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def recv_audio(sock, stream):
    while True:
        try:
            data = sock.recv(CHUNK)
            if not data:
                break
            stream.write(data)
        except:
            break

def client_program():
    host = "129.10.10.206"
    port = 50007

    p = pyaudio.PyAudio()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    threading.Thread(target=recv_audio, args=(client_socket, stream_out)).start()

    try:
        while True:
            data = stream_in.read(CHUNK)
            client_socket.sendall(data)
    except KeyboardInterrupt:
        pass

    stream_in.stop_stream()
    stream_in.close()
    stream_out.stop_stream()
    stream_out.close()
    p.terminate()
    client_socket.close()

if __name__ == "__main__":
    client_program()
