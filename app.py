import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from blockchain import Blockchain
from database import init_db, register_user, verify_user

app = Flask(__name__)
app.secret_key = '\xb7\x86\xbd\xea\r\xd2\x1e\x16\xee\xea'

# Initialize the database and blockchain
init_db()
blockchain = Blockchain()  # Automatically handles loading or creating the blockchain

# IPFS URL
IPFS_URL = "http://127.0.0.1:5001/api/v0/add"

# Upload file to IPFS
def upload_to_ipfs(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(IPFS_URL, files={'file': f})
    ipfs_hash = response.json()['Hash']
    return ipfs_hash

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Try a different one.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))

    ipfs_hash = session.get('ipfs_hash')  # Retrieve IPFS hash from session
    return render_template('dashboard.html', ipfs_hash=ipfs_hash)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        flash('Please log in to upload files.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            # Upload to IPFS and get the hash
            ipfs_hash = upload_to_ipfs(file_path)

            # Store the IPFS hash in the session
            session['ipfs_hash'] = ipfs_hash

            # Add block to the blockchain
            blockchain.add_block(ipfs_hash)

            flash(f'File uploaded successfully. IPFS Hash: {ipfs_hash}')
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_file():
    verified = None
    block_details = None

    if request.method == 'POST':
        ipfs_hash = request.form['ipfs_hash']
        for block in blockchain.get_chain():
            if block['data'] == ipfs_hash:
                verified = True
                block_details = block
                break
        if not verified:
            verified = False

    return render_template('verify.html', verified=verified, block_details=block_details)

@app.route('/view_blockchain')
def view_blockchain():
    if 'username' not in session:
        flash('Please log in to view the blockchain.')
        return redirect(url_for('login'))

    blockchain_data = blockchain.get_chain()
    return render_template('view_blockchain.html', blockchain=blockchain_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('ipfs_hash', None)
    flash('Logged out successfully.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
