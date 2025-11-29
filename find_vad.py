import torch
import os
import shutil

try:
    hub_dir = torch.hub.get_dir()
    vad_dir = os.path.join(hub_dir, 'snakers4_silero-vad_master')
    
    # Search for the file
    found = False
    for root, dirs, files in os.walk(vad_dir):
        if 'silero_vad.jit' in files:
            src = os.path.join(root, 'silero_vad.jit')
            dst_dir = os.path.join(os.getcwd(), 'assets')
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            dst = os.path.join(dst_dir, 'silero_vad.jit')
            shutil.copy2(src, dst)
            print(f"File copied to {dst}")
            found = True
            break
    
    if not found:
        print("silero_vad.jit not found in cache.")
        # Trigger download if not found
        print("Downloading model...")
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True)
        # Try finding again
        # ... (simplified for now)

except Exception as e:
    print(f"Error: {e}")
