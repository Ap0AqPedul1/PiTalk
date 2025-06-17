# server.py
import socket

def server_program():
    host = "127.0.0.1"  # localhost
    port = 5000  # port bebas yang tidak dipakai

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Menunggu koneksi client...")

    conn, address = server_socket.accept()
    print(f"Terhubung dengan client {address}")

    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print(f"Dari client: {data}")
        data = input("Balas klient: ")
        conn.send(data.encode())
    conn.close()

if __name__ == '__main__':
    server_program()
