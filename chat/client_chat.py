import socket
import threading

# --- Konfigurasi ---
SERVER_IP = '127.0.0.1'  # Ganti dengan IP server jika perlu
SERVER_PORT = 12345
USERNAME = "Azhari"      # Ganti sesuai nama client

# --- Setup Socket ---
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', 0))  # port random, auto

# --- Thread untuk menerima pesan dari server ---
def listen():
    while True:
        try:
            data, addr = client_socket.recvfrom(1024)
            print(f"\n{data.decode()}")
        except Exception as e:
            print(f"[RECEIVE ERROR] {e}")
            break

# --- Jalankan Thread Penerima ---
threading.Thread(target=listen, daemon=True).start()

print(f"[{USERNAME}] READY. Ketik pesan (Ctrl+C untuk keluar):")
while True:
    try:
        msg = input("> ")
        full_msg = f"[{USERNAME}] {msg}"
        client_socket.sendto(full_msg.encode(), (SERVER_IP, SERVER_PORT))
    except KeyboardInterrupt:
        print("\n[EXIT] Keluar dari chat.")
        break
    except Exception as e:
        print(f"[SEND ERROR] {e}")
        break

client_socket.close()
