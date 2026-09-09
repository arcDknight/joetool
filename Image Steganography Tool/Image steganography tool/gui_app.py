"""
IKB21303 Assignment 2 - Image Steganography Tool (GUI Version)
Built on top of stego_engine.py (Task 1 - Core Tool).

Features:
- Load a cover image and a secret file
- Hide the secret and save the stego image
- Extract a secret from a stego image
- Side-by-side view: Cover | Stego | Amplified Difference
- RGB channel histogram comparison (Cover vs Stego)

Run with:  python gui_app.py
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from PIL import Image, ImageTk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from stego_engine import hide_file, extract_file, load_cover_image


PREVIEW_SIZE = (220, 220)   # thumbnail size for the 3 image panels
AMPLIFY_FACTOR = 255        # LSB changes are only +/-1, so boost hard to make them visible


class StegoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IKB21303 - Image Steganography Tool")
        self.geometry("1050x780")
        self.configure(bg="#1e1e1e")

        self.cover_path = None
        self.secret_path = None
        self.stego_path = None

        self._build_top_bar()
        self._build_image_panels()
        self._build_histogram_area()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_top_bar(self):
        bar = tk.Frame(self, bg="#252526", pady=10)
        bar.pack(fill="x")

        tk.Button(bar, text="1. Load Cover Image", command=self.load_cover,
                  width=20, bg="#3a3d41", fg="white").grid(row=0, column=0, padx=8)
        tk.Button(bar, text="2. Load Secret File", command=self.load_secret,
                  width=20, bg="#3a3d41", fg="white").grid(row=0, column=1, padx=8)
        tk.Button(bar, text="3. Hide -> Save Stego", command=self.run_hide,
                  width=20, bg="#0e639c", fg="white").grid(row=0, column=2, padx=8)
        tk.Button(bar, text="4. Extract from Stego", command=self.run_extract,
                  width=20, bg="#0e639c", fg="white").grid(row=0, column=3, padx=8)

        self.cover_label = tk.Label(bar, text="Cover: (none)", bg="#252526", fg="#cccccc")
        self.cover_label.grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="w", padx=8)
        self.secret_label = tk.Label(bar, text="Secret: (none)", bg="#252526", fg="#cccccc")
        self.secret_label.grid(row=1, column=2, columnspan=2, pady=(8, 0), sticky="w", padx=8)

    def _build_image_panels(self):
        frame = tk.Frame(self, bg="#1e1e1e", pady=10)
        frame.pack(fill="x")

        self.cover_panel = self._make_panel(frame, "Cover Image", 0)
        self.stego_panel = self._make_panel(frame, "Stego Image", 1)
        self.diff_panel = self._make_panel(frame, f"Amplified Difference (x{AMPLIFY_FACTOR})", 2)

    def _make_panel(self, parent, title, col):
        box = tk.Frame(parent, bg="#1e1e1e")
        box.grid(row=0, column=col, padx=15)
        tk.Label(box, text=title, bg="#1e1e1e", fg="#e0e0e0",
                 font=("Segoe UI", 10, "bold")).pack()
        img_label = tk.Label(box, bg="#2d2d30", width=PREVIEW_SIZE[0], height=PREVIEW_SIZE[1])
        img_label.pack(pady=5)
        return img_label

    def _build_histogram_area(self):
        tk.Label(self, text="RGB Channel Histograms - Cover vs Stego",
                 bg="#1e1e1e", fg="#e0e0e0", font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))

        self.fig = Figure(figsize=(10, 3.2), dpi=90)
        self.fig.patch.set_facecolor("#1e1e1e")
        self.axes = self.fig.subplots(1, 3)
        for ax, name in zip(self.axes, ["Red", "Green", "Blue"]):
            ax.set_title(name, color="white", fontsize=9)
            ax.set_facecolor("#252526")
            ax.tick_params(colors="white", labelsize=7)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

    def _build_status_bar(self):
        self.status = tk.Label(self, text="Ready. Load a cover image and a secret file to begin.",
                                bg="#0e639c", fg="white", anchor="w", padx=10, pady=6)
        self.status.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Button actions
    # ------------------------------------------------------------------

    def load_cover(self):
        path = filedialog.askopenfilename(
            title="Choose a cover image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not path:
            return
        self.cover_path = path
        self.cover_label.config(text=f"Cover: {os.path.basename(path)}")
        self._show_image(self.cover_panel, Image.open(path).convert("RGB"))
        self.set_status(f"Cover image loaded: {os.path.basename(path)}")

    def load_secret(self):
        path = filedialog.askopenfilename(title="Choose a secret file to hide")
        if not path:
            return
        self.secret_path = path
        self.secret_label.config(text=f"Secret: {os.path.basename(path)}")
        self.set_status(f"Secret file loaded: {os.path.basename(path)}")

    def run_hide(self):
        if not self.cover_path or not self.secret_path:
            messagebox.showwarning("Missing input", "Please load both a cover image and a secret file first.")
            return
        try:
            out_dir = os.path.dirname(self.cover_path)
            output_path = os.path.join(out_dir, "stego_gui_output.png")
            hide_file(self.cover_path, self.secret_path, output_path)
            self.stego_path = output_path

            self._show_image(self.stego_panel, Image.open(output_path).convert("RGB"))
            self._show_amplified_diff()
            self._update_histograms()

            cover_size = os.path.getsize(self.cover_path)
            stego_size = os.path.getsize(output_path)
            self.set_status(
                f"Hidden successfully -> {os.path.basename(output_path)} "
                f"(cover: {cover_size:,} bytes, stego: {stego_size:,} bytes)"
            )
        except Exception as e:
            messagebox.showerror("Hide failed", str(e))
            self.set_status(f"Error: {e}")

    def run_extract(self):
        if not self.stego_path:
            messagebox.showwarning("Missing stego image", "Hide a file first, or load a stego image.")
            return
        try:
            out_dir = filedialog.askdirectory(title="Choose where to save the extracted file")
            if not out_dir:
                return
            result_path = extract_file(self.stego_path, out_dir)
            messagebox.showinfo("Extraction complete", f"Recovered file saved to:\n{result_path}")
            self.set_status(f"Extracted -> {result_path}")
        except Exception as e:
            messagebox.showerror("Extract failed", str(e))
            self.set_status(f"Error: {e}")

    # ------------------------------------------------------------------
    # Visual helpers
    # ------------------------------------------------------------------

    def _show_image(self, label_widget, pil_img, nearest=False):
        thumb = pil_img.copy()
        resample = Image.NEAREST if nearest else Image.BICUBIC
        thumb.thumbnail(PREVIEW_SIZE, resample=resample)
        tk_img = ImageTk.PhotoImage(thumb)
        label_widget.config(image=tk_img)
        label_widget.image = tk_img  # keep a reference so it isn't garbage collected

    def _show_amplified_diff(self):
        """
        Show WHERE the hidden bits changed, by exaggerating the tiny pixel
        differences. LSB changes are only +/-1, so a small secret file only
        touches a thin strip of pixels near the top of the image (that's
        how LSB embedding fills pixels left-to-right, top-to-bottom). We
        crop tightly around that changed region and zoom in, otherwise a
        small secret would shrink down to nothing in a full-image thumbnail.
        """
        cover_img = Image.open(self.cover_path).convert("RGB")
        stego_img = Image.open(self.stego_path).convert("RGB")
        cover_img = cover_img.resize(stego_img.size)

        cover_arr = np.array(cover_img).astype(np.int16)
        stego_arr = np.array(stego_img).astype(np.int16)

        diff = np.abs(stego_arr - cover_arr)
        changed_mask = diff.sum(axis=2) > 0
        amplified = np.clip(diff * AMPLIFY_FACTOR, 0, 255).astype(np.uint8)

        rows = np.where(changed_mask.any(axis=1))[0]
        if len(rows) == 0:
            # nothing changed at all (e.g. hide failed) - show as-is
            diff_img = Image.fromarray(amplified, mode="RGB")
            self._show_image(self.diff_panel, diff_img)
            return

        height = stego_img.size[1]
        top = max(0, rows.min() - 2)
        bottom = min(height, rows.max() + 3)
        # Make sure the crop has enough height to actually be visible when zoomed
        min_crop_height = 8
        if bottom - top < min_crop_height:
            bottom = min(height, top + min_crop_height)

        crop = amplified[top:bottom, :, :]
        diff_img = Image.fromarray(crop, mode="RGB")
        # Deliberately stretch to fill the panel (ignoring aspect ratio) -
        # a real diff strip can be just 1-2 pixels tall, which would
        # otherwise vanish almost completely when thumbnailed normally.
        # Nearest-neighbor keeps each changed pixel a crisp, visible block.
        stretched = diff_img.resize(PREVIEW_SIZE, resample=Image.NEAREST)
        tk_img = ImageTk.PhotoImage(stretched)
        self.diff_panel.config(image=tk_img)
        self.diff_panel.image = tk_img

    def _update_histograms(self):
        cover_arr = np.array(Image.open(self.cover_path).convert("RGB"))
        stego_arr = np.array(Image.open(self.stego_path).convert("RGB").resize(
            (cover_arr.shape[1], cover_arr.shape[0])
        ))

        colors = ["#e06c75", "#98c379", "#61afef"]  # red, green, blue accents
        titles = ["Red", "Green", "Blue"]

        for i, (ax, title, color) in enumerate(zip(self.axes, titles, colors)):
            ax.clear()
            ax.set_title(title, color="white", fontsize=9)
            ax.set_facecolor("#252526")
            ax.hist(cover_arr[:, :, i].ravel(), bins=64, range=(0, 255),
                     color=color, alpha=0.55, label="Cover")
            ax.hist(stego_arr[:, :, i].ravel(), bins=64, range=(0, 255),
                     color="white", alpha=0.35, label="Stego")
            ax.tick_params(colors="white", labelsize=7)
            ax.legend(fontsize=7, facecolor="#1e1e1e", labelcolor="white")

        self.fig.tight_layout()
        self.canvas.draw()

    def set_status(self, text):
        self.status.config(text=text)


if __name__ == "__main__":
    app = StegoGUI()
    app.mainloop()
