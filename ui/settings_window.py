from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QTextEdit, QComboBox, QSlider, 
                               QPushButton, QColorDialog, QCheckBox, QGroupBox, QScrollArea, QApplication)
from PySide6.QtCore import Qt, Signal
import sounddevice as sd
from utils.config_manager import config_manager

class SettingsWindow(QWidget):
    settings_changed = Signal()
    lock_overlay_toggled = Signal(bool)
    start_requested = Signal()
    stop_requested = Signal()
    hide_overlay_requested = Signal()
    send_ai_requested = Signal()
    clear_text_requested = Signal()
    scroll_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meeting Assistant Settings")
        self.resize(600, 700)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Control Buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Listening (Ctrl+Alt+S)")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.start_btn.clicked.connect(self.start_requested.emit)
        
        self.stop_btn = QPushButton("Stop Listening (Ctrl+Alt+S)")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)

        # AI Controls
        ai_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send to AI (Ctrl+Alt+Enter)")
        self.send_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.send_btn.clicked.connect(lambda: self.send_ai_requested.emit())
        
        self.clear_btn = QPushButton("Clear Text (Ctrl+Alt+Bksp)")
        self.clear_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        self.clear_btn.clicked.connect(lambda: self.clear_text_requested.emit())
        
        ai_layout.addWidget(self.send_btn)
        ai_layout.addWidget(self.clear_btn)
        layout.addLayout(ai_layout)

        # Scroll Controls
        scroll_layout = QHBoxLayout()
        self.scroll_up_btn = QPushButton("Scroll Up (Ctrl+Alt+Up)")
        self.scroll_up_btn.clicked.connect(lambda: self.scroll_requested.emit("up"))
        
        self.scroll_down_btn = QPushButton("Scroll Down (Ctrl+Alt+Down)")
        self.scroll_down_btn.clicked.connect(lambda: self.scroll_requested.emit("down"))
        
        scroll_layout.addWidget(self.scroll_up_btn)
        scroll_layout.addWidget(self.scroll_down_btn)
        layout.addLayout(scroll_layout)

        # App Controls
        app_layout = QHBoxLayout()
        self.hide_btn = QPushButton("Hide Overlay (Ctrl+Alt+O)")
        self.hide_btn.clicked.connect(lambda: self.hide_overlay_requested.emit())
        
        self.exit_btn = QPushButton("Exit Application (Ctrl+Alt+Q)")
        self.exit_btn.setStyleSheet("background-color: #333; color: white;")
        self.exit_btn.clicked.connect(QApplication.instance().quit)
        
        app_layout.addWidget(self.hide_btn)
        app_layout.addWidget(self.exit_btn)
        layout.addLayout(app_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Audio Settings
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QVBoxLayout()
        
        audio_layout.addWidget(QLabel("Input Device:"))
        self.device_combo = QComboBox()
        self.populate_devices()
        self.device_combo.currentIndexChanged.connect(self.save_audio_device)
        audio_layout.addWidget(self.device_combo)
        
        audio_group.setLayout(audio_layout)
        self.form_layout.addWidget(audio_group)

        # Transcription Settings
        trans_group = QGroupBox("Transcription Settings")
        trans_layout = QVBoxLayout()
        
        trans_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["local", "cloud"])
        self.mode_combo.setCurrentText(config_manager.get("transcription_mode", "local"))
        self.mode_combo.currentTextChanged.connect(lambda t: self.update_config("transcription_mode", t))
        trans_layout.addWidget(self.mode_combo)
        
        trans_layout.addWidget(QLabel("OpenAI API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(config_manager.get("openai_api_key", ""))
        self.api_key_input.textChanged.connect(lambda t: self.update_config("openai_api_key", t))
        trans_layout.addWidget(self.api_key_input)
        
        trans_group.setLayout(trans_layout)
        self.form_layout.addWidget(trans_group)

        # LLM Settings
        llm_group = QGroupBox("LLM Settings")
        llm_layout = QVBoxLayout()
        
        llm_layout.addWidget(QLabel("Prompt Template (use {{transcript}}):"))
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(config_manager.get("prompt_template", ""))
        self.prompt_edit.textChanged.connect(lambda: self.update_config("prompt_template", self.prompt_edit.toPlainText()))
        llm_layout.addWidget(self.prompt_edit)
        
        llm_group.setLayout(llm_layout)
        self.form_layout.addWidget(llm_group)

        # Overlay Settings
        overlay_group = QGroupBox("Overlay Settings")
        overlay_layout = QVBoxLayout()
        
        # Lock/Unlock
        self.lock_check = QCheckBox("Lock Overlay (Uncheck to Resize & Move)")
        self.lock_check.setChecked(True)
        self.lock_check.toggled.connect(self.lock_overlay_toggled.emit)
        overlay_layout.addWidget(self.lock_check)
        
        # Opacity
        overlay_layout.addWidget(QLabel("Opacity (%):"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(config_manager.get("overlay_opacity", 70))
        self.opacity_slider.valueChanged.connect(lambda v: self.update_config_and_signal("overlay_opacity", v))
        overlay_layout.addWidget(self.opacity_slider)
        
        # Font Size
        overlay_layout.addWidget(QLabel("Font Size:"))
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(10, 72)
        self.font_slider.setValue(config_manager.get("font_size", 24))
        self.font_slider.valueChanged.connect(lambda v: self.update_config_and_signal("font_size", v))
        overlay_layout.addWidget(self.font_slider)
        
        # Text Color
        self.color_btn = QPushButton("Choose Text Color")
        self.color_btn.clicked.connect(self.choose_color)
        overlay_layout.addWidget(self.color_btn)

        # Background Color
        self.bg_color_btn = QPushButton("Choose Background Color")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        overlay_layout.addWidget(self.bg_color_btn)
        
        overlay_group.setLayout(overlay_layout)
        self.form_layout.addWidget(overlay_group)

    def populate_devices(self):
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name = f"{i}: {dev['name']}"
                    self.device_combo.addItem(name, i)
                    if i == config_manager.get("audio_device_index", default_input):
                        self.device_combo.setCurrentIndex(self.device_combo.count() - 1)
        except Exception:
            pass

    def save_audio_device(self, index):
        device_idx = self.device_combo.itemData(index)
        config_manager.set("audio_device_index", device_idx)
        self.settings_changed.emit()

    def update_config(self, key, value):
        config_manager.set(key, value)

    def update_config_and_signal(self, key, value):
        config_manager.set(key, value)
        self.settings_changed.emit()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            config_manager.set("font_color", color.name())
            self.settings_changed.emit()

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # Store as hex string
            config_manager.set("bg_color", color.name())
            self.settings_changed.emit()
