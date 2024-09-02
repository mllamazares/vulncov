from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# Database file path
DATABASE = 'test.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    # This will NEVER be triggered
    if 1==2:
        ping()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # Vulnerable to XSS
        return f"Welcome {username}!"
    else:
        return "Invalid credentials!", 403

#@app.route('/ping', methods=['GET'])
def ping():
    ip = request.args.get('ip')
    
    # Vulnerable to command injection
    command = f"ping -c 1 {ip}"
    output = os.popen(command).read()
    
    # Vulnerable to XSS
    return f"<pre>{output}</pre>"

if __name__ == '__main__':
    init_db()
    app.run(debug=False)
