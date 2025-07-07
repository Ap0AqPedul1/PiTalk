# server_tcp.py (modifikasi bagian client connect dan command)
import socket
import threading

class ClientInfo:
    def __init__(self, socket, address, name):
        self.socket = socket
        self.address = address
        self.name = name
        self.status = "UNMUTE"  # default status client

class TCPServer:
    def __init__(self, ip='0.0.0.0', port=6006):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # key: client name, value: ClientInfo
        self.lock = threading.Lock()

    def start(self):
        self.server_socket.bind((self.TCP_IP, self.TCP_PORT))
        self.server_socket.listen()
        print(f"Server TCP berjalan di {self.TCP_IP}:{self.TCP_PORT}")

        threading.Thread(target=self.command_input_loop, daemon=True).start()

        while True:
            client_socket, client_address = self.server_socket.accept()

            # Menerima nama client pertama kali
            client_socket.sendall(b"Please send your name:")
            name_data = client_socket.recv(1024)
            if not name_data:
                client_socket.close()
                continue
            client_name = name_data.decode().strip()

            with self.lock:
                if client_name in self.clients:
                    # Jika nama sudah dipakai
                    client_socket.sendall(b"Name already taken. Disconnecting.")
                    client_socket.close()
                    continue
                else:
                    self.clients[client_name] = ClientInfo(client_socket, client_address, client_name)

            print(f"Client baru terhubung: {client_name} ({client_address[0]}:{client_address[1]})")
            self.set_client_status(client_name, "UNMUTE")
            threading.Thread(target=self.handle_client, args=(client_name,), daemon=True).start()

    def handle_client(self, client_name):
        client_info = self.clients[client_name]
        sock = client_info.socket
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    print(f"Client {client_name} terputus")
                    break
                msg = data.decode().strip()
                print(f"Menerima dari {client_name}: {msg}")
        except ConnectionResetError:
            print(f"Connection reset by {client_name}")
        finally:
            with self.lock:
                sock.close()
                del self.clients[client_name]

    def command_input_loop(self):
        while True:
            command = input("Perintah (list/mute/unmute/exit): ").strip().lower()
            if command == "list":
                self.show_clients()
            elif command.startswith("mute "):
                name = command[5:]
                self.set_client_status(name, "MUTE")
            elif command.startswith("unmute "):
                name = command[7:]
                self.set_client_status(name, "UNMUTE")
            elif command == "exit":
                print("Menutup server...")
                self.close_all()
                break
            else:
                print("Perintah tidak dikenal. Gunakan: list, mute <name>, unmute <name>, exit")

    def show_clients(self):
        with self.lock:
            if not self.clients:
                print("Tidak ada client terhubung.")
                return
            print("Daftar client dan status:")
            for name, info in self.clients.items():
                addr = f"{info.address[0]}:{info.address[1]}"
                print(f"{name} ({addr}) - {info.status}")

    def set_client_status(self, name, status):
        with self.lock:
            client_info = self.clients.get(name)
            if client_info:
                client_info.status = status
                try:
                    client_info.socket.sendall(status.encode())
                    print(f"Kirim perintah '{status}' ke {name}")
                except Exception as e:
                    print(f"Gagal mengirim ke {name}: {e}")
            else:
                print(f"Client dengan nama '{name}' tidak ditemukan.")

    def close_all(self):
        with self.lock:
            for info in self.clients.values():
                info.socket.close()
            self.server_socket.close()

if __name__ == "__main__":
    server = TCPServer()
    server.start()
