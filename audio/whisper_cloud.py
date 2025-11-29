import openai
from openai import OpenAI
import os
import tempfile
import soundfile as sf
from utils.logger import logger
from utils.config_manager import config_manager

class WhisperCloud:
    def __init__(self):
        self.api_key = config_manager.get("openai_api_key", "")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def update_api_key(self, key):
        self.api_key = key
        self.client = OpenAI(api_key=key)

    def transcribe(self, audio_data, sample_rate=16000):
        """
        Transcribe audio data using OpenAI API.
        audio_data: numpy array of float32
        """
        if not self.client:
            logger.warning("OpenAI API Key not set for Cloud Whisper.")
            return "Error: API Key missing"

        try:
            # Save to temporary wav file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_filename = tmp.name
            
            sf.write(tmp_filename, audio_data, sample_rate)

            with open(tmp_filename, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            
            os.remove(tmp_filename)
            
            text = transcript.text.strip()
            return text
        except Exception as e:
            logger.error(f"Cloud Transcription Error: {e}")
            return f"Error: {str(e)}"
