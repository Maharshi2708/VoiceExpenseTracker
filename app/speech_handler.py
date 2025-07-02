import openai
from config.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text
