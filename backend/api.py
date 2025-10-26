from flask import Flask, jsonify, request   
import function
import helper
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
current_user = helper.User(None, None, None)

@app.route('/api/process', methods=['POST'])
def process_request():
    data = request.json
    function_name = data.get("function_name")
    args = data.get("args", [])
    output = call_function(function_name, *args)
    return jsonify({"status": "success", "output": output}), 200

def call_function(function_name, *args):
    func = getattr(function, function_name, None)
    if callable(func):
        return func(*args)
    else:
        return {"error": "Function not found"}

@app.route('/api/login', methods=['POST'])
def on_login():
    global current_user
    data = request.json
    if function.login(data["username"], data["password"], current_user):
        return jsonify({"status": "success", "message": "User logged in", "output": True}), 200
    return jsonify({"status": "error", "message": "Login failed", "output": False}), 400

@app.route('/api/signup', methods=['POST'])
def on_signup():
    global current_user
    data = request.json
    if function.sign_up(data["username"], data["password"], data["gmail"]):
        return jsonify({"status": "success", "message": "User signed up", "output": True}), 201
    return jsonify({"status": "error", "message": "Sign up failed", "output": False}), 400

@app.route('/api/logout', methods=['POST']) 
def on_logout():
    global current_user
    if function.log_out(current_user):
        current_user = None
        return jsonify({"status": "success", "message": "User logged out", "output": True}), 200
    return jsonify({"status": "error", "message": "Logout failed", "output": False}), 400


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)