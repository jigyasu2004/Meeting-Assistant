import whisper
import torch
from utils.logger import logger
from utils.config_manager import config_manager

class WhisperLocal:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.current_model_size = config_manager.get("whisper_model_size", "small")
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Loading Local Whisper ({self.current_model_size}) on {self.device}...")
            self.model = whisper.load_model(self.current_model_size, device=self.device)
            logger.info("Local Whisper loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Local Whisper: {e}")

    def transcribe(self, audio_data):
        """
        Transcribe audio data.
        audio_data: numpy array of float32 (16kHz mono)
        """
        if self.model is None:
            return ""
        
        try:
            # Whisper expects float32 audio
            result = self.model.transcribe(audio_data, fp16=(self.device == "cuda"))
            text = result.get("text", "").strip()
            return text
        except Exception as e:
            logger.error(f"Local Transcription Error: {e}")
            return ""
