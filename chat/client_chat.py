import socket
import threading

SERVER_IP = '129.10.10.186'  # Ganti dengan IP server
SERVER_PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', 0))  # port random

def listen():
    while True:
        try:
            data, addr = client_socket.recvfrom(1024)
            print(f"\n[RELAY] {addr}: {data.decode()}")
        except Exception as e:
            print(f"[RECEIVE ERROR] {e}")
            break

threading.Thread(target=listen, daemon=True).start()

print("[READY] Type message (Ctrl+C to exit):")
while True:
    try:
        msg = input("> ")
        client_socket.sendto(msg.encode(), (SERVER_IP, SERVER_PORT))
    except KeyboardInterrupt:
        print("\n[EXIT] Bye.")
        break
    except Exception as e:
        print(f"[SEND ERROR] {e}")
        break

client_socket.close()
