import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 8888
DATA_SERVER_UPDATE_PORT = 9999

class ControlServer:
    def __init__(self):
        self.users = {}  # user_id: {"conn": conn, "addr": addr, "mute": False}
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)

        # Socket to send update mute status to server_data
        self.data_server_conn = None
        self.data_server_lock = threading.Lock()

    def start(self):
        print("ControlServer started. Waiting for clients and server_data connection...")
        threading.Thread(target=self._accept_data_server_conn, daemon=True).start()
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self._client_handler, args=(conn, addr), daemon=True).start()

    def _accept_data_server_conn(self):
        # Listening for one connection from server_data for mute update
        data_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        data_server_sock.bind((HOST, DATA_SERVER_UPDATE_PORT))
        data_server_sock.listen(1)
        print(f"Waiting for server_data to connect for mute updates on port {DATA_SERVER_UPDATE_PORT}...")
        conn, addr = data_server_sock.accept()
        print(f"server_data connected from {addr} for mute updates.")
        with self.data_server_lock:
            self.data_server_conn = conn
        try:
            while True:
                # Keep connection alive
                data = conn.recv(1024)
                if not data:
                    break
        except:
            pass
        with self.data_server_lock:
            self.data_server_conn = None
        print("server_data connection for mute updates closed.")

    def _client_handler(self, conn, addr):
        user_id = None
        try:
            while True:
                data = b''
                while not data.endswith(b'\n'):
                    chunk = conn.recv(1024)
                    if not chunk:
                        return
                    data += chunk
                msg = data.decode().strip()
                try:
                    cmd = json.loads(msg)
                except:
                    continue
                action = cmd.get('action')
                if action == 'join':
                    user_id = cmd.get('user_id')
                    if user_id:
                        with self.lock:
                            self.users[user_id] = {'conn': conn, 'addr': addr, 'mute': False}
                        self._send_response(conn, {'result': 'joined', 'user_id': user_id})
                        print(f"User {user_id} joined from {addr}")
                elif action == 'mute':
                    target = cmd.get('user_id')
                    if target:
                        self._set_mute_status(target, True)
                elif action == 'unmute':
                    target = cmd.get('user_id')
                    if target:
                        self._set_mute_status(target, False)
                elif action == 'leave':
                    if user_id:
                        self._remove_user(user_id)
                    return
        finally:
            if user_id:
                self._remove_user(user_id)

    def _set_mute_status(self, user_id, mute):
        with self.lock:
            if user_id in self.users:
                self.users[user_id]['mute'] = mute
                print(f"User {user_id} mute set to {mute}")
                self._send_mute_update_to_data_server(user_id, mute)

    def _remove_user(self, user_id):
        with self.lock:
            if user_id in self.users:
                print(f"User {user_id} disconnected.")
                del self.users[user_id]
                self._send_mute_update_to_data_server(user_id, True)

    def _send_response(self, conn, obj):
        try:
            conn.sendall((json.dumps(obj) + '\n').encode())
        except:
            pass

    def _send_mute_update_to_data_server(self, user_id, mute):
        with self.data_server_lock:
            if self.data_server_conn:
                try:
                    msg = json.dumps({'user_id': user_id, 'mute': mute}) + '\n'
                    self.data_server_conn.sendall(msg.encode())
                except:
                    self.data_server_conn = None

if __name__ == "__main__":
    server = ControlServer()
    server.start()
