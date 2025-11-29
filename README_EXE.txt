Meeting Assistant
=================

Thank you for using Meeting Assistant!

🚀 How to Run:
1.  **Configuration**:
    - A `config.json` file has been created for you in this folder.
    - Open it with Notepad.
    - If you want to use AI features (Summarization, Translation) or Cloud Transcription, paste your OpenAI API Key into the `"openai_api_key"` field.
    - You can also adjust settings like `font_size`, `overlay_opacity`, etc., in this file.

2.  **Start the App**:
    - Double-click `MeetingAssistant.exe`.
    - The overlay should appear at the top of your screen.

3.  **Controls**:
    - **Ctrl + Alt + S**: Start / Stop Listening
    - **Ctrl + Alt + O**: Toggle Overlay Visibility
    - **Ctrl + Alt + P**: Open Settings Window
    - **Ctrl + Alt + Enter**: Send text to AI
    - **Ctrl + Alt + Backspace**: Clear text
    - **Ctrl + Alt + Q**: Exit Applicationæ

🎧 Audio Setup (Crucial):
To let the app "hear" the meeting while you still hear it in your headphones:
1.  **Windows Sound Settings**:
    - Open **Sound Control Panel** (Search "Change system sounds" in Windows Start).
    - Go to the **Recording** tab.
    - Find **CABLE Output**, right-click > **Properties**.
    - Go to the **Listen** tab.
    - Check **"Listen to this device"**.
    - Under "Playback through this device", select your **Headphones/Speakers**.
    - Click Apply/OK.
2.  **Meeting App (Zoom/Teams)**:
    - In the meeting app's Audio Settings, set **Speaker** to **CABLE Input**.

🧪 Testing with YouTube (Quick Check):
Want to test if it works without a real meeting?
1.  **Open YouTube** in your browser (Chrome/Edge).
2.  **Route Browser Audio**:
    - Go to **Windows Settings > System > Sound > Volume mixer**.
    - Find your browser in the "Apps" list.
    - Change the **Output device** to **CABLE Input**.
3.  **Run the App**:
    - Open Settings (`Ctrl + Alt + P`).
    - Ensure Input Device is **CABLE Output**.
    - Start Listening (`Ctrl + Alt + S`).
4.  **Play Video**: The app should transcribe the video audio!

📦 Sharing / Installing on a New PC:
If you want to run this on another computer, follow these steps:
1.  **Copy the Entire Folder**: Do NOT just copy the `.exe` file. You must copy the entire `MeetingAssistant` folder containing the `_internal` folder and other files.
2.  **Install VB-Audio Cable**: The new computer needs the virtual audio driver. Download and install it from: https://vb-audio.com/Cable/
3.  **Install FFmpeg**: The app needs FFmpeg to process audio.
    - Download from: https://ffmpeg.org/download.html
    - Extract it and add the `bin` folder to the System PATH.
4.  **Update Config**: Open `config.json` on the new PC and ensure the OpenAI API Key is set if needed.

⚠️ Troubleshooting:
- **"FFmpeg not found"**: You must have FFmpeg installed on your computer and added to your System PATH.
- **App closes immediately**:
    - Try running the `.exe` as Administrator.
    - Check the `logs` folder (if created) for error details.
