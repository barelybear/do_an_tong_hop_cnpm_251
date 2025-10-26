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
    def __init__(self, sender, content, timestamp):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
        self.is_media = False
        self.media_type = None  # e.g., 'image', 'video'


class User:
    def __init__(self, username, password, gmail):
        self.username = username
        self.password = password
        self.gmail = gmail
        self.friends = []
        self.groups = []
        self.status = "online"
        self.avatar = None
        self.bio = ""
        self.ip_address = None
        self.last_active = None
        self.blocked_users = []
        self.notifications = []

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
    
class Group:
    def __init__(self, group_name, members):
        self.group_name = group_name
        self.members = members  # List of usernames
        self.messages = []
        self.admins = []

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

