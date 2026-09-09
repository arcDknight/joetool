"""
IKB21303 - Assignment 2: Image Steganography Tool
Task 1 (Adib) - Core Tool: LSB hide/extract engine, load cover image,
save stego.png, basic error handling.
"""

from PIL import Image
import os


def _bytes_to_bits(data: bytes):
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _bits_to_bytes(bits):
    data = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        byte = 0
        for bit in chunk:
            byte = (byte << 1) | bit
        data.append(byte)
    return bytes(data)


def load_cover_image(path: str) -> Image.Image:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Cover image not found: {path}")
    try:
        img = Image.open(path)
    except Exception as e:
        raise ValueError(f"Could not open '{path}' as an image: {e}")
    return img.convert("RGB")


def _build_payload(secret_path: str) -> bytes:
    if not os.path.isfile(secret_path):
        raise FileNotFoundError(f"Secret file not found: {secret_path}")

    with open(secret_path, "rb") as f:
        secret_data = f.read()

    filename = os.path.basename(secret_path)
    filename_bytes = filename.encode("utf-8")
    if len(filename_bytes) > 255:
        raise ValueError("Secret filename is too long (max 255 bytes).")

    header = bytes([len(filename_bytes)]) + filename_bytes
    header += len(secret_data).to_bytes(4, byteorder="big")
    return header + secret_data


def hide_file(cover_path: str, secret_path: str, output_path: str = "stego.png") -> str:
    cover_img = load_cover_image(cover_path)
    payload_bits = _bytes_to_bits(_build_payload(secret_path))

    width, height = cover_img.size
    capacity_bits = width * height * 3

    if len(payload_bits) > capacity_bits:
        raise ValueError(
            f"Secret file too large for this cover image. "
            f"Need {len(payload_bits)} bits, capacity is {capacity_bits} bits. "
            f"Use a bigger cover image or a smaller secret file."
        )

    if not output_path.lower().endswith(".png"):
        raise ValueError("Output must be .png (PNG is lossless; JPG would destroy the hidden bits).")

    pixels = list(cover_img.getdata())
    new_pixels = []
    bit_index = 0
    total_bits = len(payload_bits)

    for r, g, b in pixels:
        if bit_index < total_bits:
            r = (r & ~1) | payload_bits[bit_index]
            bit_index += 1
        if bit_index < total_bits:
            g = (g & ~1) | payload_bits[bit_index]
            bit_index += 1
        if bit_index < total_bits:
            b = (b & ~1) | payload_bits[bit_index]
            bit_index += 1
        new_pixels.append((r, g, b))

    stego_img = Image.new("RGB", cover_img.size)
    stego_img.putdata(new_pixels)
    stego_img.save(output_path, "PNG")

    print(f"[hide_file] '{secret_path}' hidden inside '{cover_path}' -> '{output_path}'")
    return output_path


def extract_file(stego_path: str, output_dir: str = ".") -> str:
    if not os.path.isfile(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")

    stego_img = Image.open(stego_path).convert("RGB")
    pixels = list(stego_img.getdata())

    bits = []
    for r, g, b in pixels:
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

    fname_len = _bits_to_bytes(bits[0:8])[0]
    fname_end = 8 + fname_len * 8
    filename = _bits_to_bytes(bits[8:fname_end]).decode("utf-8", errors="replace")

    len_end = fname_end + 32
    data_len = int.from_bytes(_bits_to_bytes(bits[fname_end:len_end]), byteorder="big")

    data_end = len_end + data_len * 8
    if data_end > len(bits):
        raise ValueError("Stego image is corrupted or has no valid hidden data.")

    secret_data = _bits_to_bytes(bits[len_end:data_end])

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as f:
        f.write(secret_data)

    print(f"[extract_file] hidden file recovered -> '{output_path}'")
    return output_path


if __name__ == "__main__":
    print("Steganography core engine ready. Import hide_file() / extract_file() to use it.")
