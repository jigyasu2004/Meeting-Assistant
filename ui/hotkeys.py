import keyboard
from utils.logger import logger

class HotkeyManager:
    def __init__(self, callbacks):
        """
        callbacks: dict mapping action names to functions
        Actions: 'toggle_transcription', 'toggle_overlay', 'open_settings', 'copy_transcript'
        """
        self.callbacks = callbacks
        self.setup_hotkeys()

    def setup_hotkeys(self):
        try:
            # Standard Controls (Ctrl + Alt)
            keyboard.add_hotkey('ctrl+alt+s', self.callbacks.get('toggle_transcription', lambda: None))
            keyboard.add_hotkey('ctrl+alt+o', self.callbacks.get('toggle_overlay', lambda: None))
            keyboard.add_hotkey('ctrl+alt+p', self.callbacks.get('open_settings', lambda: None))
            keyboard.add_hotkey('ctrl+alt+c', self.callbacks.get('copy_transcript', lambda: None))
            
            # AI Controls
            keyboard.add_hotkey('ctrl+alt+enter', self.callbacks.get('send_to_ai', lambda: None))
            keyboard.add_hotkey('ctrl+alt+backspace', self.callbacks.get('clear_text', lambda: None))
            
            # Scroll Controls
            keyboard.add_hotkey('ctrl+alt+up', self.callbacks.get('scroll_up', lambda: None))
            keyboard.add_hotkey('ctrl+alt+down', self.callbacks.get('scroll_down', lambda: None))
            
            # App Controls
            keyboard.add_hotkey('ctrl+alt+q', self.callbacks.get('exit_app', lambda: None))
            
            logger.info("Hotkeys registered successfully.")
        except Exception as e:
            logger.error(f"Failed to register hotkeys: {e}")

    def stop(self):
        keyboard.unhook_all()
