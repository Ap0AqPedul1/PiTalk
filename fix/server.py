import socket

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5005
BUFFER_SIZE = 65507

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

clients = set()

print("Server relay berjalan, menunggu paket...")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    if addr not in clients:
        clients.add(addr)
        print(f"Tambah client baru: {addr}, total client: {len(clients)}")
    print(f"Menerima {len(data)} bytes dari {addr}, diteruskan ke client lain")
    response = b"Hello, data diterima!"
  
    for client in clients:
        if client != addr:
            sock.sendto(data, client)
