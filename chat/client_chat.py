import socket
import threading

def receive_messages(sock):
    while True:
        try:
            message, addr = sock.recvfrom(1024)
            print(f"\nMessage from {addr}: {message.decode()}\n> ", end='')
        except:
            break

def udp_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.5)

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    print(f"Connected to server {server_ip}:{server_port}")
    while True:
        msg = input('> ')
        if msg.lower() == 'exit':
            print("Exiting chat...")
            break
        client_socket.sendto(msg.encode(), (server_ip, server_port))

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))
    udp_client(server_ip, server_port)
