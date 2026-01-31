from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# 資料庫設定
DATABASE = "music.db"


def get_db_connection():
    """建立資料庫連接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化資料庫"""
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            song_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


# 初始化資料庫
init_db()


@app.route("/")
def index():
    """首頁"""
    return render_template("index.html")


@app.route("/api/songs", methods=["GET"])
def get_songs():
    """取得所有歌曲或搜尋歌曲"""
    search_query = request.args.get("search", "").strip()

    conn = get_db_connection()

    if search_query:
        # 搜尋歌手或歌名
        songs = conn.execute(
            """
            SELECT * FROM songs 
            WHERE artist LIKE ? OR song_name LIKE ?
            ORDER BY created_at DESC
        """,
            (f"%{search_query}%", f"%{search_query}%"),
        ).fetchall()
    else:
        # 取得所有歌曲
        songs = conn.execute("SELECT * FROM songs ORDER BY created_at DESC").fetchall()

    conn.close()

    # 轉換為字典列表
    songs_list = [dict(song) for song in songs]
    return jsonify(songs_list)


@app.route("/api/songs", methods=["POST"])
def add_song():
    """新增歌曲"""
    data = request.get_json()

    artist = data.get("artist", "").strip()
    song_name = data.get("song_name", "").strip()

    # 驗證輸入
    if not artist or not song_name:
        return jsonify({"error": "歌手和歌名不能為空"}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO songs (artist, song_name) VALUES (?, ?)", (artist, song_name)
    )
    conn.commit()

    # 取得新增的歌曲資料
    new_song = conn.execute(
        "SELECT * FROM songs WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()

    return jsonify(dict(new_song)), 201


@app.route("/api/songs/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    """刪除歌曲"""
    conn = get_db_connection()
    conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "刪除成功"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
