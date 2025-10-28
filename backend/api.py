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
    return output

def call_function(function_name, *args):
    print(f"🔍 Looking for function: {function_name}")

    func = getattr(function, function_name, None)
    if func is None:
        func = globals().get(function_name, None)

    if callable(func):
        return func(*args)
    else:
        return {"error": "Function not found"}

def on_login(username, password):
    global current_user
    if function.login(username, password, current_user):
        return jsonify({"status": "success", "message": "User logged in", "output": True})
    return jsonify({"status": "error", "message": "Login failed", "output": False})

def on_signup(username, password, gmail):
    global current_user
    if function.sign_up(username, password, gmail):
        return jsonify({"status": "success", "message": "User signed up", "output": True})
    return jsonify({"status": "error", "message": "Sign up failed", "output": False})

def on_logout():
    global current_user
    if function.log_out(current_user):
        current_user = None
        return jsonify({"status": "success", "message": "User logged out", "output": True})
    return jsonify({"status": "error", "message": "Logout failed", "output": False})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)