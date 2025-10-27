# Morse Code Encryption & Decryption Web App

![prothum](https://github.com/S-hadowHeart/Morse-Code-Encryption-Decryption/assets/103097446/8eab5b89-88fc-499e-8e46-c08ca4eb9e7d)

Welcome to the Morse Code Fun web application, where you can decode secret messages or create your own encrypted texts using Morse code! This interactive and user-friendly app is designed to make Morse code encryption and decryption a breeze. Whether you want to send coded messages or decipher mysterious texts, Morse Code Fun has got you covered.

## Features

- **Easy-to-Use Interface**: With a sleek and intuitive design, Morse Code Fun provides a seamless user experience.
- **Encode and Decode**: Input your text or Morse code and instantly encode or decode messages with a single click.
- **Real-Time Results**: See the results in real-time with immediate feedback displayed on the screen.
- **Responsive Design**: Access the web app on any device, from desktop to mobile, with full responsiveness.

## How to Use

1. **Input Text**: Enter your text or Morse code into the designated input field.
2. **Click Encode/Decode**: Hit the button to either encode or decode your message.
3. **View Results**: Instantly see the encoded or decoded message displayed below the input field.

## Live Demo

Check out the live demo of Morse Code Fun [here](https://heart-code.onrender.com) to experience it in action!

## Get Started

To run the application locally:

1. Clone this repository:

   ```bash
   git clone https://github.com/S-hadowHeart/Morse-Code-Encryption-Decryption.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Morse-Code-Encryption-Decryption
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask app:

   ```bash
   python app.py
   ```

5. Open your web browser and visit [http://127.0.0.1:10000](http://127.0.0.1:10000) to access the Morse Code Fun web app.

## Notes for developers

- Persistent encryption key: The app now persists a Fernet key to `fernet.key` in the project root (or uses the `FERNET_KEY` / `ENCRYPTION_KEY` environment variable if provided). This ensures encrypted chat messages can be decrypted after the server restarts. If you want ephemeral keys, delete `fernet.key` before starting the server.

- Running quick smoke tests:

  1. Ensure the server is running on port 10000 (default):

     ```powershell
     python .\app.py
     ```

  2. In another shell, run the smoke tests:

     ```powershell
     python .\tests\test_smoke.py
     ```

  The smoke test will exercise `/code` and `/chat/create` and report simple pass/fail output.

## Connect with Me

- [LinkedIn](https://lnkd.in/d5dA7dEn)
- [Twitter](https://twitter.com/S_hadowHeart)
- [Dev.to](https://dev.to/s_hadowheart)
- [Other social media](https://s-hadowheart.carrd.co/)

Feel free to reach out to me for any questions, feedback, or collaboration opportunities!

## Demo Video

Watch this demo video to see Morse Code Fun in action:

https://github.com/S-hadowHeart/Morse-Code-Encryption-Decryption/assets/103097446/df332f37-82b6-4abb-a372-f9fb9829390a

Enjoy encoding and decoding messages with Morse Code Fun! 🚀🔒

---

**S-hadowHeart**  
[GitHub](https://github.com/S-hadowHeart)
