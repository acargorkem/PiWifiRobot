import pyaudio
import numpy as np
import struct
import time
import queue
from scipy.signal import butter, sosfilt, sosfreqz

CHUNK = 8192  # frames to keep in buffer between reads
SAMP_RATE = 44100
pyaudio_format = pyaudio.paFloat32
buffer_format = np.float32
CHANNELS = 2

lowcut = 500.0
highcut = 1250.0

fulldata = np.array([])
raw_data = np.array([])

audio = pyaudio.PyAudio()  # create pyaudio instantiation


def get_device_index():
    global audio
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels'):
            device_name = audio.get_device_info_by_host_api_device_index(0, i).get('name')
            if device_name == 'snd_rpi_i2s_card: simple-card_codec_link snd-soc-dummy-dai-0 (hw:2,0)':
                print('device name : ' + device_name)
                return i
            else:
                return 0  # use default index: 0


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype='band', output='sos')
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfilt(sos, data)
    return y


def my_callback(in_data, frame_count, time_info, status):
    global fulldata, raw_data, frames

    audio_data = np.fromstring(in_data, dtype=buffer_format)
    raw_data = np.append(raw_data, audio_data)
    # do processing here
    audio_data = butter_bandpass_filter(audio_data, lowcut, highcut, SAMP_RATE, order=6)
    fulldata = np.append(fulldata, audio_data)
    return audio_data, pyaudio.paContinue


def open_stream():
    global audio
    stream = audio.open(format=pyaudio_format,
                        rate=SAMP_RATE,
                        channels=CHANNELS,
                        input_device_index=get_device_index(),
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=my_callback)
    return stream


def read_data(record_time):
    global raw_data, fulldata
    fulldata = np.array([])
    raw_data = np.array([])
    stream = open_stream()
    stream.start_stream()

    while stream.is_active():
        time.sleep(record_time)
        stream.stop_stream()
    stream.close()
    return fulldata.tobytes()
