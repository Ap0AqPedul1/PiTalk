import socket
import threading
import json
import time

CONTROL_SERVER_IP = '192.168.0.105'  # Ganti sesuai IP Control Server Anda
CONTROL_SERVER_PORT = 9999
UDP_LISTEN_IP = '0.0.0.0'
UDP_LISTEN_PORT = 7777
POLL_INTERVAL = 5  # detik

active_clients = []
active_clients_lock = threading.Lock()

def poll_active_users():
    """Polling data user aktif dari Control Server melalui TCP."""
    global active_clients
    while True:
        try:
            with socket.create_connection((CONTROL_SERVER_IP, CONTROL_SERVER_PORT), timeout=3) as sock:
                data = b''
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                users = json.loads(data.decode('utf-8'))
                with active_clients_lock:
                    active_clients = users
                # Debug print jumlah client aktif
                print(f"[Polling] Received active clients: {len(users)}")
        except Exception as e:
            print(f"[Polling] Error polling active users: {e}")

        time.sleep(POLL_INTERVAL)

def udp_audio_server():
    """Menerima paket audio UDP dan meneruskannya hanya ke client aktif kecuali pengirim."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))
    print(f"Audio Server listening UDP on {UDP_LISTEN_IP}:{UDP_LISTEN_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(4096)  # buffer 4096 bytes
            sender_ip, sender_port = addr
            print(f"[UDP] Received audio from {sender_ip}:{sender_port}, size: {len(data)} bytes")
            # Dapatkan daftar client aktif saat ini
            with active_clients_lock:
                clients = active_clients.copy()
            # Forward paket ke semua client kecuali pengirim
            for client in clients:
                client_ip = client.get('ip')
                client_port = client.get('udp_port')
                if (client_ip, client_port) != (sender_ip, sender_port):
                    print(f"[UDP] Forwarding to {client_ip}:{client_port}")
                    try:
                        sock.sendto(data, (client_ip, client_port))

                    except Exception as e:
                        print(f"[UDP] Error sending to {client_ip}:{client_port} - {e}")
        except Exception as e:
            print(f"[UDP] Error receiving audio UDP: {e}")

def main():
    # Thread polling data user aktif
    threading.Thread(target=poll_active_users, daemon=True).start()
    # Thread menerima dan meneruskan audio UDP
    udp_audio_server()

if __name__ == '__main__':
    main()
