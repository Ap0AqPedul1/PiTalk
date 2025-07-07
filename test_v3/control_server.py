import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 8888

USERS = {}
lock = threading.Lock()

def handle_client_chat(conn, addr):
    # Contoh placeholder handling Control Server client (asli Anda tentu fungsionalnya lebih lengkap)
    try:
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Decoding dan mengupdate USERS dict sesuai protokol Anda
                # Contoh dummy (harus disesuaikan):
                msg = data.decode('utf-8').strip()
                if msg.startswith("JOIN"):
                    parts = msg.split()
                    if len(parts) >= 3:
                        username = parts[1]
                        udp_port = int(parts[2])
                        with lock:
                            USERS[username] = {'ip': addr[0], 'udp_port': udp_port}
                        print(f"User {username} joined from {addr[0]}:{udp_port}")
                elif msg.startswith("LEAVE"):
                    parts = msg.split()
                    if len(parts) >= 2:
                        username = parts[1]
                        with lock:
                            USERS.pop(username, None)
                        print(f"User {username} left")
    except Exception as e:
        print(f"Error in client chat handler: {e}")

def thread_tcp_user_query(conn, addr):
    with lock:
        # Kirim list user aktif dalam bentuk list dict dengan ip dan udp_port
        active_users = [ {'ip': u['ip'], 'udp_port': u['udp_port']} for u in USERS.values() ]
    data = json.dumps(active_users).encode('utf-8')
    try:
        conn.sendall(data)
    except Exception as e:
        print(f"Error sending user data to {addr}: {e}")
    finally:
        conn.close()

def tcp_user_server():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((HOST, 9999))
    tcp_sock.listen(5)
    print(f"Control Server User TCP server listening on {HOST}:9999")
    while True:
        conn, addr = tcp_sock.accept()
        threading.Thread(target=thread_tcp_user_query, args=(conn, addr), daemon=True).start()

def main():
    threading.Thread(target=tcp_user_server, daemon=True).start()
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"Control Server main listening on {HOST}:{PORT}")
    while True:
        conn, addr = server_sock.accept()
        threading.Thread(target=handle_client_chat, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()
