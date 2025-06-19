import socket
import threading
import json
import time

VOICE_SERVER_IP = '129.10.10.186'
VOICE_SERVER_PORT = 10000

CONTROL_SERVER_IP = '129.10.10.186'
CONTROL_SERVER_PORT = 8888

user_addrs = {}
user_status = {}  # user_id -> status (e.g., muted or not)
lock = threading.Lock()

def update_user_addrs():
    global user_addrs, user_status
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((CONTROL_SERVER_IP, CONTROL_SERVER_PORT))
                sock.sendall(b"LIST\n")
                data = b""
                while True:
                    part = sock.recv(1024)
                    if not part:
                        break
                    data += part
                user_list = json.loads(data.decode())
                with lock:
                    user_addrs = { (u["udp_ip"], u["udp_port"]) : u["user_id"] for u in user_list }
                    user_status = { u["user_id"]: u["status"] for u in user_list }
        except Exception as e:
            print("Error updating user_addrs:", e)
        time.sleep(5)

def voice_server_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((VOICE_SERVER_IP, VOICE_SERVER_PORT))
    print(f"Voice Server running on UDP {VOICE_SERVER_IP}:{VOICE_SERVER_PORT}")
    
    while True:
        data, addr = sock.recvfrom(4096)
        with lock:
            sender_user_id = user_addrs.get(addr, None)
            if sender_user_id is None or user_status.get(sender_user_id) == 'muted':
                continue
            for client_addr, user_id in user_addrs.items():
                if user_id != sender_user_id and user_status.get(user_id) != 'muted':
                    try:
                        sock.sendto(data, client_addr)
                    except Exception as e:
                        print(f"Error sending to {client_addr}: {e}")

if __name__ == "__main__":
    threading.Thread(target=update_user_addrs, daemon=True).start()
    voice_server_loop()
