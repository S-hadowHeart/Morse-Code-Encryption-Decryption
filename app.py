from flask import Flask, render_template, request, jsonify
from morse3 import Morse as m
import random
import os
import json

app = Flask(__name__)

# --- Morse Code Section --- #

# Easter eggs dictionary
EASTER_EGGS = {
    "hello world": ".... . .-.. .-.. --- / .-- --- .-. .-.. -..",
    "the matrix": "AGENT SMITH: 'Mr. Anderson...'",
    "sudo rm -rf /": "COMMAND NOT RECOGNIZED. SYSTEM INTEGRITY IS SECURE.",
    "shadowheart": "CREATOR OF THIS UNIVERSE.",
    "never gonna give you up": "-. . ...- . .-. / --. --- -. -. .- / --. .. ...- . / -.-- --- ..- / ..- .--.",
    "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs.",
    "what is the meaning of life": "42",
    "show themes": "Available themes: 💜💙, ✨💫, 🔥💧, 💀👻"
}

SYMBOL_THEMES = [
    {".": "💜", "-": "💙"},
    {".": "✨", "-": "💫"},
    {".": "🔥", "-": "💧"},
    {".": "💀", "-": "👻"},
]

# --- Chat Section --- #

AGENT_NAMES = ["Whisper", "Specter", "Mirage", "Echo", "Shadow", "Cipher", "Ronin", "Oracle", "Nyx", "Wraith"]
CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

def generate_room_code():
    return '-'.join(''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4)) for _ in range(3))

@app.route('/chat/create', methods=['POST'])
def create_chat_room():
    room_code = generate_room_code()
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    with open(file_path, 'w') as f:
        json.dump({"messages": []}, f)
    return jsonify({'status': 'success', 'room_code': room_code})

@app.route('/chat/join', methods=['POST'])
def join_chat_room():
    room_code = request.form.get('room_code')
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if os.path.exists(file_path):
        agent_name = random.choice(AGENT_NAMES)
        return jsonify({'status': 'success', 'agent_name': agent_name})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})

@app.route('/chat/send', methods=['POST'])
def send_message():
    room_code = request.form.get('room_code')
    agent_name = request.form.get('agent_name')
    message = request.form.get('message')
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")

    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            chat_data = json.load(f)
            chat_data["messages"].append({"agent": agent_name, "text": message})
            f.seek(0)
            json.dump(chat_data, f)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})

@app.route('/chat/messages', methods=['GET'])
def get_messages():
    room_code = request.args.get('room_code')
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            chat_data = json.load(f)
        return jsonify({'status': 'success', 'messages': chat_data['messages']})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})


# --- Main Application --- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/code', methods=['POST'])
def code():
    text = request.form.get('textInput', '').strip().lower()
    
    if not text:
        return jsonify({'status': 'error', 'message': 'Error: Input is empty.'})

    # Check for Easter eggs
    if text in EASTER_EGGS:
        result = EASTER_EGGS[text]
        # For morse code easter eggs, convert to a random theme
        if text in ["hello world", "never gonna give you up"]:
            theme = random.choice(SYMBOL_THEMES)
            dot = theme["."]
            dash = theme["-"]
            result = result.replace(".", dot).replace("-", dash)
        return jsonify({'status': 'success', 'result': result})

    is_morse = any(c in '.-💜💙✨💫🔥💧💀👻' for c in text)

    if is_morse:
        result = decode(text)
    else:
        result = encode(text)
        
    if "Error:" in result:
        return jsonify({'status': 'error', 'message': result})
    return jsonify({'status': 'success', 'result': result})

def encode(a):
    try:
        theme = random.choice(SYMBOL_THEMES)
        dot = theme["."]
        dash = theme["-"]

        words = a.split(' ')
        encoded_words = []
        for word in words:
            encoded_word = m(word).stringToMorse()
            if isinstance(encoded_word, KeyError):
                invalid_char = str(encoded_word).split("'")[1]
                return f"Error: Invalid character for encoding: '{invalid_char}'"
            encoded_word = encoded_word.replace(".", dot).replace("-", dash)
            encoded_words.append(encoded_word)
        return " / ".join(encoded_words)
    except Exception as e:
        return f"Error: Could not encode the provided text. Details: {str(e)}"

def decode(a):
    try:
        # Create a translation table for all symbols
        translation_table = {
            "💜": ".", "💙": "-",
            "✨": ".", "💫": "-",
            "🔥": ".", "💧": "-",
            "💀": ".", "👻": "-",
        }
        # Use a loop to build the normalized string
        normalized_input = ""
        for char in a:
            normalized_input += translation_table.get(char, char)

        words = normalized_input.split(' / ')
        decoded_words = []
        for word in words:
            decoded_word = word.strip()
            if not decoded_word:
                continue
            result = m(decoded_word).morseToString()
            if isinstance(result, KeyError):
                return f"Error: Invalid Morse code sequence: '{decoded_word}'"
            decoded_words.append(result)
        return " ".join(decoded_words)
    except Exception as e:
        return f"Error: Could not decode the provided Morse code. Details: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)