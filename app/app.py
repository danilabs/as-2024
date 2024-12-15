from flask import Flask, jsonify

app = Flask(__name__)

USERS = {
    "test": {"role": "test", "message": "This is a test user"},
    "dev": {"role": "dev", "message": "This is a developer user"},
    "admin": {"role": "admin", "message": "This is an admin user"}
}

@app.route('/')
def hello_world():
    return "Hello, this is a simple Flask API!"

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    if username in USERS:
        return jsonify(USERS[username])
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
