from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
import os
import base64
from io import BytesIO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===========================
# ENCODING FUNCTIONS
# ===========================
def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    cipher = Fernet(key)
    return cipher.encrypt(message.encode())

def embed_data_in_image(image_path, data_bytes, output_path):
    img = Image.open(image_path)
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    arr = np.array(img)
    flat = arr.flatten()

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

def encode_message(image_path, message, output_path):
    key = generate_key()
    encrypted = encrypt_message(message, key)
    embed_data_in_image(image_path, encrypted, output_path)
    return key.decode()

# ===========================
# DECODING FUNCTIONS
# ===========================
def decrypt_message(encrypted_message, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message).decode()

def extract_data_from_image(image_path):
    img = Image.open(image_path)
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    arr = np.array(img)
    flat = arr.flatten()

    header_bits = flat[:32] & 1
    header_bytes = np.packbits(header_bits)
    data_len = int.from_bytes(header_bytes.tobytes(), "big")

    bits = flat[32:32 + data_len * 8] & 1
    data_bytes = np.packbits(bits)
    return data_bytes.tobytes()

def decode_message(image_path, key):
    data_bytes = extract_data_from_image(image_path)
    return decrypt_message(data_bytes, key.encode())

# ===========================
# ROUTES
# ===========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        image = request.files['image']
        message = request.form.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Save uploaded image
        input_path = os.path.join(UPLOAD_FOLDER, 'input_' + image.filename)
        output_filename = 'stego_' + image.filename.rsplit('.', 1)[0] + '.png'
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        image.save(input_path)
        
        # Encode message
        passkey = encode_message(input_path, message, output_path)
        
        # Cleanup input
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'passkey': passkey,
            'filename': output_filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        image = request.files['image']
        passkey = request.form.get('passkey', '')
        
        if not passkey:
            return jsonify({'error': 'No passkey provided'}), 400
        
        # Save uploaded image
        input_path = os.path.join(UPLOAD_FOLDER, 'decode_' + image.filename)
        image.save(input_path)
        
        # Decode message
        decoded_message = decode_message(input_path, passkey)
        
        # Cleanup
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'message': decoded_message
        })
    
    except Exception as e:
        print(f"Decode error: {str(e)}")  # Log the actual error
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to decode: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
