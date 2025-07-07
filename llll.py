# client_asyncio_audio.py
import asyncio
import pyaudio
import queue

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()

# Async queue untuk data audio keluar dan masuk
send_queue = asyncio.Queue()
recv_queue = asyncio.Queue()

async def send_audio(writer):
    while True:
        data = await send_queue.get()
        if data is None:
            break
        writer.write(data)
        await writer.drain()

async def recv_audio(reader):
    while True:
        data = await reader.read(CHUNK)
        if not data:
            break
        await recv_queue.put(data)

def callback(in_data, frame_count, time_info, status):
    asyncio.run_coroutine_threadsafe(send_queue.put(in_data), loop)
    return (None, pyaudio.paContinue)

async def playback():
    stream_out = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            output=True,
                            frames_per_buffer=CHUNK)
    while True:
        data = await recv_queue.get()
        if data is None:
            break
        stream_out.write(data)
    stream_out.stop_stream()
    stream_out.close()

async def main(host='192.168.0.103', port=8888):
    global loop
    loop = asyncio.get_running_loop()

    reader, writer = await asyncio.open_connection(host, port)
    
    # Stream input audio async dengan callback PyAudio dari thread berbeda
    stream_in = audio.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK,
                           stream_callback=callback)
    stream_in.start_stream()

    # Jalankan send dan receive audio secara async
    send_task = asyncio.create_task(send_audio(writer))
    recv_task = asyncio.create_task(recv_audio(reader))
    playback_task = asyncio.create_task(playback())

    await asyncio.gather(send_task, recv_task)

    # Cleanup
    await recv_queue.put(None)
    await send_queue.put(None)
    writer.close()
    await writer.wait_closed()
    stream_in.stop_stream()
    stream_in.close()
    audio.terminate()

if __name__ == "__main__":
    asyncio.run(main())
