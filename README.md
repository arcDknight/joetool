Core Tool (with GUI)

## Folder contents
- `stego_engine.py` - the core LSB hide/extract engine 
- `gui_app.py` - visual interface: load images, hide/extract, see histograms + amplified diff
- `demo.py` - simple command-line version (no GUI) if you just want a quick test
- `zombie_cover.jpg` - sample cover image
- `sample_secret.txt` / `sample_secret_image.png` - sample secret files to test with

## Setup (only needed once)
Open a terminal in this folder and run:
```
pip install pillow numpy matplotlib
```
(tkinter, used for the GUI window itself, comes built into Python already on Windows.)

## Running the GUI
```
python gui_app.py
```

A window will open with 4 buttons across the top:

1. **Load Cover Image** - pick the picture you want to hide something inside (try `zombie_cover.jpg`)
2. **Load Secret File** - pick the file you want hidden (try `sample_secret.txt` or `sample_secret_image.png`)
3. **Hide -> Save Stego** - runs the hiding process and shows you three panels:
   - **Cover Image** - your original picture
   - **Stego Image** - the picture with the secret now hidden inside (looks identical to the eye)
   - **Amplified Difference** - a zoomed-in, color-boosted strip showing exactly which pixels changed. LSB steganography only changes pixels by 1 out of 255, so this view multiplies that tiny difference so you can actually see where the hidden data lives.
   - Below that: **RGB histograms** comparing the Red/Green/Blue color distributions of the cover vs stego image side by side.
4. **Extract from Stego** - pulls the hidden file back out of the stego image and saves it wherever you choose. Use this to prove the hidden data survives correctly.

## Running the simple command-line version instead
```
python demo.py
```
This does the same hide -> extract -> compare cycle without any window, just printed text output - useful if you only need a quick terminal screenshot.
