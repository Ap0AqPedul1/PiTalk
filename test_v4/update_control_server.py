import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 8888
USERS = {}
lock = threading.Lock()

def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())
        if msg.get('action') == 'join':
            name = msg.get('name')
            udp_port = msg.get('udp_port')
            with lock:
                USERS[name] = {'addr': (addr[0], udp_port)}
            resp = {'status': 'ok', 'message': f'{name} joined'}
            print(f'[Control] {name} joined from {addr[0]}:{udp_port}')
        else:
            resp = {'status': 'error', 'message': 'Unknown action'}
        conn.sendall(json.dumps(resp).encode())
    except Exception as e:
        print(f'[Control Error] {e}')
    finally:
        conn.close()

def start_control_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'[Control Server] Listening on {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_control_server()
