import socket
import threading

SERVER_IP = "192.168.0.104"   # IP server relay kamu (ubah jika perlu)
SERVER_PORT = 5005
BUFFER_SIZE = 4096

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 0))  # Gunakan port acak

def listen():
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"[<] Diterima dari {addr}: {data.decode(errors='ignore')}")
        except Exception as e:
            print(f"[X] Error terima: {e}")

# Jalankan thread penerima
thread = threading.Thread(target=listen, daemon=True)
thread.start()

# Kirim data berulang
while True:
    msg = input("Ketik pesan (enter untuk kirim): ")
    sock.sendto(msg.encode(), (SERVER_IP, SERVER_PORT))
