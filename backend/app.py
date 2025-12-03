import os
import psycopg2
from flask import Flask, request, jsonify
from elo import update_elo

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        dbname=os.getenv("DATABASE_NAME")
    )

@app.post("/users")
def add_user():
    data = request.json
    name = data.get("name")
    elo = data.get("elo", 1000)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, elo) VALUES (%s, %s) RETURNING id;", (name, elo))
    uid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "ok", "user_id": uid})

@app.get("/users")
def list_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, elo FROM users ORDER BY elo DESC;")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {"id": u[0], "name": u[1], "elo": u[2]} for u in users
    ])

@app.post("/match")
def process_match():
    data = request.json
    name_a = data["user_a"]  
    name_b = data["user_b"] 
    score_a = data["score_a"]  

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT elo FROM users WHERE name=%s;", (name_a,))
    result_a = cur.fetchone()
    if not result_a:
        return jsonify({"error": f"User '{name_a}' not found"}), 404
    r_a = result_a[0]

    cur.execute("SELECT elo FROM users WHERE name=%s;", (name_b,))
    result_b = cur.fetchone()
    if not result_b:
        return jsonify({"error": f"User '{name_b}' not found"}), 404
    r_b = result_b[0]

    new_a, new_b = update_elo(r_a, r_b, score_a)

    cur.execute("UPDATE users SET elo=%s WHERE name=%s;", (new_a, name_a))
    cur.execute("UPDATE users SET elo=%s WHERE name=%s;", (new_b, name_b))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        name_a: new_a,
        name_b: new_b
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
