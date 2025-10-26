from flask import Flask, render_template, request, jsonify
from morse3 import Morse as m

app = Flask(__name__)

# Easter eggs dictionary
EASTER_EGGS = {
    "hello world": "💜💙💙💙/💜/💜💙💜💜/💜💙💜💜/💜💜💜💜💜 / 💜💜💜💙/💜💜💜💜💜/💜💙💜/💜💙💜💜/💙💜💜",
    "the matrix": "AGENT SMITH: 'Mr. Anderson...'",
    "sudo rm -rf /": "COMMAND NOT RECOGNIZED. SYSTEM INTEGRITY IS SECURE.",
    "shadowheart": "CREATOR OF THIS UNIVERSE.",
    "never gonna give you up": "....-./---/-.--/./.../--.-/--/---/-./-./.-/--./---/-./-./.-/--./../...-/./-.--/---/..-/..-/--./--./---/-./-./.-/.-.././-/./-.--/---/..-/ -../---/.--/-.",
    "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs.",
    "what is the meaning of life": "42"
}

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
        return jsonify({'status': 'success', 'result': EASTER_EGGS[text]})

    is_morse = any(c in '.-💜💙' for c in text)

    if is_morse:
        result = decode(text)
    else:
        result = encode(text)
        
    if "Error:" in result:
        return jsonify({'status': 'error', 'message': result})
    return jsonify({'status': 'success', 'result': result})

def encode(a):
    try:
        words = a.split(' ')
        encoded_words = []
        for word in words:
            encoded_word = m(word).stringToMorse()
            if isinstance(encoded_word, KeyError):
                invalid_char = str(encoded_word).split("'")[1]
                return f"Error: Invalid character for encoding: '{invalid_char}'"
            encoded_word = encoded_word.replace(".", "💜").replace("-", "💙")
            encoded_words.append(encoded_word)
        return " / ".join(encoded_words)
    except Exception as e:
        return f"Error: Could not encode the provided text. Details: {str(e)}"

def decode(a):
    try:
        words = a.split(' / ')
        decoded_words = []
        for word in words:
            decoded_word = word.replace("💜", ".").replace("💙", "-").strip()
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