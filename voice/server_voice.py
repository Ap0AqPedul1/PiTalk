# server_relay.py
import socket
from datetime import datetime

PORT = 5005
BUFFER_SIZE = 2048

# Buat socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("0.0.0.0", PORT))
   
# Simpan alamat client
client_addresses = set()

print("🔁 Server relay siap menerima dan meneruskan audio...")

try:
    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🎧 Diterima {len(data)} byte dari {addr}")

        client_addresses.add(addr)

        for client in client_addresses:
            if client != addr:
                server_socket.sendto(data, client)
except KeyboardInterrupt:
    print("❌ Server dihentikan.")
finally:
    server_socket.close()
