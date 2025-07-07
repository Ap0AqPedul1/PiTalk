# client_tcp.py (modifikasi untuk mengirim nama ke server saat connect)
import socket
import time
import threading
import json

class TCPClient:
    def __init__(self, server_port=6006):
        
        self.SERVER_PORT = server_port
        self.BUFFER_SIZE = 1024
        self.socket = None
        self.connected = False
        
        self.file ='state.json'

        self.state = self.load_state()
        self.name = self.state['name']
        self.SERVER_IP = self.state['server']
        self.status = self.state['mic']

    def load_state(self):
        with open(self.file) as f:
            return json.load(f)

    def save_state(self):
        self.state['mic'] = self.status
        with open(self.file, 'w') as f:
            json.dump(self.state, f, indent=4)

    def connect(self):
        while not self.connected:
            try:
                print(f"Mencoba koneksi ke {self.SERVER_IP}:{self.SERVER_PORT} ...")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.SERVER_IP, self.SERVER_PORT))

                # Terima prompt dari server untuk nama client
                prompt = self.socket.recv(self.BUFFER_SIZE).decode()
                print(prompt)

                # Kirim nama ke server
                self.socket.sendall(self.name.encode())

                # Bisa juga tunggu konfirmasi disini jika perlu

                self.connected = True
                print("Terhubung ke server.")
            except (ConnectionRefusedError, OSError):
                print("Gagal koneksi, mencoba ulang dalam 5 detik...")
                time.sleep(5)

    def listen_server(self):
        try:
            while self.connected:
                data = self.socket.recv(self.BUFFER_SIZE)
                if not data:
                    print("Server terputus.")
                    self.connected = False
                    self.socket.close()
                    break
                command = data.decode().strip()
                if command == "MUTE":
                    self.status = True
                    self.save_state()
                    print("Perintah dari server: MUTE - Microphone OFF")
                elif command == "UNMUTE":
                    self.status = False
                    self.save_state()
                    print("Perintah dari server: UNMUTE - Microphone ON")
                else:
                    print(f"Perintah tidak dikenali dari server: {command}")
                
        except ConnectionResetError:
            print("Koneksi server terputus.")
            self.connected = False
            if self.socket:
                self.socket.close()

    def run(self):
        while True:
            if not self.connected:
                self.connect()
                threading.Thread(target=self.listen_server, daemon=True).start()
            time.sleep(1)

if __name__ == "__main__":
    # Ganti "client1" dengan nama unik client Anda
    client = TCPClient()
    client.run()
