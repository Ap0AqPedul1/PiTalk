import threading
import subprocess

def run_tcp():
    subprocess.run(["python", "tcp.client.py"])

def run_sound():
    subprocess.run(["python", "sound.py"])

t1 = threading.Thread(target=run_sound)
t2 = threading.Thread(target=run_tcp)

t1.start()
t2.start()

t1.join()
t2.join()
