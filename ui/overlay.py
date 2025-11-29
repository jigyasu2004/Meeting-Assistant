import sys
import ctypes
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QTextBrowser, QFrame
from PySide6.QtGui import QFont, QColor, QScreen
from PySide6.QtCore import Qt, Slot
from utils.config_manager import config_manager
from utils.logger import logger

# Windows API for hiding from capture
user32 = ctypes.windll.user32
WDA_EXCLUDEFROMCAPTURE = 0x00000011

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initial Geometry - Maximize with margins
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.95)
        height = int(screen.height() * 0.95)
        
        self.resize(
            config_manager.get("overlay_width", width),
            config_manager.get("overlay_height", height)
        )
        self.center_on_screen()

        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0) # Remove window margins

        # Container Frame (The "Board")
        self.container = QFrame()
        self.container.setObjectName("container")
        self.layout.addWidget(self.container)

        # Container Layout
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 20, 20, 20)

        # Use QTextBrowser for scrollable history
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.container_layout.addWidget(self.text_browser)

        self.apply_settings()
        self.hide_from_capture()
        self.set_click_through(True)
        
        self.last_role = None

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def apply_settings(self):
        # Font
        font_size = config_manager.get("font_size", 24)
        font_family = config_manager.get("font_family", "Arial")
        font = QFont(font_family, font_size)
        self.text_browser.setFont(font)

        # Colors & Opacity
        text_color = config_manager.get("font_color", "#FFFFFF")
        bg_color_hex = config_manager.get("bg_color", "#002800") # Default Dark Green
        
        # Convert hex to RGB for rgba string
        c = QColor(bg_color_hex)
        r, g, b = c.red(), c.green(), c.blue()
        
        opacity_percent = config_manager.get("overlay_opacity", 70)
        alpha = int(255 * (opacity_percent / 100))
        
        # Style the Container
        self.setStyleSheet(f"""
            QFrame#container {{
                background-color: rgba({r}, {g}, {b}, {alpha});
                border-radius: 20px;
                border: 2px solid rgba({r}, {g}, {b}, 100);
            }}
            QTextBrowser {{
                background-color: transparent;
                border: none;
                color: {text_color};
                padding: 10px;
            }}
        """)

    def hide_from_capture(self):
        try:
            hwnd = self.winId()
            user32.SetWindowDisplayAffinity(int(hwnd), WDA_EXCLUDEFROMCAPTURE)
            logger.info("Overlay hidden from screen capture.")
        except Exception as e:
            logger.error(f"Failed to hide overlay from capture: {e}")

    def set_click_through(self, enabled):
        if enabled:
            # Locked: Click-through, Frameless
            self.setWindowFlag(Qt.WindowTransparentForInput, True)
            self.setWindowFlag(Qt.FramelessWindowHint, True)
        else:
            # Unlocked: Interactive, Standard Window Frame for Resizing
            self.setWindowFlag(Qt.WindowTransparentForInput, False)
            self.setWindowFlag(Qt.FramelessWindowHint, False)
        
        # Always keep these
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.Tool, True)
        
        self.show()

    @Slot(str, str)
    def add_message(self, role, text):
        """
        role: 'System', 'Transcript', 'AI'
        """
        color = config_manager.get("font_color", "#FFFFFF")
        prefix = ""
        
        if role == "Transcript":
            color = "#AAAAAA" # Gray for raw transcript
            prefix = "🎤 "
        elif role == "AI":
            color = config_manager.get("font_color", "#FFFFFF") # User color for AI
            prefix = "🤖 "
        else:
            color = "#FFFF00" # Yellow for system
            prefix = "⚙️ "

        # Smart Appending: If same role (and it's Transcript), append to same line
        if self.last_role == role and role == "Transcript":
            self.text_browser.moveCursor(self.text_browser.textCursor().MoveOperation.End)
            # Add a space before the new text
            html = f'<span style="color: {color};"> {text}</span>'
            self.text_browser.insertHtml(html)
        else:
            # New block
            html = f'<div style="margin-bottom: 10px;"><span style="color: {color}; font-weight: bold;">{prefix}{role}:</span> <span style="color: {color};">{text}</span></div>'
            self.text_browser.append(html)
        
        self.last_role = role
        
        # Auto scroll to bottom
        self.text_browser.moveCursor(self.text_browser.textCursor().MoveOperation.End)

    @Slot(str)
    def scroll_content(self, direction):
        scrollbar = self.text_browser.verticalScrollBar()
        step = 50
        if direction == "up":
            scrollbar.setValue(scrollbar.value() - step)
        elif direction == "down":
            scrollbar.setValue(scrollbar.value() + step)

    @Slot(str)
    def update_status(self, text):
        # For simple status updates, we can just append a system message
        self.add_message("System", text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
            config_manager.set("overlay_x", self.x())
            config_manager.set("overlay_y", self.y())

    def resizeEvent(self, event):
        config_manager.set("overlay_width", self.width())
        config_manager.set("overlay_height", self.height())
        super().resizeEvent(event)
