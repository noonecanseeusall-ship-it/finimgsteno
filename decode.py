# ==============================
# IMAGE STEGANOGRAPHY DECODER (No metadata)
# ==============================

from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from google.colab import files

# -----------------------------
# Decryption
# -----------------------------
def decrypt_message(encrypted_message, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message).decode()

# -----------------------------
# Extract Data from Image
# -----------------------------
def extract_data_from_image(image_path):
    img = Image.open(image_path)
    arr = np.array(img)
    flat = arr.flatten()

    # Read first 32 bits (header) = message length
    header_bits = flat[:32] & 1
    header_bytes = np.packbits(header_bits)
    data_len = int.from_bytes(header_bytes.tobytes(), "big")

    # Extract message bits
    bits = flat[32:32 + data_len * 8] & 1
    data_bytes = np.packbits(bits)
    return data_bytes.tobytes()

# -----------------------------
# Decode Message
# -----------------------------
def decode_message(image_path, key):
    data_bytes = extract_data_from_image(image_path)
    return decrypt_message(data_bytes, key.encode())

# -----------------------------
# User Interaction
# -----------------------------
print("Upload the encoded (stego) image:")
uploaded = files.upload()
stego_img = list(uploaded.keys())[0]

passkey = input("Enter the secret passkey: ")

try:
    decoded_text = decode_message(stego_img, passkey)
    print("\nDecoded Message:")
    print(decoded_text)
except Exception as e:
    print("\n❌ Failed to decode! Check your passkey or image.")
    print("Error:", e)
