from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# 資料檔案路徑
DATA_FILE = "songs_data.json"


# 初始化資料檔案
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)


# 讀取歌曲資料
def read_songs():
    init_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# 寫入歌曲資料
def write_songs(songs):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/songs", methods=["GET"])
def get_songs():
    """獲取所有歌曲"""
    songs = read_songs()
    return jsonify(songs)


@app.route("/api/songs", methods=["POST"])
def add_song():
    """新增歌曲"""
    data = request.get_json()

    if not data or "artist" not in data or "song" not in data:
        return jsonify({"error": "缺少必要欄位"}), 400

    songs = read_songs()

    # 建立新歌曲物件
    new_song = {
        "id": len(songs) + 1,
        "artist": data["artist"].strip(),
        "song": data["song"].strip(),
    }

    songs.append(new_song)
    write_songs(songs)

    return jsonify(new_song), 201


@app.route("/api/songs/search", methods=["GET"])
def search_songs():
    """搜尋歌曲"""
    query = request.args.get("q", "").lower()

    if not query:
        return jsonify([])

    songs = read_songs()
    results = [
        song
        for song in songs
        if query in song["artist"].lower() or query in song["song"].lower()
    ]

    return jsonify(results)


@app.route("/api/songs/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    """刪除歌曲"""
    songs = read_songs()
    songs = [song for song in songs if song["id"] != song_id]
    write_songs(songs)
    return jsonify({"message": "刪除成功"})


if __name__ == "__main__":
    init_data()
    app.run(debug=True, host="0.0.0.0", port=5000)
