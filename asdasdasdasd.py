import socket
import sounddevice as sd
import numpy as np

def udp_server_audio_play():
    UDP_IP = "192.168.0.105"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Server UDP berjalan pada {UDP_IP}:{UDP_PORT}")

    samplerate = 44100
    channels = 1
    dtype = 'int16'

    with sd.OutputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while True:
            data, addr = sock.recvfrom(65535)  # buffer size diubah supaya tidak eror
            print(f"Data diterima dari {addr}, memutar audio")

            audio_data = np.frombuffer(data, dtype=dtype)
            stream.write(audio_data)

if __name__ == "__main__":
    udp_server_audio_play()
