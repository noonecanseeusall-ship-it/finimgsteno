# ==============================
# 🧠 IMAGE STEGANOGRAPHY ENCODER (No metadata)
# ==============================

from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from google.colab import files
import os, time

# -----------------------------
# 🔐 Encryption
# -----------------------------
def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    cipher = Fernet(key)
    return cipher.encrypt(message.encode())

# -----------------------------
# 🧩 Embed Data in Image
# -----------------------------
def embed_data_in_image(image_path, data_bytes, output_path="stego_image.png"):
    img = Image.open(image_path)
    arr = np.array(img)
    flat = arr.flatten()

    # Convert data length to 32-bit binary header
    data_len = len(data_bytes)
    header = np.unpackbits(np.array([data_len >> i & 0xFF for i in (24,16,8,0)], dtype=np.uint8))
    data_bits = np.unpackbits(np.frombuffer(data_bytes, dtype=np.uint8))
    bits = np.concatenate([header, data_bits])

    capacity = len(flat)
    if len(bits) > capacity:
        raise ValueError("Message too large to fit in this image.")

    flat[:len(bits)] = (flat[:len(bits)] & 254) | bits
    new_arr = flat.reshape(arr.shape)
    stego_img = Image.fromarray(new_arr.astype(np.uint8))
    stego_img.save(output_path)
    return output_path

# -----------------------------
# 🚀 Encode Message
# -----------------------------
def encode_message(image_path, message):
    key = generate_key()
    encrypted = encrypt_message(message, key)
    output_path = "stego_image.png"
    embed_data_in_image(image_path, encrypted, output_path)
    return key.decode()

# -----------------------------
# 🎯 User Interaction
# -----------------------------
print("📤 Upload your image (PNG/JPG):")
uploaded = files.upload()
img_name = list(uploaded.keys())[0]

secret_text = input("📝 Enter the secret text you want to hide: ")

# Encode message
passkey = encode_message(img_name, secret_text)
print(f"\n✅ Message successfully hidden in image!")
print(f"🔑 Save this passkey: {passkey}")

# ✅ Download output
output_path = "stego_image.png"
if os.path.exists(output_path):
    print("\n📥 Preparing stego image for download...")
    time.sleep(1)
    files.download(output_path)
else:
    print("❌ Error: Stego image not created.")
