import os
import uuid
import requests
from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "storage")
os.makedirs(VIDEO_DIR, exist_ok=True)

# ---------- App ----------
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"

# 🔥 CRITICAL: force threading + polling (Replit fix)
socketio = SocketIO(
    app,
    async_mode="threading",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# ---------- State ----------
room_state = {
    "is_playing": False,
    "time": 0.0,
    "video": None
}
users = {}

# ---------- Helpers ----------
def drive_to_direct(url: str) -> str:
    if "drive.google.com" not in url:
        return url
    file_id = url.split("/file/d/")[1].split("/")[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def download_video(url: str) -> str:
    print("⬇️ Download requested:", url)
    direct = drive_to_direct(url)

    filename = f"video_{uuid.uuid4().hex}.mp4"
    path = os.path.join(VIDEO_DIR, filename)

    r = requests.get(direct, stream=True, timeout=120)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

    print("✅ Downloaded:", filename)
    return filename

# ---------- Routes ----------
@app.route("/")
def index():
    print("🌐 Page loaded")
    return render_template("index.html")

@app.route("/load", methods=["POST"])
def load_video():
    data = request.json
    print("📩 /load called:", data)

    filename = download_video(data["url"])
    room_state.update({
        "video": filename,
        "time": 0.0,
        "is_playing": False
    })

    socketio.emit("video_loaded", {"video": filename})
    return {"ok": True}

@app.route("/video/<name>")
def serve_video(name):
    return send_from_directory(VIDEO_DIR, name)

# ---------- Socket.IO ----------
@socketio.on("connect")
def connect():
    print("🔌 SOCKET CONNECTED")
    emit("sync_state", room_state)

@socketio.on("set_name")
def set_name(data):
    print("🧑 set_name:", data)
    users[request.sid] = data["name"]
    emit("system", {"msg": f"{data['name']} joined"}, broadcast=True)

@socketio.on("chat")
def chat(data):
    print("💬 chat:", data)
    emit("chat", {
        "name": users.get(request.sid, "Guest"),
        "msg": data["msg"]
    }, broadcast=True)

@socketio.on("play")
def play(data):
    print("▶️ play")
    room_state["is_playing"] = True
    room_state["time"] = data["time"]
    emit("play", room_state, broadcast=True, include_self=False)

@socketio.on("pause")
def pause(data):
    print("⏸ pause")
    room_state["is_playing"] = False
    room_state["time"] = data["time"]
    emit("pause", room_state, broadcast=True, include_self=False)

@socketio.on("seek")
def seek(data):
    print("⏩ seek", data)
    room_state["time"] = data["time"]
    emit("seek", room_state, broadcast=True, include_self=False)

# ---------- Run ----------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
