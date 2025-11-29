@echo off
echo ==========================================
echo      Building Meeting Assistant EXE
echo ==========================================

echo 1. Installing PyInstaller...
pip install pyinstaller markdown

echo 2. Cleaning up previous builds...
rmdir /s /q build
rmdir /s /q dist
del *.spec

echo 3. Running PyInstaller...
echo    This may take a few minutes.
pyinstaller --noconfirm --onedir --windowed --name "MeetingAssistant" --collect-all "whisper" --add-data "config.example.json;." --add-data "assets;assets" --hidden-import="torch" --hidden-import="scipy.signal" --hidden-import="scipy.spatial.transform._rotation_groups" main.py

echo 4. Setting up distribution folder...
copy config.example.json dist\MeetingAssistant\config.json
copy README_EXE.txt dist\MeetingAssistant\README.txt

echo ==========================================
echo      Build Complete!
echo ==========================================
echo You can find your app in: dist\MeetingAssistant
start explorer dist\MeetingAssistant
pause
