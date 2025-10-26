from flask import Flask, render_template, request
from morse3 import Morse as m

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/code', methods=['POST'])
def code():
    text = request.form['textInput']
    
    if text.startswith(".") or text.startswith("-") or text.startswith("💙") or text.startswith("💜"):
        result = decode(text)
    else :
        result = encode(text)
    return render_template('index.html', result=result)

def encode(a):
    words = a.split(' ')
    encoded_words = []
    for word in words:
        encoded_word = m(word).stringToMorse()
        encoded_word = encoded_word.replace(".", "💜").replace("-", "💙")
        encoded_words.append(encoded_word)
    return " / ".join(encoded_words)

def decode(a):
    words = a.split(' / ')
    decoded_words = []
    for word in words:
        decoded_word = word.replace("💜", ".").replace("💙", "-")
        decoded_word = m(decoded_word.strip()).morseToString()
        decoded_words.append(decoded_word)
    return " ".join(decoded_words)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)