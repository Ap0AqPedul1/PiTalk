import socket

def udp_text_relay_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"[STARTED] UDP text relay server on {host}:{port}")

    clients = set()

    while True:
        try:
            data, addr = server_socket.recvfrom(1024)
            message = data.decode()
            print(f"[RECEIVED] From {addr}: {message}")

            # Tambahkan client baru ke set
            if addr not in clients:
                clients.add(addr)
                print(f"[JOINED] New client: {addr}")

            # Relay pesan ke semua client lain
            for client_addr in list(clients):
                if client_addr != addr:
                    try:
                        server_socket.sendto(data, client_addr)
                        print(f"[FORWARDED] To {client_addr}")
                    except Exception as e:
                        print(f"[ERROR] Failed to send to {client_addr}: {e}")
                        clients.remove(client_addr)

        except Exception as e:
            print(f"[SERVER ERROR] {e}")

if __name__ == "__main__":
    udp_text_relay_server()
