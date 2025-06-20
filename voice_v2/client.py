import socket
import threading
import json

CONTROL_SERVER_IP = '192.168.1.111'
CONTROL_SERVER_PORT = 8888

VOICE_SERVER_IP = '192.168.1.111'
VOICE_SERVER_PORT = 10000

user_id = None
mute_status = False
udp_port = 15000  # Contoh port UDP client, sesuaikan sesuai implementasi

def tcp_listener(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            line = data.decode().strip()
            if line.startswith("KICKED"):
                print("[INFO] You have been kicked by the server.")
                break
            elif line.startswith("MUTED"):
                print(f"[INFO] User muted: {line.split()[1]}")
            elif line.startswith("UNMUTED"):
                print(f"[INFO] User unmuted: {line.split()[1]}")
            elif line.startswith("JOINED"):
                print(f"[INFO] Joined as {line.split()[1]}")
            # Chat messages are removed from here
        except Exception as e:
            print("Error in TCP listener:", e)
            break

def voice_receive(sock):
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            # Processing voice data (e.g., play) should be implemented here
            print(f"[Voice Data] Received {len(data)} bytes")
        except Exception as e:
            print("Voice receive error:", e)
            break

def voice_send(sock):
    while True:
        try:
            # Simulate sending voice data - in real case read microphone
            data = b"Voice sample data"
            sock.sendto(data, (VOICE_SERVER_IP, VOICE_SERVER_PORT))
            # Adjustable sleep time based on voice codec and frame size
            threading.Event().wait(0.1)
        except Exception as e:
            print("Voice send error:", e)
            break

def main():
    global user_id
    user_id = input("Enter your user ID: ")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', udp_port))

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((CONTROL_SERVER_IP, CONTROL_SERVER_PORT))

    # Send JOIN with udp_ip and udp_port
    local_ip = tcp_sock.getsockname()[0]  # Local IP of TCP socket
    join_cmd = f"JOIN {user_id} {local_ip} {udp_port}\n"
    tcp_sock.sendall(join_cmd.encode())

    threading.Thread(target=tcp_listener, args=(tcp_sock,), daemon=True).start()
    threading.Thread(target=voice_receive, args=(udp_sock,), daemon=True).start()
    threading.Thread(target=voice_send, args=(udp_sock,), daemon=True).start()

    # Simple command input for mute/unmute/kick
    while True:
        cmd = input("Enter command (MUTE user, UNMUTE user, KICK user, EXIT): ").strip()
        if cmd.upper() == "EXIT":
            break
        tcp_sock.sendall((cmd + "\n").encode())

    tcp_sock.close()
    udp_sock.close()

if __name__ == "__main__":
    main()
