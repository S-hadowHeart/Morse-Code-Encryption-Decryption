from flask import Flask, render_template, request, jsonify, send_from_directory
from morse3 import Morse as m
import random
import os
import json
import uuid
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Directory Setup ---
CHAT_DIR = "chats"
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Morse Code Section --- #
EASTER_EGGS = {
    "hello world": ".... . .-.. .-.. --- / .-- --- .-. .-.. -..",
    "the matrix": "AGENT SMITH: 'Mr. Anderson...'",
}
AGENT_NAMES = ["Whisper", "Specter", "Mirage", "Echo", "Shadow", "Cipher", "Ronin", "Oracle", "Nyx", "Wraith"]

# --- Chat Section --- #
@app.route('/chat/create', methods=['POST'])
def create_chat_room():
    room_code = generate_room_code()
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    agent_name = random.choice(AGENT_NAMES)
    with open(file_path, 'w') as f:
        json.dump({"messages": [], "typing_status": {}}, f)
    return jsonify({'status': 'success', 'room_code': room_code, 'agent_name': agent_name})

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
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})

    message_content = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = f"/uploads/{filename}"
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in {'png', 'jpg', 'jpeg', 'gif'}:
            message_content = f"[IMAGE]{file_url}"
        elif file_ext in {'mp4', 'mov', 'avi'}:
            message_content = f"[VIDEO]{file_url}"
    elif message_text:
        message_content = message_text

    if message_content:
        new_message = {
            "id": str(uuid.uuid4()),
            "agent": agent_name,
            "text": message_content,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "reactions": {},
            "reply_to": reply_to
        }
        with open(file_path, 'r+') as f:
            chat_data = json.load(f)
            chat_data["messages"].append(new_message)
            f.seek(0)
            f.truncate()
            json.dump(chat_data, f)
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Invalid file type or empty message.'})

@app.route('/chat/react', methods=['POST'])
def react_to_message():
    room_code = request.form.get('room_code')
    agent_name = request.form.get('agent_name')
    message_id = request.form.get('message_id')
    emoji = request.form.get('emoji')

    if not all([room_code, agent_name, message_id, emoji]):
        return jsonify({'status': 'error', 'message': 'Missing data for reaction.'})

    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})

    with open(file_path, 'r+') as f:
        chat_data = json.load(f)
        message_found = False
        for msg in chat_data['messages']:
            if msg['id'] == message_id:
                message_found = True
                if emoji not in msg['reactions']:
                    msg['reactions'][emoji] = []
                
                if agent_name in msg['reactions'][emoji]:
                    msg['reactions'][emoji].remove(agent_name)
                    if not msg['reactions'][emoji]: del msg['reactions'][emoji]
                else:
                    msg['reactions'][emoji].append(agent_name)
                break
        
        if not message_found: return jsonify({'status': 'error', 'message': 'Message not found.'})

        f.seek(0)
        f.truncate()
        json.dump(chat_data, f)

    return jsonify({'status': 'success'})


@app.route('/chat/messages', methods=['GET'])
def get_messages():
    room_code = request.args.get('room_code')
    agent_name = request.args.get('agent_name')
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            chat_data = json.load(f)
        typing_agents = [name for name, status in chat_data.get("typing_status", {}).items() if status and name != agent_name]
        return jsonify({
            'status': 'success', 
            'messages': chat_data['messages'],
            'typing_agents': typing_agents
        })
    else:
        return jsonify({'status': 'error', 'message': 'Invalid room code.'})

@app.route('/chat/typing', methods=['POST'])
def handle_typing():
    room_code = request.form.get('room_code')
    agent_name = request.form.get('agent_name')
    is_typing = request.form.get('is_typing') == 'true'
    
    file_path = os.path.join(CHAT_DIR, f"{room_code}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            chat_data = json.load(f)
            chat_data.setdefault("typing_status", {})[agent_name] = is_typing
            f.seek(0)
            f.truncate()
            json.dump(chat_data, f)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid room code.'})

# --- Main Application & Routing --- #
@app.route('/')
def index(): return render_template('index.html')

@app.route('/guide')
def guide(): return render_template('guide.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename): return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def generate_room_code():
    return '-'.join(''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4)) for _ in range(3))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
