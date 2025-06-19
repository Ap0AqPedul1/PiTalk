import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 8888

lock = threading.Lock()
users = {}      # user_id -> (conn, addr)
user_status = {}  # user_id -> {'mute': False, 'kicked': False}

def broadcast(data, exclude_user=None):
    """Kirim data JSON ke semua user yang tidak kicked."""
    with lock:
        for uid, (conn, addr) in users.items():
            if uid != exclude_user and not user_status.get(uid, {}).get('kicked', False):
                try:
                    conn.sendall((json.dumps(data) + "\n").encode())
                except:
                    pass

def client_handler(conn, addr):
    user_id = None
    try:
        buffer = ""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    cmd = json.loads(line)
                except:
                    conn.sendall(b'{"error": "format json salah"}\n')
                    continue

                command = cmd.get("command")
                if command == "JOIN":
                    user_id = cmd.get("user_id")
                    if not user_id:
                        conn.sendall(b'{"error": "user_id harus diisi"}\n')
                        continue
                    with lock:
                        users[user_id] = (conn, addr)
                        user_status[user_id] = {"mute": False, "kicked": False}
                    response = {"info": f"{user_id} bergabung"}
                    conn.sendall((json.dumps(response) + "\n").encode())
                    broadcast({"info": f"{user_id} masuk ke server"}, exclude_user=user_id)
                    print(f"{user_id} join from {addr}")

                elif command == "KICK":
                    target = cmd.get("user_id")
                    with lock:
                        if target in user_status:
                            user_status[target]["kicked"] = True
                    broadcast({"info": f"{target} telah dikick oleh {user_id}"})
                
                elif command == "MUTE":
                    target = cmd.get("user_id")
                    with lock:
                        if target in user_status:
                            user_status[target]["mute"] = True
                    broadcast({"info": f"{target} dimute oleh {user_id}"})
                
                elif command == "UNMUTE":
                    target = cmd.get("user_id")
                    with lock:
                        if target in user_status:
                            user_status[target]["mute"] = False
                    broadcast({"info": f"{target} diunmute oleh {user_id}"})

                elif command == "LIST":
                    with lock:
                        lst = [{"user_id": u, "mute": user_status[u].get("mute", False), "kicked": user_status[u].get("kicked", False)} 
                               for u in users.keys()]
                    response = {"users": lst}
                    conn.sendall((json.dumps(response) + "\n").encode())

                elif command == "CHAT":
                    from_user = user_id
                    msg = cmd.get("message", "")
                    
                    with lock:
                        # Cek apakah user dalam keadaan mute
                        if user_status.get(from_user, {}).get("mute", False):
                            conn.sendall(b'{"error": "Kamu sedang dalam mode mute, tidak bisa mengirim pesan"}\n')
                            continue

                    # Broadcast chat message ke semua client
                    chat_data = {
                        "type": "CHAT",
                        "from": from_user,
                        "message": msg
                    }
                    broadcast(chat_data)


                else:
                    conn.sendall(b'{"error": "command tidak dikenali"}\n')

    except Exception as e:
        print(f"Error client_handler: {e}")
    finally:
        if user_id:
            with lock:
                if user_id in users:
                    del users[user_id]
                    del user_status[user_id]
            broadcast({"info": f"{user_id} keluar"})
        conn.close()
        print(f"Connection from {addr} closed")

def main():
    print("Control Server started...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
