import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 8888

lock = threading.Lock()
users = {}  # user_id -> user info dict: { "conn":, "addr":, "udp_ip":, "udp_port":, "status": "active"/"muted"/"kicked" }

def broadcast_user_list():
    with lock:
        user_list = [
            {
                "user_id": user_id,
                "udp_ip": info.get("udp_ip", ""),
                "udp_port": info.get("udp_port", 0),
                "status": info.get("status", "active")
            }
            for user_id, info in users.items()
            if info.get("status") != "kicked"
        ]
    return json.dumps(user_list)

def handle_client(conn, addr):
    user_id = None
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            line = data.decode().strip()
            if line.startswith("JOIN"):
                # Format: JOIN user_id udp_ip udp_port\n
                parts = line.split()
                if len(parts) != 4:
                    conn.sendall(b"ERROR Invalid JOIN format\n")
                    continue
                user_id = parts[1]
                udp_ip = parts[2]
                try:
                    udp_port = int(parts[3])
                except:
                    conn.sendall(b"ERROR Invalid UDP port\n")
                    continue
                with lock:
                    users[user_id] = {
                        "conn": conn,
                        "addr": addr,
                        "udp_ip": udp_ip,
                        "udp_port": udp_port,
                        "status": "active"
                    }
                conn.sendall(f"JOINED {user_id}\n".encode())
            elif line.startswith("LIST"):
                user_list_str = broadcast_user_list()
                conn.sendall(user_list_str.encode())
            elif line.startswith("MUTE"):
                parts = line.split()
                if len(parts) != 2:
                    conn.sendall(b"ERROR Invalid MUTE command\n")
                    continue
                target_user = parts[1]
                with lock:
                    if target_user in users:
                        users[target_user]["status"] = "muted"
                        conn.sendall(f"MUTED {target_user}\n".encode())
                    else:
                        conn.sendall(b"ERROR User not found\n")
            elif line.startswith("UNMUTE"):
                parts = line.split()
                if len(parts) != 2:
                    conn.sendall(b"ERROR Invalid UNMUTE command\n")
                    continue
                target_user = parts[1]
                with lock:
                    if target_user in users:
                        users[target_user]["status"] = "active"
                        conn.sendall(f"UNMUTED {target_user}\n".encode())
                    else:
                        conn.sendall(b"ERROR User not found\n")
            elif line.startswith("KICK"):
                parts = line.split()
                if len(parts) != 2:
                    conn.sendall(b"ERROR Invalid KICK command\n")
                    continue
                target_user = parts[1]
                with lock:
                    if target_user in users:
                        users[target_user]["status"] = "kicked"
                        try:
                            users[target_user]["conn"].sendall(b"KICKED\n")
                            users[target_user]["conn"].close()
                        except:
                            pass
                        del users[target_user]
                        conn.sendall(f"KICKED {target_user}\n".encode())
                    else:
                        conn.sendall(b"ERROR User not found\n")
            else:
                conn.sendall(b"ERROR Unknown command\n")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        if user_id:
            with lock:
                if user_id in users:
                    del users[user_id]
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Control Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
