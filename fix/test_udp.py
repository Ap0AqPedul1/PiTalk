import socket

# Konfigurasi
IP_SERVER = "0.0.0.0"  # menerima dari semua IP
PORT = 5005
BUFFER_SIZE = 1024

# Buat socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP_SERVER, PORT))

print(f"Server berjalan di {IP_SERVER}:{PORT}")

# Loop terima pesan
while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"Dari {addr}: {data.decode()}")
    
    # Kirim balasan
    reply = "Pesan diterima!"
    sock.send(reply.encode(), addr)
