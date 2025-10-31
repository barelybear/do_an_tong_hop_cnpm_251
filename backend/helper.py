import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
key_path = Path(__file__).resolve().parent.parent / "trans-chat-key.json"
cred = credentials.Certificate(key_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- PCLOUD CONFIG ----------------
PCLOUD_TOKEN = "wtFmxkZu6gP7ZBeQ9sxXiqAYF8bjH6N5Ep8SMb8Hk"  # use the 'auth' returned from /login
PCLOUD_FOLDER_ID = 0  # root folder

cred = credentials.Certificate(key_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
class Message:
    def __init__(self, sender, content, timestamp, media_type, is_media):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
        self.is_media = is_media  # Boolean indicating if the message contains media
        self.media_type = media_type  # e.g., 'image', 'video'


class User:
    def __init__(self, username, password, gmail, bio = "", status = "online", last_active = None, avatar = None, ip_address = None, friends = [], groups =[], blocked_users = [], notifications=[], requests = []):
        self.username = username
        self.password = password
        self.gmail = gmail
        self.friends = friends
        self.groups = groups
        self.status = status
        self.avatar = avatar
        self.bio = bio
        self._ip_address = ip_address
        self.last_active = last_active
        self.blocked_users = blocked_users
        self.notifications = notifications
        self.request = requests

    def set_ip(self, ip):
        self._ip_address = ip
        return

    def add_friend(self, friend_username):
        if friend_username not in self.friends:
            self.friends.append(friend_username)

    def remove_friend(self, friend_username):
        if friend_username in self.friends:
            self.friends.remove(friend_username)
    
    def block_user(self, username):
        if username not in self.blocked_users:
            self.blocked_users.append(username)
            self.remove_friend(username)
    
    def unblock_user(self, username):
        if username in self.blocked_users:
            self.blocked_users.remove(username)
    
    def get_ip_user(self):
        return self._ip_address
    
    def load_user(self):
        self = function.load_user(self)
    
class Group:
    def __init__(self, group_name, members, admins):
        self.group_name = group_name
        self.members = members  # List of usernames
        self.admins = admins

    def add_member(self, username):
        if username not in self.members:
            self.members.append(username)
            username.friends.append(self.group_name)

    def remove_member(self, username):
        if username in self.members:
            self.members.remove(username)
            username.friends.remove(self.group_name)

    def promote_to_admin(self, username):
        if username in self.members and username not in self.admins:
            self.admins.append(username)

    def demote_from_admin(self, username):
        if username in self.admins:
            self.admins.remove(username)

