import subprocess

# Jalankan dua file python secara paralel
p1 = subprocess.Popen(["python", "sound.py"])
p2 = subprocess.Popen(["python", "tcp.client.py"])

# Tunggu hingga keduanya selesai
p1.wait()
p2.wait()
