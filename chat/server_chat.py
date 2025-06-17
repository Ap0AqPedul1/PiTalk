import socket

def udp_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f'Server started at {host}:{port}')

    clients = set()

    while True:
        message, client_address = server_socket.recvfrom(1024)
        print(f"Received message from {client_address}: {message.decode()}")

        # Tambah client baru ke set
        if client_address not in clients:
            clients.add(client_address)
            print(f"New client added: {client_address}")

        # Kirim pesan ke semua client kecuali pengirim
        for addr in clients:
            if addr != client_address:
                server_socket.sendto(message, addr)

if __name__ == "__main__":
    udp_server()
