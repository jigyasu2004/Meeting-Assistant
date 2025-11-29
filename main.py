import sys
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot
from ui.overlay import OverlayWindow
from ui.settings_window import SettingsWindow
from ui.hotkeys import HotkeyManager
from audio.audio_listener import AudioListener
from llm.translator import Translator
from utils.logger import logger

class MainApp(QObject):
    # Signals to update UI from other threads
    update_overlay_signal = Signal(str, str) # role, text
    
    # Signals for hotkey actions (to run on main thread)
    toggle_transcription_signal = Signal()
    toggle_overlay_signal = Signal()
    open_settings_signal = Signal()
    copy_transcript_signal = Signal()
    send_ai_signal = Signal()
    clear_text_signal = Signal()
    scroll_signal = Signal(str)
    exit_app_signal = Signal()

    def __init__(self):
        super().__init__()
        self.overlay = OverlayWindow()
        self.settings = SettingsWindow()
        self.translator = Translator()
        
        self.is_transcribing = False
        self.accumulated_transcript = [] # List to store transcript chunks
        self.chat_history = [] # List of {"role": "user"|"assistant", "content": "..."}
        self.last_transcript = ""

        # Audio Listener
        self.audio_listener = AudioListener(
            on_transcript_callback=self.on_transcript_received,
            on_error_callback=self.on_audio_error
        )

        # Connect Signals
        self.update_overlay_signal.connect(self.overlay.add_message)
        self.settings.settings_changed.connect(self.reload_settings)
        self.settings.lock_overlay_toggled.connect(self.overlay.set_click_through)
        
        self.settings.start_requested.connect(self.start_transcription)
        self.settings.stop_requested.connect(self.stop_transcription)
        self.settings.hide_overlay_requested.connect(self.toggle_overlay)
        self.settings.send_ai_requested.connect(self.send_to_ai)
        self.settings.clear_text_requested.connect(self.clear_text)
        self.settings.scroll_requested.connect(self.overlay.scroll_content)
        
        self.toggle_transcription_signal.connect(self.toggle_transcription)
        self.toggle_overlay_signal.connect(self.toggle_overlay)
        self.open_settings_signal.connect(self.open_settings)
        self.copy_transcript_signal.connect(self.copy_transcript)
        
        # Connect new signals
        self.send_ai_signal.connect(self.send_to_ai)
        self.clear_text_signal.connect(self.clear_text)
        self.scroll_signal.connect(self.overlay.scroll_content)
        self.exit_app_signal.connect(QApplication.instance().quit)

        # Hotkeys (Ctrl + Alt + Key) - 'fn' is usually not mappable by OS, using Alt instead
        self.hotkeys = HotkeyManager({
            'toggle_transcription': self.toggle_transcription_signal.emit, # Ctrl+Shift+S (Legacy)
            'toggle_overlay': self.toggle_overlay_signal.emit,
            'open_settings': self.open_settings_signal.emit,
            'copy_transcript': self.copy_transcript_signal.emit,
            'send_to_ai': self.send_ai_signal.emit,
            'clear_text': self.clear_text_signal.emit,
            'scroll_up': lambda: self.scroll_signal.emit("up"),
            'scroll_down': lambda: self.scroll_signal.emit("down"),
            'exit_app': self.exit_app_signal.emit
        })

        # Preload Models
        self.overlay.show()
        self.settings.show() 
        self.update_overlay_signal.emit("System", "Initializing AI Models... Please wait.")
        self.audio_listener.preload()
        self.update_overlay_signal.emit("System", "Ready!")

    def on_transcript_received(self, text):
        # Store transcript
        self.accumulated_transcript.append(text)
        self.last_transcript = text
        # Show raw transcript immediately
        self.update_overlay_signal.emit("Transcript", text)

    @Slot()
    def send_to_ai(self):
        if not self.accumulated_transcript:
            self.update_overlay_signal.emit("System", "No new transcript to send.")
            return

        # Get the new text
        new_text = " ".join(self.accumulated_transcript)
        
        # Clear the buffer immediately so subsequent speech is treated as new
        self.accumulated_transcript = []
        
        self.update_overlay_signal.emit("System", "Sending to AI...")
        
        # Process with LLM in background
        threading.Thread(target=self.process_llm, args=(new_text,)).start()

    @Slot()
    def clear_text(self):
        self.accumulated_transcript = []
        self.chat_history = []
        self.overlay.text_browser.clear()
        self.update_overlay_signal.emit("System", "Transcript and Chat History cleared.")

    def process_llm(self, new_text):
        try:
            logger.info(f"Sending text to LLM: {new_text[:50]}...")
            
            # Add user message to history
            # We apply the prompt template here if needed, but for chat, usually raw text is better
            # If we want to support the "Translate this" template, we should apply it to the new_text
            # But let's assume the template is the "System Instruction" for now, or just send raw text.
            # To respect the user's config "prompt_template", we can use it to format the user message.
            
            prompt = self.translator.prompt_manager.get_prompt(new_text)
            self.chat_history.append({"role": "user", "content": prompt})
            
            # Send full history
            response = self.translator.process_with_history(self.chat_history)
            
            logger.info(f"LLM Response: {response[:50]}...")
            
            # Add assistant response to history
            self.chat_history.append({"role": "assistant", "content": response})
            
            self.update_overlay_signal.emit("AI", response)
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            self.update_overlay_signal.emit("System", f"AI Error: {e}")

    def on_audio_error(self, msg):
        self.update_overlay_signal.emit("System", f"Error: {msg}")

    @Slot()
    def toggle_transcription(self):
        if self.is_transcribing:
            self.stop_transcription()
        else:
            self.start_transcription()

    @Slot()
    def start_transcription(self):
        if not self.is_transcribing:
            self.audio_listener.start()
            self.is_transcribing = True
            self.update_overlay_signal.emit("System", "Listening started...")

    @Slot()
    def stop_transcription(self):
        if self.is_transcribing:
            self.audio_listener.stop()
            self.is_transcribing = False
            self.update_overlay_signal.emit("System", "Listening stopped.")

    @Slot()
    def toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()

    @Slot()
    def open_settings(self):
        self.settings.show()
        self.settings.raise_()
        self.settings.activateWindow()

    @Slot()
    def copy_transcript(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.last_transcript)
        self.update_overlay_signal.emit("System", "Copied to clipboard!")

    @Slot()
    def reload_settings(self):
        self.overlay.apply_settings()
        self.translator.update_api_key(self.settings.api_key_input.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep running even if windows closed
    
    main_app = MainApp()
    
    sys.exit(app.exec())
