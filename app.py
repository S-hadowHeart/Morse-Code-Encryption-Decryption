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
    encoded_text = m(a).stringToMorse()
    encoded_text = encoded_text.replace(".", "💜").replace("-", "💙")
    return encoded_text

def decode(a):
    decoded_text = a.replace("💜", ".").replace("💙", "-")
    decoded_text = m(decoded_text).morseToString()
    return decoded_text

if __name__ == '__main__':
    app.run(debug=True)
    