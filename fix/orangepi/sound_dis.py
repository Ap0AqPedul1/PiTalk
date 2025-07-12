import socket
import threading
import sounddevice as sd
import numpy as np
import json
import time

SERVER_IP = "192.168.0.150"     # IP server relay tujuan
SERVER_PORT = 5005              # Port server relay
LOCAL_PORT = 5006               # Port lokal untuk menerima data (beda dari server)

samplerate = 44100  # Hz
channels = 1        # mono
blocksize = 1024    # frames per blok

file_path = 'state.json'
prev_mic = False

def load_state():
    with open(file_path) as f:
        return json.load(f)

def monitor_mic():
    global prev_mic
    print("Listening for mic status changes (Ctrl+C to stop)...")
    while True:
        state = load_state()
        if state['mic'] != prev_mic:
            print(f"Mic status: {state['mic']}")
            prev_mic = state['mic']
        time.sleep(1)

def send_data(sock, server_address):
    print("Thread mengirim data audio berjalan")

    def callback(indata, frames, time, status):
        global prev_mic
        if status:
            print(f"Status rekaman: {status}")
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > 3 and not prev_mic:
            sock.sendto(indata.astype(np.float32).tobytes(), server_address)
            print(f"Mengirim data audio {len(indata.tobytes())} bytes ke server")

    try:
        with sd.InputStream(samplerate=samplerate,
                            channels=channels,
                            blocksize=blocksize,
                            dtype='float32',
                            callback=callback):
            print("Mulai merekam dan mengirim audio, tekan Ctrl+C untuk berhenti")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("Pengiriman audio dihentikan")

def receive_data(sock):
    stream = sd.OutputStream(samplerate=samplerate, channels=channels, dtype='float32')
    stream.start()
    print("Thread menerima data audio berjalan")
    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                print(f"Menerima data audio {len(data)} bytes dari {addr}")
                audio = np.frombuffer(data, dtype=np.float32)
                stream.write(audio)
            except socket.timeout:
                continue
    except Exception as e:
        print("Error di thread terima:", e)

def udp_client_threaded():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', LOCAL_PORT))  # Wajib agar bisa menerima data
    sock.settimeout(1)           # Supaya recvfrom tidak nge-freeze selamanya

    server_address = (SERVER_IP, SERVER_PORT)

    # Thread untuk menerima pesan
    recv_thread = threading.Thread(target=receive_data, args=(sock,), daemon=True)
    recv_thread.start()

    # Thread untuk cek mic
    mic_thread = threading.Thread(target=monitor_mic, daemon=True)
    mic_thread.start()

    # Thread utama: kirim audio
    send_data(sock, server_address)

    sock.close()

if __name__ == "__main__":
    udp_client_threaded()
