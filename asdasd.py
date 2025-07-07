import socket
import pyaudio
import threading

def audio_send(stream, conn, buffer_size):
    try:
        while True:
            data = stream.read(buffer_size)
            conn.sendall(data)
    except Exception as e:
        print(f"Send error: {e}")

def audio_receive(stream, conn, buffer_size):
    try:
        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            stream.write(data)
    except Exception as e:
        print(f"Receive error: {e}")

def start_server():
    server_ip = '192.168.0.101'
    server_port = 5000
    buffer_size = 1024

    p = pyaudio.PyAudio()

    # Open stream for audio input (microphone)
    stream_in = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=44100,
                       input=True,
                       frames_per_buffer=buffer_size)
    # Open stream for audio output (speaker)
    stream_out = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        output=True,
                        frames_per_buffer=buffer_size)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)
    print(f"Server listening on {server_ip}:{server_port}")

    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    # Jalankan thread parallel untuk send dan receive audio
    thread_send = threading.Thread(target=audio_send, args=(stream_in, conn, buffer_size))
    thread_recv = threading.Thread(target=audio_receive, args=(stream_out, conn, buffer_size))
    thread_send.start()
    thread_recv.start()

    try:
        thread_send.join()
        thread_recv.join()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        stream_in.stop_stream()
        stream_in.close()
        stream_out.stop_stream()
        stream_out.close()
        p.terminate()
        conn.close()
        server_socket.close()

if __name__ == '__main__':
    start_server()
