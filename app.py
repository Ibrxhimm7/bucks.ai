from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os, random
app = Flask(__name__)
app.secret_key = "bucksai"

def init_db():
    conn = sqlite3.connect('bucks_ai.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, response TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY, user_input TEXT, ai_response TEXT)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home(): return redirect('/login')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET": return render_template("login.html")
    data = request.get_json()
    conn = sqlite3.connect('bucks_ai.db'); c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (data['username'], data['password']))
    user = c.fetchone(); conn.close()
    if user:
        session['user_id'] = user[0]
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET": return render_template("signup.html")
    data = request.get_json()
    conn = sqlite3.connect('bucks_ai.db'); c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (data['username'],))
    if c.fetchone():
        conn.close(); return jsonify({"success": False, "message": "Username exists"})
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], data['password']))
    conn.commit(); conn.close()
    return jsonify({"success": True})

@app.route('/chat', methods=['GET', 'POST'])
def chat_page():
    if 'user_id' not in session: return redirect('/login')
    if request.method == 'POST':
        user_id = session['user_id']
        user_input = request.json.get("message", "").lower()
        conn = sqlite3.connect('bucks_ai.db'); c = conn.cursor()
        c.execute("SELECT ai_response FROM knowledge WHERE user_input = ?", (user_input,))
        result = c.fetchone()
        if result: ai_reply = result[0]
        else:
            ai_reply = random.choice([
                "Start flipping products online.",
                "Sell AI-generated art as prints.",
                "Offer services on Fiverr.",
                "Try affiliate marketing on Instagram."
            ])
            c.execute("INSERT INTO knowledge (user_input, ai_response) VALUES (?, ?)", (user_input, ai_reply))
        c.execute("INSERT INTO chats (user_id, message, response) VALUES (?, ?, ?)", (user_id, user_input, ai_reply))
        conn.commit(); conn.close()
        return jsonify({"reply": ai_reply})
    conn = sqlite3.connect('bucks_ai.db'); c = conn.cursor()
    c.execute("SELECT message, response FROM chats WHERE user_id = ?", (session['user_id'],))
    chat_history = c.fetchall(); conn.close()
    return render_template('chat.html', chat_history=chat_history)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
