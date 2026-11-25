import os
import sqlite3
from flask import Flask, jsonify, request, render_template
from contextlib import closing

app = Flask(__name__)

VERSION = "1.0.0"
app.config["DATABASE"] = os.getenv("DB_PATH", "notes.db")


def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_db()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


init_db()


@app.route("/")
def home():
    return render_template("index.html", version=VERSION)


@app.route("/health")
def health():
    with closing(get_db()) as conn:
        conn.execute("SELECT 1")

    return jsonify({
        "status": "healthy",
        "version": VERSION
    })


@app.route("/api/notes", methods=["GET"])
def get_notes():
    with closing(get_db()) as conn:
        notes = conn.execute(
            "SELECT * FROM notes ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(note) for note in notes])


@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}

    title = data.get("title", "")
    content = data.get("content", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(content, str):
        return jsonify({"error": "Invalid content"}), 400

    with closing(get_db()) as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title.strip(), content)
        )
        conn.commit()

        note_id = cursor.lastrowid

    return jsonify({"id": note_id, "message": "Note created"}), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json(silent=True) or {}

    title = data.get("title", "")
    content = data.get("content", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(content, str):
        return jsonify({"error": "Invalid content"}), 400

    with closing(get_db()) as conn:
        cursor = conn.execute(
            "UPDATE notes SET title=?, content=? WHERE id=?",
            (title.strip(), content, note_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note updated"})


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with closing(get_db()) as conn:
        cursor = conn.execute(
            "DELETE FROM notes WHERE id=?", (note_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
