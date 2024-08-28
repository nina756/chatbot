import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from scipy.io.wavfile import write
import whisper
import requests
import pygame
import time
import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Recording settings
duration = 10  # Duration of recording in seconds
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





###### Respond ######

load_dotenv('.env.local')

# Replace with your actual API keys
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# 11 Labs API endpoint
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

def speech_to_text(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]

async def process_chatbot_input(user_input):
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a consulting case interviewer. You are interviewing a candidate for a consulting role. You are friendly and professional.",
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        model="gpt-3.5-turbo",
        max_tokens=300,
    )
    return response.choices[0].message.content

def text_to_speech(text, voice_id="pqHfZKP75CvOlQylNhV4"):
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    print(f"Using ElevenLabs API Key: {ELEVENLABS_API_KEY[:5]}...{ELEVENLABS_API_KEY[-5:]}")

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(ELEVENLABS_URL.format(voice_id=voice_id), json=data, headers=headers)

    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        return "output.mp3"
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()

async def main():
    # Step 0: Create and play introduction
    introduction = "Hello! I'm your interviewer. Let's start the interview, what type of case would you like to practice today?"
    audio_file = text_to_speech(introduction)
    play_audio(audio_file)

    # Step 1: Speech to text
    # Record audio
    audio_data = record_audio(duration, sample_rate)
    print('recording finished')

    # Save the recorded audio as MP3
    save_as_mp3(audio_data, sample_rate, "recordingoutput.mp3")
    user_input = speech_to_text("recordingoutput.mp3")
    print(f"User said: {user_input}")

    # Step 2: Process through chatbot
    ai_response = await process_chatbot_input(user_input)
    print(f"AI response: {ai_response}")

    # Step 3: Text to speech
    audio_file = text_to_speech(ai_response)

    # Step 4: Play audio response
    if audio_file:
        play_audio(audio_file)

if __name__ == "__main__":
    asyncio.run(main())