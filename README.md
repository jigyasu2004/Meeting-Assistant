# Real-Time Meeting Assistant Overlay

A powerful, transparent, always-on-top desktop overlay that provides real-time speech-to-text and translation for your meetings (Zoom, Google Meet, Teams, etc.).

## 🚀 Features

- **Real-time Transcription**: Uses OpenAI Whisper (Local GPU or Cloud) to transcribe speech.
- **AI Assistant**: Integrate with **any OpenAI model** (default: `gpt-5.1`) to perform tasks on your meeting transcripts.
- **Versatile Use Cases**: It's not just for translation! You can ask the AI to:
    - **Summarize** the discussion so far.
    - **Extract action items** or to-do lists.
    - **Draft email responses** based on the conversation.
    - **Translate** to any language.
    - **Answer questions** about what was just said.
- **Transparent Overlay**: Click-through, adjustable overlay that sits on top of your meeting window.
- **Smart Audio Capture**: Uses Silero VAD to only process speech, saving resources.
- **Global Hotkeys**: Control the app from anywhere using `Ctrl + Alt` shortcuts.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.10 or 3.11**
    - [Download Python](https://www.python.org/downloads/)
2.  **FFmpeg** (Required for Whisper audio processing)
    - [Download FFmpeg](https://ffmpeg.org/download.html)
    - **Important**: You must add the `bin` folder of FFmpeg to your System PATH environment variable.
3.  **VB-Audio Virtual Cable** (To route meeting audio to the app)
    - [Download VB-Cable](https://vb-audio.com/Cable/)
    - Install the driver and restart your computer if prompted.

---

## 📥 Installation

1.  **Navigate to the project folder**:
    ```bash
    cd project
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**:
    - **Windows**:
      ```bash
      venv\Scripts\activate
      ```

4.  **Install PyTorch with CUDA (GPU) Support**:
    - To make transcription fast, you need to run Whisper on your NVIDIA GPU.
    - Run the following command (for CUDA 11.8/12.1):
      ```bash
      pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
      ```
    - *If you don't have an NVIDIA GPU, you can skip this, but transcription will be slower on CPU.*

5.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Setup Configuration**:
    - Copy `config.example.json` to `config.json`:
      ```bash
      copy config.example.json config.json
      ```
    - Open `config.json` and add your OpenAI API Key if using Cloud mode or LLM features.

---

## 🎧 Audio Setup (Crucial Step)

To let the app "hear" your meeting while you still hear it in your headphones, follow this setup:

1.  **Windows Sound Settings**:
    - Go to **Settings > System > Sound**.
    - Open **Sound Control Panel** (usually on the right or bottom).
    - Go to the **Recording** tab.
    - Find **CABLE Output**, right-click > **Properties**.
    - Go to the **Listen** tab.
    - Check **"Listen to this device"**.
    - Under "Playback through this device", select your **Headphones/Speakers**.
    - Click Apply/OK.

2.  **Meeting App (Zoom/Teams/Meet)**:
    - Go to the Audio Settings of your meeting app.
    - Set the **Speaker/Output** to **CABLE Input (VB-Audio Virtual Cable)**.
    
    *Now, audio goes from Zoom -> Cable Input -> Cable Output -> App (and your Headphones).*

### 🧪 Testing with YouTube (Quick Start)

Want to test the app without a real meeting? You can use a YouTube video.

1.  **Open YouTube** in your browser.
2.  **Route Browser Audio**:
    - Go to **Windows Settings > System > Sound > Volume mixer**.
    - Find your browser (e.g., Chrome, Edge) in the "Apps" list.
    - Change the **Output device** for the browser to **CABLE Input (VB-Audio Virtual Cable)**.
3.  **Configure App**:
    - Open the Meeting Assistant App.
    - Go to Settings (`Ctrl + Alt + P`).
    - Set **Input Device** to **CABLE Output**.
4.  **Play Video**: Start the YouTube video. The app should now transcribe and translate it in real-time!


---

## ▶️ How to Run

1.  **Start the Application**:
    ```bash
    python main.py
    ```
    *Or double-click `run.bat` if you created it.*

2.  **Configure Settings**:
    - Press `Ctrl + Alt + P` to open Settings.
    - **Input Device**: Select **"CABLE Output (VB-Audio Virtual Cable)"**.
    - **Transcription Mode**: Choose "Local" (Free, uses GPU) or "Cloud" (High accuracy, costs money).
    - **OpenAI API Key**: Required if using "Cloud" mode or for AI features.
    - **Prompt Template**: Customize how the LLM processes text (e.g., "Summarize this", "Translate to Spanish").

3.  **Start Transcription**:
    - Press `Ctrl + Alt + S` to start listening.
    - The overlay will show "Listening...".

---

## 📦 Building an Executable (.exe)

Want to run the app without Python installed? You can build a standalone `.exe` file.

1.  **Run the Build Script**:
    - Double-click `build_exe.bat`.
    - Wait for the process to finish (it may take a few minutes).

2.  **Locate the App**:
    - Go to the `dist/MeetingAssistant` folder.
    - You will find `MeetingAssistant.exe` there.
    - You can zip this folder and share it with others!
    
[Download EXE](https://drive.google.com/drive/folders/1Lsg8HkqLl2vg7EAO4YAqVhHz6wVjDyL1?usp=sharing)

---

## ⌨️ Hotkeys

| Hotkey | Action |
| :--- | :--- |
| `Ctrl + Alt + S` | Start / Stop Listening |
| `Ctrl + Alt + O` | Toggle Overlay Visibility |
| `Ctrl + Alt + P` | Open Settings Window |
| `Ctrl + Alt + C` | Copy Transcript to Clipboard |
| `Ctrl + Alt + Enter` | Send Accumulated Text to AI |
| `Ctrl + Alt + Backspace` | Clear Transcript History |
| `Ctrl + Alt + Up` | Scroll Overlay Up |
| `Ctrl + Alt + Down` | Scroll Overlay Down |
| `Ctrl + Alt + Q` | Exit Application |

---

## ❓ Troubleshooting

-   **"FileNotFoundError: [WinError 2] The system cannot find the file specified"**:
    - This usually means **FFmpeg** is not installed or not in your PATH.

-   **Transcription is very slow**:
    - Ensure you installed the CUDA version of PyTorch.
    - Check if `torch.cuda.is_available()` returns `True` in Python.
    - In Settings, ensure "Local" mode is selected and your GPU is capable.

-   **I can't hear the meeting audio**:
    - Double-check the "Listen to this device" step in the Audio Setup section.

-   **Overlay blocks my mouse clicks**:
    - Open Settings (`Ctrl + Alt + P`) and ensure **"Lock Overlay (Uncheck to Resize & Move)"** is checked.
