
import datetime
import json
import os
import random
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__)

# --- Configuration & Setup ---
UPLOAD_FOLDER = 'uploads'
CHAT_DIR = "chats"
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

# --- Main Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guide')
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
    elif message_text: message_content = message_text

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
    return '-'.join(''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4)) for _ in range(3))

def encode(text):
    encoded_message = ''
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            encoded_message += MORSE_CODE_DICT[char] + ' '
    return encoded_message.strip()

def decode(text):
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

# --- Main Execution ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
