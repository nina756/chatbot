import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from scipy.io.wavfile import write

# Recording settings
duration = 5  # Duration of recording in seconds
sample_rate = 44100  # Sample rate in Hz

def record_audio(duration, sample_rate):
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    return audio_data

def save_as_mp3(audio_data, sample_rate, filename):
    # Save as WAV first
    wav_filename = "temp.wav"
    write(wav_filename, sample_rate, audio_data)
    
    # Convert WAV to MP3
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(filename, format="mp3")
    print(f"Audio saved as {filename}")

# Record audio
audio_data = record_audio(duration, sample_rate)
print('recording finished')

# Save the recorded audio as MP3
save_as_mp3(audio_data, sample_rate, "recordingoutput.mp3")
