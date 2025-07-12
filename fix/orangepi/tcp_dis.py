import sys
import socket
import threading
import random
import re
import subprocess
import sounddevice as sd
import numpy as np
from PyQt5 import QtWidgets, QtCore

class ClientApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCP Client PyQt + test.py")
        self.setGeometry(100, 100, 600, 400)
        self.sock = None

        self.DEFAULT_CLIENT_NAME = f"Server"

        self.layout = QtWidgets.QVBoxLayout()

        # Input nama (disabled karena auto)
        self.top_layout = QtWidgets.QHBoxLayout()
        self.input_name = QtWidgets.QLineEdit()
        self.input_name.setText(self.DEFAULT_CLIENT_NAME)
        self.input_name.setEnabled(False)
        self.btn_connect = QtWidgets.QPushButton("Connect")
        self.btn_connect.setEnabled(False)
        self.top_layout.addWidget(self.input_name)
        self.top_layout.addWidget(self.btn_connect)
        self.layout.addLayout(self.top_layout)

        # Status
        self.status_label = QtWidgets.QLabel("Status: Belum terhubung")
        self.layout.addWidget(self.status_label)

        # Tabel client
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Nama Client", "Status", "Aksi"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.tableWidget)

        # Tombol bawah
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_list = QtWidgets.QPushButton("Minta List Client")
        self.btn_list.clicked.connect(self.request_list)
        self.btn_list.setEnabled(False)
        self.btn_exit = QtWidgets.QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close_app)
        self.btn_layout.addWidget(self.btn_list)
        self.btn_layout.addWidget(self.btn_exit)
        self.layout.addLayout(self.btn_layout)

        self.setLayout(self.layout)

        # Thread dan timer
        self.recv_thread = None
        self.running = False
        self.reconnect_timer = QtCore.QTimer()
        self.reconnect_timer.timeout.connect(self.connect_server)

        self.list_timer = QtCore.QTimer()
        self.list_timer.timeout.connect(self.request_list)

        # Mulai test.py di background
        self.test_process = subprocess.Popen(["pipenv", "run", "python", "sound_dis.py"])

        # Mulai koneksi otomatis
        self.connect_server()

    def connect_server(self):
        if self.sock:
            self.sock.close()

        name = self.DEFAULT_CLIENT_NAME
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('192.168.0.150', 6006))
            self.sock.sendall(name.encode('utf-8'))

            self.status_label.setText(f"Status: Terhubung sebagai {name}")
            self.btn_list.setEnabled(True)

            self.running = True
            self.recv_thread = threading.Thread(target=self.receive_data)
            self.recv_thread.daemon = True
            self.recv_thread.start()

            self.reconnect_timer.stop()
            self.list_timer.start(5000)
        except Exception as e:
            self.status_label.setText(f"Status: Gagal konek: {e}, mencoba lagi...")
            self.sock = None
            if not self.reconnect_timer.isActive():
                self.reconnect_timer.start(3000)

    def receive_data(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data.decode('utf-8')
                if buffer.startswith("Please send your name"):
                    buffer = ""
                else:
                    self.process_data(buffer.strip())
                    buffer = ""
            except:
                break
        self.sock = None
        self.running = False
        self.status_label.setText("Status: Terputus")

        QtCore.QMetaObject.invokeMethod(self.list_timer, "stop", QtCore.Qt.QueuedConnection)
        QtCore.QMetaObject.invokeMethod(self.reconnect_timer, "start", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(int, 3000))

    def process_data(self, data):
        if " - MUTE" in data or " - UNMUTE" in data:
            clients = self.parse_client_list(data)
            QtCore.QMetaObject.invokeMethod(self, "update_table", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(list, clients))

    def parse_client_list(self, data):
        clients = []
        lines = data.strip().split('\n')
        for line in lines:
            parts = line.split(' - ')
            if len(parts) == 2:
                user_info, status_str = parts
                match = re.match(r'^(.*?)\s*\(', user_info)
                user_name = match.group(1).strip() if match else user_info.strip()
                is_muted = status_str.strip().upper() == "MUTE"
                clients.append({'name': user_name, 'muted': is_muted})
        return clients

    @QtCore.pyqtSlot(list)
    def update_table(self, clients):
        self.tableWidget.setRowCount(len(clients))
        for row_num, client in enumerate(clients):
            self.tableWidget.setItem(row_num, 0, QtWidgets.QTableWidgetItem(client['name']))
            self.tableWidget.setItem(row_num, 1, QtWidgets.QTableWidgetItem("MUTE" if client['muted'] else "UNMUTE"))
            btn = QtWidgets.QPushButton("Toggle Mute")
            btn.clicked.connect(lambda checked, r=row_num: self.toggle_mute(r))
            self.tableWidget.setCellWidget(row_num, 2, btn)

    def toggle_mute(self, row_num):
        name_item = self.tableWidget.item(row_num, 0)
        status_item = self.tableWidget.item(row_num, 1)
        if not name_item or not status_item:
            return
        current_status = status_item.text()
        new_status = "MUTE" if current_status == "UNMUTE" else "UNMUTE"
        self.tableWidget.setItem(row_num, 1, QtWidgets.QTableWidgetItem(new_status))
        if self.sock:
            try:
                message = f"{new_status.lower()} {name_item.text()}"
                self.sock.sendall(message.encode('utf-8'))
                print(f"[Kirim ke server] {message}")
            except Exception as e:
                print(f"Gagal mengirim ke server: {e}")

    def request_list(self):
        if self.sock:
            try:
                self.sock.sendall(b"list\n")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Gagal kirim perintah 'list':\n{e}")

    def close_app(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.reconnect_timer.stop()
        self.list_timer.stop()

        # Hentikan test.py jika aktif
        if hasattr(self, 'test_process'):
            self.test_process.terminate()

        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ClientApp()
    window.show()
    sys.exit(app.exec_())
