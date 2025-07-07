import socket

def udp_server_dynamic_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 12345))  # Bind ke port server untuk menerima data

    print("Server menunggu paket dari client...")

    try:
        while True:
            data, client_address = sock.recvfrom(4096)  # Terima paket dari client
            print(f"Terima '{data.decode()}' dari {client_address}")

            # Kirim balasan ke client yang baru diketahui
            response = b"Hello, data diterima!"
            sock.sendto(response, client_address)
            print(f"Kirim balasan ke {client_address}")

    except KeyboardInterrupt:
        print("Server dihentikan.")
    finally:
        sock.close()

if __name__ == "__main__":
    udp_server_dynamic_client()
