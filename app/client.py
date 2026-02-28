# client.py
from flask import Flask, jsonify, render_template_string
import requests
import hashlib
import os

app = Flask(__name__)

# Replace this with your server's IP or domain
SERVER_URL = "http://192.168.165.134:5000/data"  

DATA_DIR = "/clientdata"
FILE_PATH = f"{DATA_DIR}/received.txt"
os.makedirs(DATA_DIR, exist_ok=True)

# HTML template
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Client App</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 50px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; margin-top: 20px; }
        #output {
            margin-top: 20px;
            display: none; /* hidden initially */
            white-space: pre-wrap;
            word-break: break-word;
            background: #f2f2f2;
            padding: 20px;
            border-radius: 8px;
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
            text-align: left;
        }
        h1 { margin-bottom: 10px; }
        p { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Client App</h1>
    <p>Click the button to fetch data from the server and verify checksum:</p>
    <button onclick="fetchData()">Fetch Data</button>
    <div id="output"></div>

    <script>
        function fetchData() {
            fetch('/fetch')
                .then(response => response.json())
                .then(result => {
                    const box = document.getElementById('output');
                    box.style.display = 'block';
                    box.textContent = result.message;
                })
                .catch(err => {
                    const box = document.getElementById('output');
                    box.style.display = 'block';
                    box.textContent = 'Error fetching data';
                });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/fetch")
def fetch_data():
    try:
        response = requests.get(SERVER_URL)
        response.raise_for_status()
        json_data = response.json()

        data = json_data["data"]
        checksum = json_data["checksum"]

        # Save received data to file
        with open(FILE_PATH, "w") as f:
            f.write(data)

        # Verify checksum
        calculated = hashlib.sha256(data.encode()).hexdigest()
        if calculated == checksum:
            status = "✅ Checksum verified!"
        else:
            status = "❌ Checksum mismatch!"

        return jsonify({
            "message": f"Data:\n{data}\n\nChecksum:\n{checksum}\n\nStatus: {status}"
        })

    except Exception as e:
        return jsonify({"message": f"Error connecting to server: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)