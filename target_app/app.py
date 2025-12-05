from flask import Flask, jsonify
import os

app = Flask(__name__)

def get_db_connection():
    # The bug trigger: checks for specific env var
    if os.environ.get("DB_HOST") == "prod-db.example.com":
        return "SUCCESS"
    else:
        raise ValueError("Database connection failed: Invalid host")

@app.route('/')
def home():
    try:
        conn_status = get_db_connection()
        return jsonify(message="App is healthy", db_status=conn_status), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/health')
def health():
    return jsonify(status="healthy"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)