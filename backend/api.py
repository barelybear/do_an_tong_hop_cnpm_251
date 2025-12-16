from flask import Flask, jsonify, request   
import controller
import helper
from flask_cors import CORS
import function
import traceback
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
CORS(app)
# Socket.IO server
socketio = SocketIO(app, cors_allowed_origins="*")

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


def _get_direct_chat_room(user1_username, user2_username):
    """Generate consistent room id for direct chat (same logic as _get_or_create_chat_ref)."""
    sorted_users = sorted([user1_username, user2_username])
    return f"{sorted_users[0]}_{sorted_users[1]}"


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
        "create_group", "get_group_info", "block_user", "unblock_user", "remove_friend",
        "add_member_to_group", "remove_member_from_group", "promote_member_to_admin",
        "demote_admin_to_member", "disband_group", "leave_group",
        "view_profile", "set_user_status", "update_profile"
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
        if function_name == "send_message_user":
            # send_message_user expects: (to_user, from_user, content)
            # Frontend passes: [target, content]
            # So we need: (target, current_user, content)
            if len(args) >= 2:
                to_user = args[0]  # target user/group
                content = args[1]   # message content
                print(f"Using current user: {system.current_user.username}")
                res = func(to_user, system.current_user.username, content)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for send_message_user. Need target and content.", "output": False, "running": False}
        elif function_name in ["load_message_user", "add_friend"]:
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
        elif function_name == 'create_group':
            # create_group needs: group_name, members, and admin_username (which should be current_user.username)
            # current_user already checked above
            if len(args) >= 2:
                group_name = args[0]
                members = args[1] if isinstance(args[1], list) else []
                # Use current_user.username as admin_username for security
                admin_username = system.current_user.username
                print(f"Creating group {group_name} with members {members}, admin: {admin_username}")
                res = func(group_name, members, admin_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for create_group. Need group_name and members.", "output": False, "running": False}
        elif function_name == 'block_user':
            # block_user needs: user (current_user), blocked_username
            if len(args) >= 1:
                blocked_username = args[0]
                print(f"Blocking user {blocked_username} by {system.current_user.username}")
                res = func(system.current_user.username, blocked_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for block_user. Need blocked_username.", "output": False, "running": False}
        elif function_name == 'unblock_user':
            # unblock_user needs: user (current_user), unblocked_username
            if len(args) >= 1:
                unblocked_username = args[0]
                print(f"Unblocking user {unblocked_username} by {system.current_user.username}")
                res = func(system.current_user.username, unblocked_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for unblock_user. Need unblocked_username.", "output": False, "running": False}
        elif function_name == 'remove_friend':
            # remove_friend needs: user (current_user), friend_username
            if len(args) >= 1:
                friend_username = args[0]
                print(f"Removing friend {friend_username} by {system.current_user.username}")
                res = func(system.current_user.username, friend_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for remove_friend. Need friend_username.", "output": False, "running": False}
        elif function_name == 'add_member_to_group':
            # add_member_to_group needs: user (current_user), group_name, new_member_username
            if len(args) >= 2:
                group_name = args[0]
                new_member_username = args[1]
                print(f"Adding member {new_member_username} to group {group_name} by {system.current_user.username}")
                res = func(system.current_user.username, group_name, new_member_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for add_member_to_group. Need group_name and new_member_username.", "output": False, "running": False}
        elif function_name == 'remove_member_from_group':
            # remove_member_from_group needs: user (current_user), group_name, member_username
            if len(args) >= 2:
                group_name = args[0]
                member_username = args[1]
                print(f"Removing member {member_username} from group {group_name} by {system.current_user.username}")
                res = func(system.current_user.username, group_name, member_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for remove_member_from_group. Need group_name and member_username.", "output": False, "running": False}
        elif function_name == 'promote_member_to_admin':
            # promote_member_to_admin needs: user (current_user), group_name, member_username
            if len(args) >= 2:
                group_name = args[0]
                member_username = args[1]
                print(f"Promoting member {member_username} to admin in group {group_name} by {system.current_user.username}")
                res = func(system.current_user.username, group_name, member_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for promote_member_to_admin. Need group_name and member_username.", "output": False, "running": False}
        elif function_name == 'demote_admin_to_member':
            # demote_admin_to_member needs: user (current_user), group_name, admin_username
            if len(args) >= 2:
                group_name = args[0]
                admin_username = args[1]
                print(f"Demoting admin {admin_username} to member in group {group_name} by {system.current_user.username}")
                res = func(system.current_user.username, group_name, admin_username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for demote_admin_to_member. Need group_name and admin_username.", "output": False, "running": False}
        elif function_name == 'disband_group':
            # disband_group needs: user (current_user), group_name
            if len(args) >= 1:
                group_name = args[0]
                print(f"Disbanding group {group_name} by {system.current_user.username}")
                res = func(system.current_user.username, group_name)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for disband_group. Need group_name.", "output": False, "running": False}
        elif function_name == 'leave_group':
            # leave_group needs: group_name, member_username (current_user)
            # But controller expects (group_name_str, member_username)
            if len(args) >= 1:
                group_name = args[0]
                print(f"Leaving group {group_name} by {system.current_user.username}")
                res = func(group_name, system.current_user.username)
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for leave_group. Need group_name.", "output": False, "running": False}
        elif function_name == 'view_profile':
            # view_profile needs: username (can be current_user or another user)
            # If no args provided, use current_user
            if len(args) >= 1:
                username = args[0]
            else:
                username = system.current_user.username
            print(f"Viewing profile for user: {username}")
            res = func(username)
        elif function_name == 'set_user_status':
            # set_user_status needs: username (current_user), status
            # If only one arg provided, assume it's status and use current_user
            if len(args) >= 2:
                username = args[0]
                status = args[1]
            elif len(args) >= 1:
                # Only status provided, use current_user
                username = system.current_user.username
                status = args[0]
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for set_user_status. Need status.", "output": False, "running": False}
            print(f"Setting status for {username} to {status}")
            res = func(username, status)
        elif function_name == 'update_profile':
            # update_profile needs: username (current_user), new_bio
            # If only one arg provided, assume it's new_bio and use current_user
            if len(args) >= 2:
                username = args[0]
                new_bio = args[1]
            elif len(args) >= 1:
                # Only new_bio provided, use current_user
                username = system.current_user.username
                new_bio = args[0]
            else:
                running = False
                return {"status": "error", "message": "Missing arguments for update_profile. Need new_bio.", "output": False, "running": False}
            print(f"Updating profile for {username} with bio: {new_bio}")
            res = func(username, new_bio)
        else:
            res = func(*args)
        
        # update user if applicable
        if function_name == 'login':
            if res and res.get("status") == "success" and res.get("username"):
                print("Loading current user")
                print(res.get("username"))
                system.current_user = function.load_user(res.get("username"))
                print("Loaded")
        elif function_name == 'create_group':
            # Reload current_user to get updated groups list
            if res and res.get("status") == "success" and system.current_user:
                print("Reloading current user after creating group")
                username = system.current_user.username
                reloaded_user = function.load_user(username)
                if reloaded_user and reloaded_user.username:
                    system.current_user = reloaded_user
                    print(f"Current user groups updated: {system.current_user.groups}")
                else:
                    print(f"⚠️ Warning: Failed to reload user {username}, keeping current_user as is")

        # --- Socket.IO real-time events ---
        try:
            if function_name == 'send_message_user' and res and res.get('status') == 'success':
                if len(args) >= 2 and system.current_user and hasattr(system.current_user, 'username'):
                    to_user = args[0]
                    content = args[1]
                    from_username = system.current_user.username
                    room = _get_direct_chat_room(from_username, to_user)
                    socketio.emit(
                        'new_message',
                        {
                            'room': room,
                            'chatType': 'direct',
                            'from': from_username,
                            'to': to_user,
                            'content': content
                        },
                        room=room
                    )
                    # also notify both users to refresh their chat list
                    socketio.emit('chat_list_updated', {'username': from_username}, room=from_username)
                    socketio.emit('chat_list_updated', {'username': to_user}, room=to_user)
        except Exception as e_emit:
            print(f"Socket.IO emit error for {function_name}: {e_emit}")

        running = False
        print(res)
        return res

    except Exception as e:
        print(f"❌ Error while calling {function_name}:")
        traceback.print_exc()
        running = False  # Always reset running flag on error
        return {"status": "error", "message": str(e), "output": False, "running": False}


@socketio.on('connect')
def handle_connect():
    print('🔌 Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Client disconnected')


@socketio.on('join')
def handle_join(data):
    """Client joins a room. Expected data: { room: string }"""
    room = data.get('room') if isinstance(data, dict) else None
    if room:
        print(f"Client joining room: {room}")
        join_room(room)


@socketio.on('leave')
def handle_leave(data):
    """Client leaves a room. Expected data: { room: string }"""
    room = data.get('room') if isinstance(data, dict) else None
    if room:
        print(f"Client leaving room: {room}")
        leave_room(room)


if __name__ == '__main__':
    system = controller.SystemController(system).get_instance()
    # Run with Socket.IO server
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
