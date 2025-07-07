import socket
import json
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
STATUS_FILE = "mute_status.json"

# Untuk tracking mapping UDP addr ke nama client (harus dikembangkan agar konsisten)
addr_to_name = {}

def load_status():
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(4096)
        mute_status = load_status()
        name = addr_to_name.get(addr)
        if not name:
            # Karena UDP tidak connection oriented, di sini Anda harus membuat mekanisme mapping
            # Contohnya kirim pesan via UDP dari client pertama kali berisi nama client
            # Untuk contoh sederhana, kita anggap data UDP berisi string "NAME:<nama_client>" saat pertama kirim
            msg = data.decode('utf-8', errors='ignore')
    
            if msg.startswith("NAME:"):
                client_name = msg[5:].strip()
                addr_to_name[addr] = client_name
                print(f"Registered UDP client {client_name} from {addr}")
            else:
                print(f"Received UDP from unknown addr {addr}, ignoring.")
        else:
            if mute_status.get(name, False):
                print(f"Ignored UDP data from muted client {name} ({addr})")
            else:
                print(f"Received UDP data from {name} ({addr}): {data.decode()}")

if __name__ == "__main__":
    udp_server()
