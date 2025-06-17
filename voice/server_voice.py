import socket
import threading

PORT = 5005
clients = set()

def handle_receive(sock):
    while True:
        try:
            data, addr = sock.recvfrom(2048)
            if addr not in clients:
                clients.add(addr)
                print(f"[NEW CLIENT] {addr}")
            # Relay ke client lain
            for client in clients:
                if client != addr:
                    sock.sendto(data, client)
            print(f"[RELAY] {len(data)} bytes dari {addr}")
        except Exception as e:
            print(f"[ERROR] {e}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))
    print(f"[SERVER] Menunggu audio di UDP port {PORT}...")
    handle_receive(sock)

if __name__ == '__main__':
    main()
