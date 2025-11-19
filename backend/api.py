from flask import Flask, jsonify, request   
import controller
import helper
from flask_cors import CORS
import function
import traceback
app = Flask(__name__)
CORS(app)
# This dude is current user
# These dude cant run while something is running
cache_chat_list = []
cache_chat_wind = []
forbidden_during_running = ["login", "sign_up", "log_out"]
running = False
system = controller.SystemController(None).get_instance()
@app.route('/api/process', methods=['POST'])
def process_request():
    data = request.json
    function_name = data.get("function_name")
    args = data.get("args", [])
    output = call_function(function_name, *args)
    return output

def call_function(function_name, *args):
    global running
    global forbidden_during_running
    global system

    print(f"🔍 Looking for function: {function_name}")

    if running and function_name in forbidden_during_running:
        print("⏳ A process is already running.")
        return {"error": 1, "running": True, "output": False}

    running = True

    # --- define manager instances ---
    managers = [
        system.auth,
        system.user_manager,
        system.chat_manager,
        system.file_manager,
        system.group_manager,
        system.notification_manager,
        system.ui_manager,  # legacy
        system.listener
    ]

    func = None
    for manager in managers:
        if hasattr(manager, function_name):
            func = getattr(manager, function_name)
            break

    if not callable(func):
        print(f"❌ Function {function_name} not found.")
        running = False
        return {"error": "Function not found"}

    # --- call the function ---
    print(f"🟢 Calling {func} with args:", args)
    try:
        # Check if current_user exists before accessing username
        if system.current_user and hasattr(system.current_user, 'username'):
            print(f"Current user: {system.current_user.username}")
        else:
            print("No current user logged in")
        
        if function_name in ["load_message_user", "send_message_user"]:
            if not system.current_user or not hasattr(system.current_user, 'username'):
                running = False
                return {"status": "error", "message": "User not logged in", "output": False, "running": False}
            print(f"Using current user: {system.current_user.username}")
            res = func(system.current_user.username, *args)
        elif function_name in ["search_users", "search_messages_in_chats"]:
            if not system.current_user or not hasattr(system.current_user, 'username'):
                running = False
                return {"status": "error", "message": "User not logged in", "output": [], "running": False}
            print(f"Searching with current user: {system.current_user.username}")
            res = func(system.current_user.username, *args)
        elif function_name == 'log_out':
            # For logout, pass current_user object if exists
            if system.current_user and hasattr(system.current_user, 'username'):
                res = func(system.current_user)
                # Clear current_user after successful logout
                if res and res.get("status") == "success":
                    system.current_user = None
                    print("Current user cleared after logout")
            else:
                res = {"status": "error", "message": "No user logged in", "output": False, "running": False}
        else:
            res = func(*args)
        
        # update user if applicable
        if function_name == 'login':
            if res and res.get("status") == "success" and res.get("username"):
                print("Loading current user")
                print(res.get("username"))
                system.current_user = function.load_user(res.get("username"))
                print("Loaded")
        # Note: sign_up doesn't set current_user - user needs to login separately
        
        running = False
        return res

    except Exception as e:
        print(f"❌ Error while calling {function_name}:")
        traceback.print_exc()
        running = False  # Always reset running flag on error
        return {"status": "error", "message": str(e), "output": False, "running": False}

# def on_login(username, password):
#     global running
#     if running:
#         return {"running": True, "output": False}
#     global current_user
#     current_user = controller.login(username, password, current_user)
#     if current_user is not None:
#         return jsonify({"status": "success", "message": "User logged in", "output": True})
#     return jsonify({"status": "error", "message": "Login failed", "output": False, "running": False})
# template for modifying function in controller.py
# def on_signup(username, password, gmail):
#     global current_user
#     global running
#     if running:
#         return {"running": True, "output": False}
#     if function.sign_up(username, password, gmail):
#         return jsonify({"status": "success", "message": "User signed up", "output": True})
#     return jsonify({"status": "error", "message": "Sign up failed", "output": False, "running": False})

# def on_logout():
#     global current_user
#     global running
#     if running:
#         return {"running": True, "output": False}
#     if function.log_out(current_user):
#         current_user = None
#         return jsonify({"status": "success", "message": "User logged out", "output": True})
#     return jsonify({"status": "error", "message": "Logout failed", "output": False, "running": False})

# def get_current_user():
#     global current_user
#     if current_user and current_user.username:
#         return jsonify({"status": "success", "username": current_user.username, "gmail": current_user.gmail})
#     return jsonify({"status": "error", "message": "No user logged in"})

# def load_chat_users():
#     global current_user
#     if current_user:
#         users = function.load_chat_users(current_user)
#         return jsonify({"status": "success", "users": users})
#     return jsonify({"status": "error", "message": "No user logged in"})

if __name__ == '__main__':
    system = controller.SystemController(system).get_instance()

    app.run(debug=True, host='127.0.0.1', port=5000)