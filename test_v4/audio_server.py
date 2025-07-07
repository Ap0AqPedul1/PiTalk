import socket
import threading

AUDIO_SERVER_IP = '0.0.0.0'
AUDIO_SERVER_PORT = 5005

clients = set()
lock = threading.Lock()

def start_audio_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((AUDIO_SERVER_IP, AUDIO_SERVER_PORT))
    print(f'[Audio Server] Listening on {AUDIO_SERVER_IP}:{AUDIO_SERVER_PORT}')
    while True:
        data, addr = sock.recvfrom(4096)
        with lock:
            if addr not in clients:
                clients.add(addr)
                print(f'[Audio Server] New client: {addr}')
            # Broadcast received audio data to all clients except sender
            for client in clients:
                if client != addr:
                    try:
                        sock.sendto(data, client)
                    except Exception as e:
                        print(f'[Audio Server Error] {e}')

if __name__ == "__main__":
    start_audio_server()
