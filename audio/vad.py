import torch
import numpy as np
from utils.logger import logger

class SileroVAD:
    def __init__(self):
        self.model = None
        self.utils = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Loading Silero VAD on {self.device}...")
            self.model, self.utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                                    model='silero_vad',
                                                    force_reload=False,
                                                    onnx=False)
            self.model.to(self.device)
            logger.info("Silero VAD loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD: {e}")

    def is_speech(self, audio_chunk, sample_rate=16000):
        """
        Check if the audio chunk contains speech.
        audio_chunk: numpy array of float32
        """
        if self.model is None:
            return False
        
        # Convert numpy array to tensor
        tensor = torch.from_numpy(audio_chunk).to(self.device)
        
        # Add batch dimension if needed (Silero expects [batch, time] or [time])
        # Usually for single chunk streaming, just 1D is fine or 2D [1, T]
        if len(tensor.shape) == 1:
            tensor = tensor.unsqueeze(0)

        try:
            speech_prob = self.model(tensor, sample_rate).item()
            return speech_prob > 0.5
        except Exception as e:
            logger.error(f"VAD Error: {e}")
            return False
