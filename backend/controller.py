import function
import helper
import listener
from firebase_admin import firestore
class SystemController:
    def __init__(self, system_singleton):
        if system_singleton is None:
            self.auth = AuthManager()
            self.user_manager = UserManager()
            self.chat_manager = ChatManager()
            self.file_manager = FileManager()
            self.group_manager = GroupManager()
            self.notification_manager = NotificationManager()
            self.ui_manager = UIManager()
            self.current_user = helper.User(None, None, None)
            self.listener = Listener()
        else:
            self.auth = system_singleton.auth
            self.user_manager = system_singleton.user_manager
            self.chat_manager = system_singleton.chat_manager
            self.file_manager = system_singleton.file_manager
            self.group_manager = system_singleton.group_manager
            self.notification_manager = system_singleton.notification_manager
            self.ui_manager = system_singleton.ui_manager
            self.current_user = system_singleton.current_user
            self.listener = system_singleton.listener

    def get_instance(self):
        return self

    def log_out(self, user):
        """
        Log out a user.
        
        Args:
            user: User object from system.current_user with username attribute
            
        Returns:
            dict: Response with status, message, and output
        """
        # user is already a User object from system.current_user
        if user and hasattr(user, 'username'):
            username = user.username
            print(f"🔐 Attempting to logout user: {username}")
            result = function.log_out(user)
            if result:
                return {"status": "success", "message": f"User {username} logged out successfully", "output": True, "running": False}
            else:
                return {"status": "error", "message": "Failed to logout. Please try again.", "output": False, "running": False}
        return {"status": "error", "message": "No user to logout", "output": False, "running": False}

class AuthManager:
    def __init__(self):
        pass
    def login(self, username, password):
        user = function.login(username, password)
        if user is None:
            return {"status": "error", "message": "Login failed", "output": False, "running": False, "is_user": False}
        return {"status": "success", "message": "User logged in", "output": True, "running": False, "is_user": True, "username": user.username, "gmail": user.password, "password": user.password}

    def sign_up(self, username, password, gmail):
        res = function.sign_up(username, password, gmail)
        if res:
            return {"status": "success", "message": "User signed up", "output": True, "running": False}
        return {"status": "error", "message": "Sign up failed", "output": False, "running": False}

    def forget_password(self, password, gmail):
        res = function.forget_password(password, gmail)
        if res:
            return {"status": "success", "message": "Password reset email sent", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send password reset email", "output": False, "running": False, "is_user": False}
    # chua xong

    def verify_email(self, receiver_email: str, is_sign_up = True) -> int:
        res = function.verify_email_sending(receiver_email, is_sign_up)
        if res != -1:
            return {"status": "success", "message": "Verification email sent", "output": res, "running": False}
        return {"status": "error", "message": "Failed to send verification email", "output": -1, "running": False, "is_user": False}

class UserManager:
    def __init__(self):
        pass
    def view_profile(self, user):
        user = function.load_user(user)             
        res = function.view_profile(user)
        if res is not None:
            # Trả về gmail gốc từ database, không mã hóa
            gmail = res.gmail if res else user.gmail
            print(f"Controller view_profile - returning gmail: {gmail}")
            # Trả về response với api_status riêng và status là user status
            return {
                "api_status": "success",  # API response status
                "status": res.status,  # User online status (online/busy/hidden/offline)
                "message": "User profile found.", 
                "ouput": True, 
                "running": False, 
                "is_user": False, 
                "username": res.username, 
                "password": res.password, 
                "gmail": gmail,  # Gmail gốc từ database, không mã hóa
                "bio": res.bio, 
                "avatar": res.avatar, 
                "friends": res.friends, 
                "groups": res.groups, 
                "last_active": res.last_active, 
                "blocked_users": res.blocked_users, 
                "notifications": res.notifications
            }
        return{"api_status": "error", "status": "error", "message": "Failed to view profile of selected user.", "output": False, "running": False, "is_user": False}
        
    def update_profile(self, user, new_bio):
        user = function.load_user(user)
        if user and function.update_bio(user, new_bio):
            return {"status": "success", "message": "Bio updated.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to update bio.", "output": False, "running": False, "is_user": False}

    def update_avatar(self, user):
        user = function.load_user(user)
        # Avatar duoc lay trong function update_avatar khong can phai truyen vao
        if user and function.update_avatar(user):
            return {"status": "success", "message": "Avatar updated.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to update avatar.", "output": False, "running": False, "is_user": False}

    def set_user_status(self, user, status):
        user = function.load_user(user)
        if user and function.set_user_status(user, status):
            return {"status": "success", "message": "Status updated.", "output": True, "running": False, "status": status}
        return {"status": "error", "message": "Failed to update status.", "output": False, "running": False, "is_user": False}

    def add_friend(self, user, friend_username):
        user = function.load_user(user)
        if user and function.add_friend(user, friend_username):
            return {"status": "success", "message": "Friend added.", "output": True, "running": False}
        return {"status": "error", "message": "Friend add failed.", "output": False, "running": False}

    def remove_friend(self, user, friend_username):
        user = function.load_user(user)
        if user and function.remove_friend(user, friend_username):
            return {"status": "success", "message": "Friend removed.", "output": True, "running": False}
        return {"status": "error", "message": "Friend remove failed.", "output": False, "running": False}

    def block_user(self, user, blocked_username):
        user = function.load_user(user)
        if user and function.block_user(user, blocked_username):
            return {"status": "success", "message": "User blocked.", "output": True, "running": False}
        return {"status": "error", "message": "User block failed.", "output": False, "running": False}

    def unblock_user(self, user, blocked_username):
        user = function.load_user(user)
        if user and function.unblock_user(user, blocked_username):
            return {"status": "success", "message": "User unblocked.", "output": True, "running": False}
        return {"status": "error", "message": "User unblock failed.", "output": False, "running": False}
    
    def search_users(self, current_user, search_query):
        current_user_obj = function.load_user(current_user)
        if current_user_obj:
            results = function.search_users_by_pattern(search_query, current_user_obj)
            return {"status": "success", "output": results, "running": False}
        return {"status": "error", "message": "User not found", "output": [], "running": False}

    def load_friend_list(self, user):
        user = function.load_user(user)
        if user:
            friends_list = function.load_friends_list(user)
            return {"status": "success", "output": friends_list, "running": False}
        return {"status": "error", "output": [], "running": False}
    
class ChatManager:
    def __init__(self):
        pass
    def send_message_user(self, to_user, from_user, content):
        # Check if to_user is actually a group name
        db = firestore.client()
        group_ref = db.collection('groups').document(to_user)
        if group_ref.get().exists:
            # It's a group, use send_message_group instead
            return self.send_message_group(to_user, from_user, content)
        
        # It's a user, proceed with send_message_user
        to_user_obj = function.load_user(to_user)
        from_user_obj = function.load_user(from_user)
        # function.send_message_user expects: (from_user, to_username, content)
        if to_user_obj and from_user_obj and function.send_message_user(from_user_obj, to_user_obj, content):
             return {"status": "success", "message": "Message sent.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send message.", "output": False, "running": False}

    def send_message_group(self, to_group, from_user, content):
        from_user_obj = function.load_user(from_user)
        # function.send_message_group expects group_name (string) and from_user (User object)
        if from_user_obj and function.send_message_group(to_group, from_user_obj, content):
            return {"status": "success", "message": "Message sent to group.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send message to group.", "output": False, "running": False}

    def load_chat_list(self, user):
        user = function.load_user(user)
        print(user)
        if user:
            chat_list = function.load_chat_list(user)
            return {"status": "success", "output": chat_list, "running": False}
        return {"status": "error", "output": [], "running": False}
    def load_message_user(self, from_user, to_username):
        # Check if to_username is actually a group name
        db = firestore.client()
        group_ref = db.collection('groups').document(to_username)
        if group_ref.get().exists:
            # It's a group, use load_message_group instead
            return self.load_message_group(to_username, from_user)
        
        # It's a user, proceed with load_message_user
        from_user_obj = function.load_user(from_user)
        if from_user_obj:
            messages = function.load_messages_user(to_username, from_user_obj)
            return {"status": "success", "output": messages, "running": False}
        return {"status": "error", "message": "Failed to load message.", "output": [], "running": False}
    
    def search_messages_in_chats(self, current_user, search_query):
        current_user_obj = function.load_user(current_user)
        if current_user_obj:
            matching_chat_ids = function.search_messages_in_chats(search_query, current_user_obj)
            return {"status": "success", "output": matching_chat_ids, "running": False}
        return {"status": "error", "message": "User not found", "output": [], "running": False}
    
    def load_message_group(self, group_name, from_user):
        from_user_obj = function.load_user(from_user)
        if from_user_obj:
            messages = function.load_messages_group(group_name, from_user_obj)
            return {"status": "success", "output": messages, "running": False}
        return {"status": "error", "message": "Failed to load message.", "output": [], "running": False}
    
    def translate_message(self, message, target_language):
        res = function.translate_text(message, target_language)
        if res and res != message:  # Translation succeeded (result different from original)
             return {"status": "success", "message": "Message translated.", "output": res, "running": False}
        # If translation failed, return original message
        return {"status": "error", "message": "Failed to translate message.", "output": message, "running": False}

class FileManager:
    def __init__(self):
        pass
    def delete_from_pcloud(self, fieldid, folderid):
        if function.delete_from_pcloud(fieldid, folderid):
            return {"status": "success", "message": "File deleted.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to delete file.", "output": False, "running": False}

    def send_file_user(self, to_username, from_user):
        
        from_user = function.load_user(from_user)
        if from_user and function.send_file_user(to_username, from_user):
             return {"status": "success", "message": "File sent.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send file.", "output": False, "running": False}

    def send_file_group(self, to_groupname, from_user):
        from_user = function.load_user(from_user)
        if from_user and function.send_file_group(to_groupname, from_user):
             return {"status": "success", "message": "File sent to group.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send file to group.", "output": False, "running": False}

class GroupManager:
    def __init__(self):
        pass
    def create_group(self, group_name, members, admin_username):
        # create_group returns (success, message, group) tuple
        result = function.create_group(group_name, members, admin_username)
        if isinstance(result, tuple):
            success, message, group = result
            if success and group:
                return {"status": "success", "message": message, "output": True, "running": False, "group_name": group.group_name, "members": group.members, "admins": group.admins}
            else:
                return {"status": "error", "message": message, "output": False, "running": False}
        # Backward compatibility: if function returns Group object directly
        if result:
            return {"status": "success", "message": "Group created.", "output": True, "running": False, "group_name": result.group_name, "members": result.members, "admins": result.admins}
        return {"status": "error", "message": "Failed to create group.", "output": False, "running": False}

    def leave_group(self, group_name_str, member_username):
        group = function.load_group_from_name(group_name_str)
        if group:
            res = function.leave_group(group, member_username)
            if res:
                return {"status": "success", "message": "Left group.", "output": True, "running": False, "group_name": res.group_name, "members": res.members, "admins": res.admins}
        return {"status": "error", "message": "Failed to leave group.", "output": False, "running": False}

    def add_member_to_group(self, user, group_name_str, new_member_username):
        user = function.load_user(user) # Validating the acting admin/user
        group = function.load_group_from_name(group_name_str)
        if user and group:
            res = function.add_member_to_group(user, group, new_member_username)
            if res:
                return {"status": "success", "message": "Member added.", "output": True, "running": False, "group_name": res.group_name, "members": res.members, "admins": res.admins}
        return {"status": "error", "message": "Failed to add member.", "output": False, "running": False}

    def remove_member_from_group(self, user, group_name_str, member_username):
        user = function.load_user(user)
        group = function.load_group_from_name(group_name_str)
        if user and group:
            res = function.remove_member_from_group(user, group, member_username)
            if res:
                return {"status": "success", "message": "Member removed.", "output": True, "running": False, "group_name": res.group_name, "members": res.members, "admins": res.admins}
        return {"status": "error", "message": "Failed to remove member.", "output": False, "running": False}

    def promote_member_to_admin(self, user, group_name_str, member_username):
        user = function.load_user(user)
        group = function.load_group_from_name(group_name_str)
        if user and group:
            res = function.promote_member_to_admin(user, group, member_username)
            if res:
                return {"status": "success", "message": "Member promoted.", "output": True, "running": False, "group_name": res.group_name, "members": res.members, "admins": res.admins}
        return {"status": "error", "message": "Failed to promote member.", "output": False, "running": False}

    def get_group_info(self, group_name_str):
        """Get group information"""
        group_info = function.get_group_info(group_name_str)
        if group_info:
            return {"status": "success", "message": "Group info loaded.", "output": group_info, "running": False}
        return {"status": "error", "message": "Group not found.", "output": None, "running": False}
    
    def demote_admin_to_member(self, user, group_name_str, admin_username):
        user = function.load_user(user)
        group = function.load_group_from_name(group_name_str)
        if user and group:
            res = function.demote_admin_to_member(user, group, admin_username)
            if res:
                return {"status": "success", "message": "Admin demoted.", "output": True, "running": False, "group_name": res.group_name, "members": res.members, "admins": res.admins}
        return {"status": "error", "message": "Failed to demote admin.", "output": False, "running": False}

    def disband_group(self, user, group_name_str):
        user = function.load_user(user)
        group = function.load_group_from_name(group_name_str)
        if user and group:
            res = function.disband_group(user, group)
            if res:
                return {"status": "success", "message": "Group disbanded.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to disband group.", "output": False, "running": False}

class NotificationManager:
    def __init__(self):
        pass
    def send_friend_request(self, from_user, to_username):
        # from_user can be either User object or username string
        if hasattr(from_user, 'username'):
            from_username = from_user.username
        else:
            from_username = str(from_user)
        
        if from_username and to_username and function.send_friend_request(from_username, to_username):
             return {"status": "success", "message": "Friend request sent.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send friend request.", "output": False, "running": False}
    
    def send_group_invite(self, from_user, to_username, group_name):
        if from_user and function.send_group_invite(from_user, to_username, group_name):
             return {"status": "success", "message": "Group invite sent.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to send group invite.", "output": False, "running": False}

    def load_requests(self, user):
        user = function.load_user(user)
        if user:
            print("123")
            requests = function.load_request(user)
            print("456")
            return {"status": "success", "output": requests, "running": False}
        return {"status": "error", "output": [], "running": False}
    
    def accept_friend_request(self, to_username, request_id, from_username):
        if to_username and request_id and from_username:
            if function.accept_friend_request(to_username, request_id, from_username):
                return {"status": "success", "message": "Friend request accepted.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to accept friend request.", "output": False, "running": False}
    
    def reject_friend_request(self, to_username, request_id, from_username):
        if to_username and request_id and from_username:
            if function.reject_friend_request(to_username, request_id, from_username):
                return {"status": "success", "message": "Friend request rejected.", "output": True, "running": False}
        return {"status": "error", "message": "Failed to reject friend request.", "output": False, "running": False}


class UIManager:
    def __init__(self):
        pass
    def open_image_popup(self, image_path):
        return function.open_image_popup(image_path)
    def play_video_stream(self, video_url):
        return function.play_video_stream(video_url)

from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
import function
# ---------------- FIREBASE SETUP ----------------
key_path = Path(__file__).resolve().parent.parent / "trans-chat-key.json"
cred = credentials.Certificate(key_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()



# return true if there is changes
class Listener:
    def __init__(self):
        pass
    
    def listen_for_messages(self, username):
        db_ref = firestore.client().collection('users').document(username)
        if db_ref.get().exists:
            notifications = db_ref.get().to_dict().get('notifications', [])
            if len(notifications) > 0:
                function.clear_all_notifications(username)
                return {"status": "success", "message": "Found changes.", "output": True, "running": False}
            return {"status": "success", "message": "No change found.", "output": False, "running": False}
        return {"status": "error", "message": "Can not find user.", "output": False, "running": False}

    def listen_for_message_in(self, username, chat, last_update):
        user_exist = firestore.client().collection('users').document(username).get().exists
        db_group = firestore.client().collection('groups').document(chat)
        if  user_exist and firestore.client().collection('users').document(chat).get().exists: 
            # get ref user chat
            db_ref = function._get_or_create_chat_ref(username, chat)
            tim = function.get_final_message_timestamp(db_ref.id)
        elif not user_exist or not db_group.get().exists:
            return {"status": "error", "message": "Can not find user.", "output": False, "running": False}
        if tim > last_update:
            return {"status": "success", "message": "Found changes.", "output": True, "running": False}
        return {"status": "success", "message": "No change found.", "output": False, "running": False}
    