import socket
import threading
import json

HOST = '0.0.0.0'
CHAT_PORT = 7777

CONTROL_SERVER_IP = '192.168.1.110'  # sesuaikan IP control server
CONTROL_SERVER_UPDATE_PORT = 9999

class ServerData:
    def __init__(self):
        self.mute_status = {}  # user_id: mute bool
        self.clients = {}  # (ip, port): user_id
        self.clients_lock = threading.Lock()
        self.mute_lock = threading.Lock()

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((HOST, CHAT_PORT))

        # TCP connection to control server for mute updates
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((CONTROL_SERVER_IP, CONTROL_SERVER_UPDATE_PORT))

    def start(self):
        threading.Thread(target=self._listen_udp, daemon=True).start()
        threading.Thread(target=self._listen_tcp_updates, daemon=True).start()
        print(f"server_data UDP listening on port {CHAT_PORT}")
        while True:
            pass

    def _listen_udp(self):
        while True:
            data, addr = self.udp_sock.recvfrom(4096)
            try:
                msg = data.decode().strip()
                cmd = json.loads(msg)
                user_id = cmd.get('user_id')
                chat = cmd.get('chat')
                if not user_id or not chat:
                    continue

                with self.clients_lock:
                    self.clients[addr] = user_id

                # Check mute status
                muted = False
                with self.mute_lock:
                    muted = self.mute_status.get(user_id, False)
                if muted:
                    # Ignore messages from muted users
                    continue

                # Broadcast chat to all other clients
                self._broadcast_chat(user_id, chat, exclude=addr)

            except Exception as e:
                print("Error UDP packet:", e)

    def _broadcast_chat(self, user_id, chat, exclude=None):
        msg_obj = {'user_id': user_id, 'chat': chat}
        msg_str = json.dumps(msg_obj)
        with self.clients_lock:
            for client_addr in list(self.clients.keys()):
                if client_addr == exclude:
                    continue
                try:
                    self.udp_sock.sendto(msg_str.encode(), client_addr)
                except:
                    # Remove problematic clients
                    del self.clients[client_addr]

    def _listen_tcp_updates(self):
        buffer = ''
        while True:
            data = self.tcp_sock.recv(1024).decode()
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                try:
                    update = json.loads(line.strip())
                    user_id = update.get('user_id')
                    mute = update.get('mute')
                    if user_id is not None and mute is not None:
                        with self.mute_lock:
                            self.mute_status[user_id] = mute
                        print(f"Updated mute status: user {user_id} mute={mute}")
                except:
                    continue

if __name__ == "__main__":
    server = ServerData()
    server.start()
