import socket
import threading
import json

CONTROL_SERVER_IP = '129.10.10.186'
CONTROL_SERVER_PORT = 8888

def listen_server(sock):
    """Thread untuk mendengarkan pesan dari server"""
    buffer = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except:
                    print("Terima data tidak valid dari server")
                    continue
                # Jika pesan chat
                if msg.get("type") == "CHAT":
                    print(f"[{msg.get('from')}]: {msg.get('message')}")
                elif msg.get("info"):
                    print(f"[INFO]: {msg.get('info')}")
                elif msg.get("users") is not None:
                    print("[LIST USER]")
                    for u in msg["users"]:
                        print(f"- {u['user_id']}, mute={u['mute']}, kicked={u['kicked']}")
                elif msg.get("error"):
                    print(f"[ERROR]: {msg.get('error')}")
                else:
                    print("[SERVER]:", msg)
        except Exception as e:
            print("Koneksi terputus atau terjadi error:", e)
            break

def main():
    user_id = input("Masukkan user_id: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((CONTROL_SERVER_IP, CONTROL_SERVER_PORT))

    # Kirim JOIN
    join_cmd = {
        "command": "JOIN",
        "user_id": user_id
    }
    sock.sendall((json.dumps(join_cmd) + "\n").encode())

    # Start listener thread
    listener_thread = threading.Thread(target=listen_server, args=(sock,), daemon=True)
    listener_thread.start()

    print("Perintah: KICK <user>, MUTE <user>, UNMUTE <user>, LIST, CHAT <pesan>, EXIT")
    while True:
        inp = input("> ").strip()
        if inp.upper() == "EXIT":
            print("Keluar program client.")
            break
        elif inp.upper() == "LIST":
            cmd = {"command": "LIST"}
        elif inp.upper().startswith("KICK "):
            target = inp[5:].strip()
            cmd = {"command": "KICK", "user_id": target}
        elif inp.upper().startswith("MUTE "):
            target = inp[5:].strip()
            cmd = {"command": "MUTE", "user_id": target}
        elif inp.upper().startswith("UNMUTE "):
            target = inp[7:].strip()
            cmd = {"command": "UNMUTE", "user_id": target}
        elif inp.upper().startswith("CHAT "):
            message = inp[5:].strip()
            cmd = {"command": "CHAT", "user_id": user_id, "message": message}
        else:
            print("Perintah tidak dikenali.")
            continue

        sock.sendall((json.dumps(cmd) + "\n").encode())

    sock.close()

if __name__ == "__main__":
    main()
