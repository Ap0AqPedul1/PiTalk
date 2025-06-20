import socket

SERVER_IP = '0.0.0.0'
SERVER_PORT = 5005

clients = set()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"Voice server listening on {SERVER_IP}:{SERVER_PORT}")

while True:
    data, addr = sock.recvfrom(4096)
    if addr not in clients:
        clients.add(addr)
        print(f"Client {addr} joined.")

    for client in clients:
        if client != addr:
            sock.sendto(data, client)
