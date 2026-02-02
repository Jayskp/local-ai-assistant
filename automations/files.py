import os
import shutil

DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

def organize_downloads():
    for file in os.listdir(DOWNLOADS):
        full_path = os.path.join(DOWNLOADS, file)

        if os.path.isfile(full_path):
            ext = file.split(".")[-1]
            folder = os.path.join(DOWNLOADS, ext.upper())

            os.makedirs(folder, exist_ok=True)
            shutil.move(full_path, os.path.join(folder, file))
