import sounddevice as sd
import numpy as np
import threading
import queue
import time
from scipy import signal
from utils.logger import logger
from utils.config_manager import config_manager
from audio.vad import SileroVAD
from audio.whisper_local import WhisperLocal
from audio.whisper_cloud import WhisperCloud

class AudioListener:
    def __init__(self, on_transcript_callback, on_error_callback=None):
        self.running = False
        self.on_transcript = on_transcript_callback
        self.on_error = on_error_callback
        
        self.target_sample_rate = 16000
        self.device_sample_rate = 16000
        self.block_size = 1024 # Increased block size
        self.vad = SileroVAD()
        
        # Transcription engines
        self.whisper_local = None
        self.whisper_cloud = None
        
        self.audio_queue = queue.Queue()
        self.buffer = []
        self.vad_buffer = np.array([], dtype=np.float32)
        self.silence_counter = 0
        self.speech_active = False
        
        # Settings
        self.silence_threshold = 20  # chunks of silence to trigger end of speech
        self.min_speech_length = 16000 * 1.0  # Minimum 1 second of speech
        
        self.processing_thread = None

    def initialize_engines(self):
        mode = config_manager.get("transcription_mode", "local")
        if mode == "local":
            if not self.whisper_local:
                logger.info("Initializing Local Whisper...")
                self.whisper_local = WhisperLocal()
        else:
            if not self.whisper_cloud:
                logger.info("Initializing Cloud Whisper...")
                self.whisper_cloud = WhisperCloud()

    def preload(self):
        """Preload models in a separate thread"""
        threading.Thread(target=self.initialize_engines, daemon=True).start()

    def get_devices(self):
        try:
            return sd.query_devices()
        except Exception as e:
            logger.error(f"Error querying devices: {e}")
            return []

    def start(self):
        if self.running:
            return

        self.initialize_engines()
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_audio_loop, daemon=True)
        self.processing_thread.start()
        
        device_index = config_manager.get("audio_device_index")
        
        try:
            # Query device info to get default sample rate
            device_info = sd.query_devices(device_index, 'input')
            self.device_sample_rate = int(device_info['default_samplerate'])
            logger.info(f"Device {device_index} Native Sample Rate: {self.device_sample_rate}")

            self.stream = sd.InputStream(
                device=device_index,
                channels=1,
                samplerate=self.device_sample_rate,
                blocksize=self.block_size,
                callback=self._audio_callback
            )
            self.stream.start()
            logger.info(f"Audio listener started on device {device_index}")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            if self.on_error:
                self.on_error(str(e))
            self.running = False

    def stop(self):
        self.running = False
        if hasattr(self, 'stream'):
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
        logger.info("Audio listener stopped")

    def _audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio status: {status}")
        if self.running:
            self.audio_queue.put(indata.copy())

    def _process_audio_loop(self):
        logger.info("Processing loop started")
        while self.running:
            try:
                # Get audio chunk
                try:
                    chunk = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # Flatten chunk
                chunk = chunk.flatten().astype(np.float32)

                # Debug Audio Level
                rms = np.sqrt(np.mean(chunk**2))
                if rms > 0.01: # Only log if there's some sound
                    # logger.debug(f"Audio detected, RMS: {rms:.4f}")
                    pass

                # Resample if necessary
                if self.device_sample_rate != self.target_sample_rate:
                    number_of_samples = int(len(chunk) * self.target_sample_rate / self.device_sample_rate)
                    chunk = signal.resample(chunk, number_of_samples)
                
                # Add to VAD buffer
                self.vad_buffer = np.concatenate((self.vad_buffer, chunk))
                
                # Process in 512-sample chunks (required by Silero)
                while len(self.vad_buffer) >= 512:
                    vad_chunk = self.vad_buffer[:512]
                    self.vad_buffer = self.vad_buffer[512:]
                    
                    # VAD Check
                    is_speech = self.vad.is_speech(vad_chunk, self.target_sample_rate)
                    
                    if is_speech:
                        if not self.speech_active:
                            logger.info("Speech detected...")
                        self.speech_active = True
                        self.silence_counter = 0
                        self.buffer.append(vad_chunk)
                    else:
                        if self.speech_active:
                            self.silence_counter += 1
                            self.buffer.append(vad_chunk) # Keep recording silence briefly
                            
                            if self.silence_counter > self.silence_threshold:
                                # End of speech segment
                                logger.info("End of speech detected.")
                                self._transcribe_buffer()
                                self.speech_active = False
                                self.silence_counter = 0
                                self.buffer = []
                        else:
                            # Just silence, ignore
                            pass
                        
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")

    def _transcribe_buffer(self):
        if not self.buffer:
            return
            
        full_audio = np.concatenate(self.buffer)
        
        if len(full_audio) < self.min_speech_length:
            logger.info("Audio too short, skipping.")
            return # Too short

        logger.info(f"Transcribing {len(full_audio)/self.target_sample_rate:.2f}s of audio...")
        
        mode = config_manager.get("transcription_mode", "local")
        text = ""
        
        if mode == "local" and self.whisper_local:
            text = self.whisper_local.transcribe(full_audio)
        elif mode == "cloud" and self.whisper_cloud:
            text = self.whisper_cloud.transcribe(full_audio, self.target_sample_rate)
            
        if text:
            logger.info(f"Transcript: {text}")
            if self.on_transcript:
                self.on_transcript(text)
