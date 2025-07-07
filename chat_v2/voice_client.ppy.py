import socket
import threading
import json
import sounddevice as sd

CONTROL_SERVER_IP = '192.168.1.113'
CONTROL_SERVER_PORT = 8888

VOICE_SERVER_IP = '192.168.1.113'
VOICE_SERVER_PORT = 10000

UDP_PORT = 5001  # Ganti sesuai user (unik per client)
SAMPLERATE = 16000
CHANNELS = 1
CHUNK = 1024

def listen_control_server(sock):
    """Mendengarkan perintah/broadcast dari control server"""
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
                    print("Data tidak valid dari server")
                    continue
                if msg.get("info"):
                    print(f"[INFO]: {msg['info']}")
                elif msg.get("users") is not None:
                    print("[LIST USER]")
                    for u in msg["users"]:
                        print(f"- {u['user_id']}, mute={u['mute']}, kicked={u['kicked']}")
                elif msg.get("error"):
                    print(f"[ERROR]: {msg['error']}")
        except Exception as e:
            print("Error kontrol:", e)
            break

def send_audio(sock_udp, dest):
    def callback(indata, frames, time, status):
        if status:
            print("Input overflow:", status)
        try:
            sock_udp.sendto(indata.tobytes(), dest)
        except Exception as e:
            print("Send UDP error:", e)

    with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, blocksize=CHUNK, callback=callback):
        threading.Event().wait()  # Jalan terus

def receive_audio(sock_udp):
    def callback(outdata, frames, time, status):
        try:
            data, _ = sock_udp.recvfrom(CHUNK * 2)
            outdata[:] = memoryview(data).cast('h').tobytes()
        except:
            outdata[:] = b'\x00' * (CHUNK * 2)

    with sd.OutputStream(samplerate=SAMPLERATE, channels=CHANNELS, blocksize=CHUNK, dtype='int16', callback=callback):
        threading.Event().wait()

def main():
    user_id = input("Masukkan user_id: ").strip()

    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.connect((CONTROL_SERVER_IP, CONTROL_SERVER_PORT))

    join_cmd = {
        "command": "JOIN",
        "user_id": user_id,
        "udp_ip": socket.gethostbyname(socket.gethostname()),
        "udp_port": UDP_PORT
    }
    sock_tcp.sendall((json.dumps(join_cmd) + "\n").encode())

    # Mulai thread listener kontrol
    threading.Thread(target=listen_control_server, args=(sock_tcp,), daemon=True).start()

    # Siapkan socket UDP untuk voice
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.bind(('', UDP_PORT))  # Client akan terima di sini

    # Mulai thread untuk menerima audio
    threading.Thread(target=receive_audio, args=(sock_udp,), daemon=True).start()

    # Mulai kirim audio
    threading.Thread(target=send_audio, args=(sock_udp, (VOICE_SERVER_IP, VOICE_SERVER_PORT)), daemon=True).start()

    print("Voice client siap. Perintah: MUTE, UNMUTE, KICK, LIST, EXIT")
    while True:
        try:
            cmd = input("> ").strip()
            if cmd.upper() == "EXIT":
                break
            elif cmd.upper() == "LIST":
                sock_tcp.sendall(b'{"command":"LIST"}\n')
            elif cmd.upper().startswith("MUTE "):
                target = cmd[5:].strip()
                sock_tcp.sendall(json.dumps({"command": "MUTE", "user_id": target}).encode() + b"\n")
            elif cmd.upper().startswith("UNMUTE "):
                target = cmd[7:].strip()
                sock_tcp.sendall(json.dumps({"command": "UNMUTE", "user_id": target}).encode() + b"\n")
            elif cmd.upper().startswith("KICK "):
                target = cmd[5:].strip()
                sock_tcp.sendall(json.dumps({"command": "KICK", "user_id": target}).encode() + b"\n")
            else:
                print("Perintah tidak dikenali.")
        except Exception as e:
            print("Error input:", e)

    sock_tcp.close()
    sock_udp.close()

if __name__ == "__main__":
    main()
