import socket

# Konfigurasi
IP_SERVER = "192.168.18.104"  # ganti dengan IP server jika beda komputer
PORT = 5005

# Buat socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Kirim pesan
pesan = input("Ketik pesan ke server: ")
sock.sendto(pesan.encode(), (IP_SERVER, PORT))

# Terima balasan
data, _ = sock.recvfrom(1024)
print(f"Balasan dari server: {data.decode()}")
