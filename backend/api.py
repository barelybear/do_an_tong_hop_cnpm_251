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
    # Convert args to list if it's a dict (for consistency)
    if isinstance(args, dict):
        args = [args]
    elif not isinstance(args, list):
        args = [args]
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
    # First check if function exists in SystemController itself (e.g., log_out)
    if hasattr(system, function_name):
        func = getattr(system, function_name)
        print(f"✅ Found {function_name} in SystemController")
    else:
        # Otherwise search in managers
        for manager in managers:
            if hasattr(manager, function_name):
                func = getattr(manager, function_name)
                print(f"✅ Found {function_name} in {type(manager).__name__}")
                break

    if not callable(func):
        print(f"❌ Function {function_name} not found in SystemController or any manager.")
        running = False
        return {"error": "Function not found"}

    # --- call the function ---
    print(f"🟢 Calling {func} with args:", args)
    
    # Check current_user early for functions that need it
    needs_current_user = function_name in [
        "load_message_user", "send_message_user", "add_friend", 
        "search_users", "search_messages_in_chats", "send_friend_request",
        "accept_friend_request", "reject_friend_request", "load_requests",
        "create_group", "get_group_info"
    ]
    
    if needs_current_user:
        if not system.current_user:
            print(f"❌ ERROR: {function_name} requires login but current_user is None")
            running = False
            return {"status": "error", "message": "User not logged in. Please login first.", "output": False, "running": False}
        if not hasattr(system.current_user, 'username') or not system.current_user.username:
            print(f"❌ ERROR: {function_name} requires login but current_user has no valid username")
            running = False
            return {"status": "error", "message": "User not logged in. Please login first.", "output": False, "running": False}
        print(f"Current user: {system.current_user.username}")
    
    try:
        if function_name in ["load_message_user", "send_message_user", "add_friend"]:
            # current_user already checked above
            print(f"Using current user: {system.current_user.username}")
            res = func(system.current_user.username, *args)
        elif function_name in ["search_users", "search_messages_in_chats"]:
            # current_user already checked above
            print(f"Searching with current user: {system.current_user.username}")
            res = func(system.current_user.username, *args)
        elif function_name == 'log_out':
            # For logout, pass current_user object if exists
            print(f"Logout requested. Current user: {system.current_user}")
            if system.current_user and hasattr(system.current_user, 'username'):
                username = system.current_user.username
                print(f"Logging out user: {username}")
                res = func(system.current_user)
                # Clear current_user after successful logout
                if res and res.get("status") == "success":
                    system.current_user = None
                    print(f"✅ User {username} logged out successfully. Current user cleared.")
                else:
                    print(f"❌ Failed to logout user {username}")
            else:
                print("⚠️ Logout requested but no user is logged in")
                res = {"status": "error", "message": "No user logged in", "output": False, "running": False}
        elif function_name == 'load_requests':
            # current_user already checked above
            res = func(system.current_user.username)
        elif function_name == 'send_friend_request':
            # send_friend_request needs current_user object and to_username from args
            # current_user already checked above
            # args should be [from_username, to_username] from frontend
            # But controller expects (from_user, to_username), so pass current_user object and to_username
            if len(args) >= 2:
                to_username = args[1]  # Second argument is to_username
                print(f"Calling send_friend_request with current_user={system.current_user.username}, to_username={to_username}")
                res = func(system.current_user, to_username)
            else:
                print(f"ERROR: Missing arguments for send_friend_request. Args received: {args}")
                running = False
                return {"status": "error", "message": "Missing arguments for send_friend_request", "output": False, "running": False}
        elif function_name in ['accept_friend_request', 'reject_friend_request']:
            # Frontend passes: {request_id, from} as args[0]
            # We need: to_username (current user), request_id, from_username
            if not system.current_user or not hasattr(system.current_user, 'username'):
                running = False
                return {"status": "error", "message": "User not logged in", "output": False, "running": False}
            
            # Extract arguments - args should be list with dict at index 0
            if len(args) == 0 or not isinstance(args[0], dict):
                running = False
                return {"status": "error", "message": f"Invalid arguments format for {function_name}. Expected object with request_id and from.", "output": False, "running": False}
            
            arg_obj = args[0]
            
            # Extract values from object
            request_id = arg_obj.get('request_id') or arg_obj.get('id')
            from_username = arg_obj.get('from') or arg_obj.get('username')  # For friend request, 'from' is the username
            to_username = system.current_user.username  # Current user is the one accepting/rejecting
            
            if request_id and from_username:
                res = func(to_username, request_id, from_username)
            else:
                running = False
                return {"status": "error", "message": f"Missing required arguments for {function_name}. Need request_id and from.", "output": False, "running": False}
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
        print(res)
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