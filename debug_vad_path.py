import torch
import os

hub_dir = torch.hub.get_dir()
print(f"Torch Hub Dir: {hub_dir}")

if os.path.exists(hub_dir):
    print("Contents of Hub Dir:")
    for root, dirs, files in os.walk(hub_dir):
        for file in files:
            if "silero" in file or "vad" in file:
                print(os.path.join(root, file))
else:
    print("Hub dir does not exist.")
