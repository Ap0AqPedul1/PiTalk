import socket

CHUNK = 1024
PORT = 12345

def audio_relay_server(host='0.0.0.0'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, PORT))
    print(f"[STARTED] UDP Audio Relay Server on {host}:{PORT}")

    clients = set()

    while True:
        try:
            data, addr = server_socket.recvfrom(CHUNK)
            
            if addr not in clients:
                clients.add(addr)
                print(f"[JOINED] {addr}")

            for client in list(clients):
                if client != addr:
                    try:
                        server_socket.sendto(data, client)
                    except:
                        clients.remove(client)
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    audio_relay_server()
