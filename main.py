from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "data.json"

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"url": "https://animepahe.ru", "messages": []}, f)

def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route('/')
def index():
    return render_template('index.html')

# API to get current video URL and Chat
@app.route('/get_state')
def get_state():
    data = read_data()
    return jsonify(data)

# API to update the video URL
@app.route('/update_url', methods=['POST'])
def update_url():
    new_url = request.json.get('url')
    data = read_data()
    data['url'] = new_url
    write_data(data)
    return jsonify({"status": "success"})

# API to send a message
@app.route('/send_msg', methods=['POST'])
def send_msg():
    username = request.json.get('username')
    text = request.json.get('text')

    data = read_data()
    data['messages'].append({"user": username, "text": text})

    # Keep only last 50 messages
    if len(data['messages']) > 50:
        data['messages'] = data['messages'][-50:]

    write_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Run on 0.0.0.0 so Replit/Network can access it
    app.run(host='0.0.0.0', port=5000)