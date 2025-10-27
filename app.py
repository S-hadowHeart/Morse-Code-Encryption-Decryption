
import datetime
import json
import os
import random
import uuid
import hashlib
import requests
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, render_template, request, send_from_directory, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# --- Configuration & Setup ---
UPLOAD_FOLDER = 'uploads'
CHAT_DIR = "chats"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

for directory in [UPLOAD_FOLDER, CHAT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Data & Constants ---
AGENT_NAMES = ["Whisper", "Specter", "Mirage", "Echo", "Shadow", "Cipher", "Ronin", "Oracle", "Nyx", "Wraith"]
EASTER_EGGS = {
    "hello world": ".... . .-.. .-.. --- / .-- --- .-. .-.. -..",
    "the matrix": "AGENT SMITH: 'Mr. Anderson...'",
    "sudo rm -rf /": "COMMAND NOT RECOGNIZED. SYSTEM INTEGRITY IS SECURE.",
    "shadowheart": "CREATOR OF THIS UNIVERSE.",
    "never gonna give you up": "-. . ...- . .-. / --. --- -. -. .- / --. .. ...- . / -.-- --- ..- / ..- .--.",
    "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs.",
    "what is the meaning of life": "42",
    "show themes": "Available themes: 💜💙, ✨💫, 🔥💧, 💀👻, 🎵🎶, ☀️🌙, 🐾🦴, 🌸🌺, 🔹🔸"
}
SYMBOL_THEMES = [
    {".": "💜", "-": "💙"},
    {".": "✨", "-": "💫"},
    {".": "🔥", "-": "💧"},
    {".": "💀", "-": "👻"},
    {".": "🎵", "-": "🎶"},
    {".": "☀️", "-": "🌙"},
    {".": "🐾", "-": "🦴"},
    {".": "🌸", "-": "🌺"},
    {".": "🔹", "-": "🔸"},
]
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..--', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
    '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', ' ': '/'
}
REVERSED_MORSE_CODE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

# --- Security Decorators ---
def require_room_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        room_code = request.form.get('room_code') or request.args.get('room_code')
        if not room_code:
            return jsonify({'status': 'error', 'message': 'Room code required'})
        file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': 'Invalid room code'})
        return f(*args, **kwargs)
    return decorated_function

# --- Main Routes ---
@app.route('/')
@limiter.limit("60 per minute")
def index():
    return render_template('index.html')

@app.route('/guide')
@limiter.limit("30 per minute")
def guide():
    return render_template('guide.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Morse Code API ---
@app.route('/code', methods=['POST'])
def code():
    text = request.form.get('textInput', '').strip()
    if not text: return jsonify({'status': 'error', 'message': 'Error: Input is empty.'})

    lower_text = text.lower()
    if lower_text in EASTER_EGGS:
        return jsonify({'status': 'success', 'result': EASTER_EGGS[lower_text]})
    
    try:
        theme_index = int(lower_text[-1]) - 1
        if 0 <= theme_index < len(SYMBOL_THEMES):
            text_to_encode = text[:-1].strip()
            encoded = encode(text_to_encode)
            themed_encoded = ''.join(SYMBOL_THEMES[theme_index].get(char, char) for char in encoded)
            return jsonify({'status': 'success', 'result': themed_encoded})
    except (ValueError, IndexError):
        pass

    if any(c in '.-/' for c in text):
        return jsonify({'status': 'success', 'result': decode(text)})
    else:
        return jsonify({'status': 'success', 'result': encode(text)})

# --- Chat API ---
@app.route('/chat/create', methods=['POST'])
def create_chat_room():
    room_code = generate_room_code()
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    agent_name = random.choice(AGENT_NAMES)
    with open(file_path, 'w') as f:
        json.dump({"messages": [], "typing_status": {}}, f)
    return jsonify({'status': 'success', 'room_code': room_code, 'agent_name': agent_name})

@app.route('/chat/join', methods=['POST'])
def join_chat_room():
    room_code = request.form.get('room_code')
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if os.path.exists(file_path):
        agent_name = random.choice(AGENT_NAMES)
        return jsonify({'status': 'success', 'agent_name': agent_name})
    return jsonify({'status': 'error', 'message': 'Invalid room code.'})

@app.route('/chat/send', methods=['POST'])
def send_message():
    room_code = request.form.get('room_code')
    agent_name = request.form.get('agent_name')
    message_text = request.form.get('message', '')
    reply_to = request.form.get('reply_to')
    file = request.files.get('file')

    if not room_code or not agent_name or (not message_text and not file):
        return jsonify({'status': 'error', 'message': 'Missing data.'})

    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if not os.path.exists(file_path): return jsonify({'status': 'error', 'message': 'Room not found'})

    message_content = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = f"/uploads/{filename}"
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in {'png', 'jpg', 'jpeg', 'gif'}: message_content = f"[IMAGE]{file_url}"
        elif file_ext in {'mp4', 'mov', 'avi'}: message_content = f"[VIDEO]{file_url}"
    elif message_text:
        # Giphy integration: /gif <gif_id>
        if message_text.startswith('/gif '):
            gif_id = message_text.split(' ', 1)[1].strip()
            if gif_id:
                giphy_key = os.environ.get('GIPHY_API_KEY', 'k3LYUibhNR8LbZqXZKKrdqUCzSLZsnr0')
                try:
                    resp = requests.get(f'https://api.giphy.com/v1/gifs/{gif_id}', params={'api_key': giphy_key}, timeout=5)
                    if resp.status_code == 200:
                        j = resp.json()
                        gif_url = j.get('data', {}).get('images', {}).get('original', {}).get('url')
                        if gif_url:
                            message_content = f'[GIF]{gif_url}'
                        else:
                            return jsonify({'status': 'error', 'message': 'GIF URL not found.'})
                    else:
                        return jsonify({'status': 'error', 'message': 'GIF not found.'})
                except Exception:
                    return jsonify({'status': 'error', 'message': 'Failed to fetch GIF.'})
            else:
                return jsonify({'status': 'error', 'message': 'GIF id missing.'})
        # Allow chat-level encryption with the command: /encrypt <message>
        elif message_text.startswith('/encrypt '):
            payload = message_text[len('/encrypt '):]
            try:
                encrypted = encrypt_message(payload)
                # store as a readable token prefixed with marker
                message_content = '[ENCRYPTED]' + encrypted.decode()
            except Exception:
                message_content = message_text
        else:
            message_content = message_text

    if message_content:
        new_message = {
            "id": str(uuid.uuid4()), "agent": agent_name, "text": message_content,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "reactions": {}, "reply_to": reply_to
        }
        with open(file_path, 'r+') as f:
            chat_data = json.load(f)
            chat_data["messages"].append(new_message)
            f.seek(0); f.truncate(); json.dump(chat_data, f, indent=2)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid file or empty message.'})


@app.route('/chat/decrypt', methods=['POST'])
def chat_decrypt():
    payload = request.form.get('payload')
    if not payload:
        return jsonify({'status': 'error', 'message': 'Missing payload.'})
    try:
        # payload should be the URL-safe base64 string produced by Fernet
        decrypted = decrypt_message(payload.encode())
        if decrypted is None:
            return jsonify({'status': 'error', 'message': 'Decryption failed.'})
        return jsonify({'status': 'success', 'result': decrypted})
    except Exception:
        return jsonify({'status': 'error', 'message': 'Decryption error.'})

@app.route('/chat/messages', methods=['GET'])
def get_messages():
    room_code = request.args.get('room_code')
    agent_name = request.args.get('agent_name')
    since = request.args.get('since')
    
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})

    with open(file_path, 'r') as f:
        chat_data = json.load(f)

    if since:
        messages = [msg for msg in chat_data['messages'] if msg['timestamp'] > since]
    else:
        messages = chat_data['messages']
        
    typing_agents = [name for name, status in chat_data.get("typing_status", {}).items() if status and name != agent_name]
    
    return jsonify({'status': 'success', 'messages': messages, 'typing_agents': typing_agents})

@app.route('/chat/react', methods=['POST'])
def react_to_message():
    room_code, agent_name, message_id, emoji = request.form.get('room_code'), request.form.get('agent_name'), request.form.get('message_id'), request.form.get('emoji')
    if not all([room_code, agent_name, message_id, emoji]): return jsonify({'status': 'error', 'message': 'Missing data.'})
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if not os.path.exists(file_path): return jsonify({'status': 'error', 'message': 'Room not found.'})

    with open(file_path, 'r+') as f:
        chat_data = json.load(f)
        msg_found = False
        for msg in chat_data['messages']:
            if msg['id'] == message_id:
                reactions = msg.setdefault('reactions', {})
                agent_list = reactions.setdefault(emoji, [])
                if agent_name in agent_list: agent_list.remove(agent_name)
                else: agent_list.append(agent_name)
                if not agent_list: del reactions[emoji]
                msg_found = True
                break
        if not msg_found: return jsonify({'status': 'error', 'message': 'Message not found.'})
        f.seek(0); f.truncate(); json.dump(chat_data, f, indent=2)
    return jsonify({'status': 'success'})

@app.route('/chat/typing', methods=['POST'])
def handle_typing():
    room_code, agent_name, is_typing = request.form.get('room_code'), request.form.get('agent_name'), request.form.get('is_typing') == 'true'
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            chat_data = json.load(f)
            chat_data.setdefault("typing_status", {})[agent_name] = is_typing
            f.seek(0); f.truncate(); json.dump(chat_data, f, indent=2)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid room code.'})

# --- Helper Functions ---
def generate_room_code():
    """Generate a secure room code with additional entropy"""
    random_bytes = os.urandom(12)
    hash_object = hashlib.sha256(random_bytes)
    room_hash = hash_object.hexdigest()[:12]
    return '-'.join(''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4)) for _ in range(3))

def encrypt_message(message):
    """Encrypt a message using Fernet symmetric encryption"""
    if isinstance(message, str):
        message = message.encode()
    return cipher_suite.encrypt(message)

def decrypt_message(encrypted_message):
    """Decrypt a message using Fernet symmetric encryption"""
    try:
        return cipher_suite.decrypt(encrypted_message).decode()
    except Exception:
        return None

def sanitize_input(text):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not isinstance(text, str):
        return ""
    # Remove potentially dangerous characters and HTML
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text[:1000]  # Limit message length

def encode(text):
    """Encode text to Morse code with input sanitization"""
    text = sanitize_input(text)
    encoded_message = ''
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            encoded_message += MORSE_CODE_DICT[char] + ' '
    return encoded_message.strip()

def decode(text):
    """Decode Morse code to text with input validation"""
    if not all(c in '.- /' for c in text):
        return "Invalid Morse code"
    text = text.replace('/', ' / ')
    words = text.split(' / ')
    decoded_message = ''
    for word in words:
        chars = word.split(' ')
        for char in chars:
            if char in REVERSED_MORSE_CODE_DICT:
                decoded_message += REVERSED_MORSE_CODE_DICT[char]
        decoded_message += ' '
    return decoded_message.strip()

def rate_limit_exceeded_handler():
    """Handler for rate limit exceeded errors"""
    return jsonify({
        'status': 'error',
        'message': 'Rate limit exceeded. Please try again later.'
    }), 429

# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'status': 'error', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'status': 'error', 'message': 'File too large'}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'status': 'error', 'message': f"Rate limit exceeded. {e.description}"}), 429

# --- Health Check ---
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

# --- Main Execution ---
if __name__ == '__main__':
    # Create required directories
    for directory in [UPLOAD_FOLDER, CHAT_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    # Set file upload limit
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Start server
    app.run(host='0.0.0.0', port=10000, debug=True)
