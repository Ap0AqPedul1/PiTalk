# client.py
import socket

def client_program():
    host = "127.0.0.1"  # IP server
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    message = input("Kirim pesan: ")

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()
        print(f"Dari server: {data}")
        message = input("Kirim pesan: ")

    client_socket.close()

if __name__ == '__main__':
    client_program()
