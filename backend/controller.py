import function

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
        else:
            self.auth = system_singleton.auth
            self.user_manager = system_singleton.user_manager
            self.chat_manager = system_singleton.chat_manager
            self.file_manager = system_singleton.file_manager
            self.group_manager = system_singleton.group_manager
            self.notification_manager = system_singleton.notification_manager
            self.ui_manager = system_singleton.ui_manager
        return self
    
    def log_out(self, user):
        return function.log_out(user)

class AuthManager:
    def __init__(self):
        pass
    def login(self, username, password):
        return function.login(username, password)
        
    def sign_up(self, username, password, gmail):
        return function.sign_up(username, password, gmail)
    
    def forget_password(self, gmail):
        return function.forget_password(gmail)
    # chua xong
        

class UserManager:
    def __init__(self):
        pass
    def view_profile(self, user):
        return function.view_profile(user)
    def update_profile(self, user, new_bio):
        return function.update_profile(user, new_bio)
    def update_avatar(self, user):
        return function.update_avatar(user)
        # Avatar duoc lay trong function update_avatar khong can phai truyen vao
    def set_user_status(self, user, status):
        return function.set_user_status(user, status) 
    def add_friend(self, user, friend_username):
        return function.add_friend(user, friend_username)
    def remove_friend(self, user, friend_username):
        return function.remove_friend(user, friend_username)
    def block_user(self, user, blocked_username):
        return function.block_user(user, blocked_username)
    def unblock_user(self, user, blocked_username):
        return function.unblock_user(user, blocked_username)    
    
class ChatManager:
    def __init__(self):
        pass
    def send_message_user(self, to_user, from_user, content):
        return function.send_message_user(to_user, from_user, content)
    def send_message_group(self, to_group, from_user, content):
        return function.send_message_group(to_group, from_user, content)
    def load_messages_user(self, to_user, from_user):
        return function.load_messages_user(to_user, from_user)
    def load_messages_group(self, to_groupname, from_user):
        return function.load_messages_group(to_groupname, from_user)
    def translate_message(self, message, target_language):
        return function.translate_text(message, target_language)
    #def display_messages(self, frame, messages):
    #    return function.display_messages(frame, messages)
    # cũ rồi, dùng cái của js
class FileManager:
    def __init__(self):
        pass
    def upload_to_pcloud(self, file_path):
        return function.upload_to_pcloud(file_path)
    def delete_from_pcloud(self, fieldid, folderid):
        return function.delete_from_pcloud(fieldid, folderid)
    def _get_file_id_from_path(self, file_path):
        return function.get_file_id_from_path(file_path)
        # cái này private
    def send_file_user(self, to_username, from_user):
        return function.send_file_user(to_username, from_user)
    def send_file_group(self, to_groupname, from_user):
        return function.send_file_group(to_groupname, from_user)

class GroupManager:
    def __init__(self):
        pass
    def create_group(self, group_name, members, admin_username):
        return function.create_group(group_name, members, admin_username)
    def leave_group(self, group_name, new_member_username):
        return function.leave_group(group_name, new_member_username)
    def add_member_to_group(self, user, group_name, new_member_username):
        return function.add_member_to_group(user, group_name, new_member_username)
    def remove_member_from_group(self, user, group_name, member_username):
        return function.remove_member_from_group(user, group_name, member_username)
    def promote_member_to_admin(self, user, group_name, member_username):
        return function.promote_member_to_admin(user, group_name, member_username)
    def demote_admin_to_member(self, user, group_name, admin_username):
        return function.demote_admin_to_member(user, group_name, admin_username)

class NotificationManager:
    def __init__(self):
        pass
    def notify_user(self, user, from_user):
        return function.notify_user(user, from_user)
    def clear_notifications(self, user):
        return function.clear_notifications(user)
    def clear_all_notifications(self, user):
        return function.clear_all_notifications(user)
# có thể phải vứt vì dùng js để làm UI
class UIManager:
    def __init__(self):
        pass
    def open_image_popup(self, image_path):
        return function.open_image_popup(image_path)
    def play_video_stream(self, video_url):
        return function.play_video_stream(video_url)
