# 🔐 Image Steganography Web App

A beautiful web interface for hiding secret messages inside images using steganography and encryption.

## Features

- 🔒 **Encode**: Hide encrypted messages inside images
- 🔓 **Decode**: Extract hidden messages using a passkey
- 🎨 Modern, responsive UI with drag-and-drop support
- 🔐 Secure encryption using Fernet (symmetric encryption)
- 📱 Works on desktop and mobile browsers

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and go to:
```
http://localhost:5000
```

3. **To Encode**:
   - Upload an image (PNG/JPG)
   - Enter your secret message
   - Click "Hide Message"
   - Save the passkey and download the encoded image

4. **To Decode**:
   - Upload the encoded image
   - Enter the passkey
   - Click "Reveal Message"

## How It Works

- Uses LSB (Least Significant Bit) steganography to hide data in image pixels
- Messages are encrypted with Fernet before embedding
- The passkey is required to decrypt and read the hidden message
- Original encode/decode logic preserved from Colab version

## Security Note

Keep your passkey safe! Without it, the hidden message cannot be recovered.
