import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

def check_microphone(duration=5, samplerate=44100):
    print(f"[INFO] Merekam selama {duration} detik...")

    try:
        # Rekam suara dari mic
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()  # Tunggu hingga rekaman selesai

        print("[INFO] Rekaman selesai. Memutar ulang...")
        sd.play(recording, samplerate)
        sd.wait()

        # Simpan sebagai file (opsional)
        wav.write("mic_test.wav", samplerate, recording)
        print("[INFO] File 'mic_test.wav' disimpan.")
    except Exception as e:
        print(f"[ERROR] Gagal merekam suara: {e}")

if __name__ == "__main__":
    check_microphone()
