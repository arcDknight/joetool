"""
Command-line demo - run this if you just want to test the engine
without the GUI. See gui_app.py for the visual version.
"""

import os
from stego_engine import hide_file, extract_file

COVER_IMAGE = "zombie_cover.jpg"
SECRET_FILE = "sample_secret.txt"
OUTPUT_STEGO = "stego.png"
EXTRACT_DIR = "extracted_output"

if __name__ == "__main__":
    print("=== HIDING ===")
    hide_file(COVER_IMAGE, SECRET_FILE, OUTPUT_STEGO)

    print("\n=== EXTRACTING ===")
    extract_file(OUTPUT_STEGO, EXTRACT_DIR)

    print("\n=== FILE SIZE COMPARISON ===")
    cover_size = os.path.getsize(COVER_IMAGE)
    stego_size = os.path.getsize(OUTPUT_STEGO)
    print(f"Cover image size : {cover_size} bytes")
    print(f"Stego image size : {stego_size} bytes")
    print(f"Difference       : {stego_size - cover_size} bytes")
