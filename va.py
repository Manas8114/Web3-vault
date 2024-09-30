from flask import Flask, request, send_file, render_template
from cryptography.fernet import Fernet
import os
import io

app = Flask(__name__)

# Generate a key and store it in a file
def generate_key():
    key = Fernet.generate_key()
    with open("vault_key.key", "wb") as key_file:
        key_file.write(key)

# Load the previously generated key
def load_key():
    return open("vault_key.key", "rb").read()

# Encrypt file content
def encrypt_file(file_data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(file_data)
    return encrypted_data

# Decrypt file content
def decrypt_file(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data

# Add a file to the vault (encrypt it and store it)
def add_file_to_vault(filename, key, file_data):
    encrypted_data = encrypt_file(file_data, key)
    with open(f"vault_{filename}", "wb") as vault_file:
        vault_file.write(encrypted_data)

# Retrieve a file from the vault (decrypt and return it)
def retrieve_file_from_vault(filename, key):
    vault_filename = f"vault_{filename}"
    if os.path.exists(vault_filename):
        with open(vault_filename, "rb") as vault_file:
            encrypted_data = vault_file.read()
            return decrypt_file(encrypted_data, key)
    return None

# Home page with upload and download forms
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        if not os.path.exists("vault_key.key"):
            generate_key()
        key = load_key()

        file_data = file.read()
        add_file_to_vault(file.filename, key, file_data)
        return f"File {file.filename} has been encrypted and stored."

# Route to handle file downloads
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if not os.path.exists(f"vault_{filename}"):
        return "File not found in vault."

    key = load_key()
    file_data = retrieve_file_from_vault(filename, key)

    if file_data:
        # Provide the decrypted file for download
        return send_file(
            io.BytesIO(file_data),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=filename
        )
    else:
        return "File could not be decrypted or found."

if __name__ == "__main__":
    app.run(debug=True)
