import tkinter as tk
from helper import *
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import bcrypt
import socket
from datetime import datetime
from tkinter import Label, filedialog, messagebox
import os
import requests
import mimetypes
from PIL import Image, ImageTk
import io
from firebase_admin import firestore
MAX_IMAGE_W, MAX_IMAGE_H = 900, 500
# ĐỪNG CHỈNH SỬA PHẦN NÀY NẾU KHÔNG CẦN THIẾT
# Nếu chỉnh sửa thì bắt đầu bằng """update start""" và """update end"""


# ---------------- FIREBASE SETUP ----------------
key_path = Path(__file__).resolve().parent.parent / "trans-chat-key.json"
cred = credentials.Certificate(key_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- PCLOUD CONFIG ----------------
PCLOUD_TOKEN = "wtFmxkZu6gP7ZBeQ9sxXiqAYF8bjH6N5Ep8SMb8Hk"  # use the 'auth' returned from /login
PCLOUD_FOLDER_ID = 0  # root folder
# Initialize app with your service account key
cred = credentials.Certificate(key_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# ---------------- CACHE FOR PERFORMANCE ----------------
# Simple in-memory cache for user data to reduce database queries
_user_cache = {}
_cache_timestamps = {}  # Track when cache entries were created
CACHE_TTL_SECONDS = 30  # Cache time-to-live: 30 seconds

def _clear_user_cache(username=None):
    """Clear user cache. If username is provided, clear only that user. Otherwise clear all."""
    global _user_cache, _cache_timestamps
    if username:
        _user_cache.pop(username, None)
        _cache_timestamps.pop(username, None)
    else:
        _user_cache.clear()
        _cache_timestamps.clear()

def get_outbound_ip():
    """Get the local IP address used for outbound connections (non-loopback)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
    
def login(username_entry, password_entry):
    print(f"Login Clicked with Username: {username_entry} and Password: {password_entry}")
    user = load_user(username_entry)
    db_ref = firestore.client().collection('users').document(username_entry)
    doc = db_ref.get()
    if doc.exists:
        last_active = datetime.now().isoformat()
        user_data = doc.to_dict()
        print(user.password, user_data['password'])
        if bcrypt.checkpw(password_entry.encode('utf-8'), user_data['password'].encode('utf-8')):
            print("Login Successful")
            db_ref.get().to_dict()
            user.friends = user_data.get('friends', [])
            user.groups = user_data.get('groups', [])
            user.last_active = last_active
            user.set_ip(get_outbound_ip())
            db_ref.update({
                'last_active': last_active,
                'ip_address': user.get_ip_user(),
                'status': "online"
            })
            user.status = "online"
            print("adsfasdfa")
            print(user.username)
            return user
        else:
            print("Incorrect Password or Username")
            #messagebox.showerror("Login Failed", "Incorrect password or username.")
            return None
    print("Username does not exist")
    return None

def forget_password(gmail_entry):
    print("Forget Password Clicked")
    # Implement forget password functionality here
    

def sign_up(username_entry, password_entry, gmail_entry):
    print("Sign Up Clicked")
    user = User(username_entry, password_entry, gmail_entry)
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        print("Username already exists")
        return False
    if firestore.client().collection('gmail').document(user.gmail).get().exists:
        print("Gmail already registered")
        return False
    db_ref.set({
        'username': user.username,
        'password': hashed_password.decode('utf-8'),
        'gmail': user.gmail,
        'friends': user.friends,
        'groups': user.groups,
        'status': user.status,
        'avatar': user.avatar,
        'bio': user.bio,
        'ip_address': None,#wait till log in
        'last_active': user.last_active,
        'blocked_users': user.blocked_users,
        'notifications': user.notifications
    })
    firestore.client().collection('gmail').document(user.gmail).set({
        'username': user.username,
    })
    return True

def search_user(search_entry, user):
    print(f"Search for user: {search_entry}")
    db_ref = firestore.client().collection('users').document(search_entry)
    if db_ref.get().exists:
        if user.username not in db_ref.get().to_dict().get('blocked_users', []):
            print(f"User {search_entry} found")
            return True
    else:
        db_ref = firestore.client().collection('gmail').document(search_entry)
        if db_ref.get().exists:
            username = db_ref.get().to_dict().get('username')
            user_ref = firestore.client().collection('users').document(username)
            if user.username not in user_ref.get().to_dict().get('blocked_users', []):
                print(f"User with gmail {search_entry} found: {username}")
                return True
    print(f"User {search_entry} not found")
    return False

def detect_message_type(message):
    """Detect if input is text, image, video, or file."""
    if isinstance(message, str) and not os.path.exists(message):
        return "text"
    mime, _ = mimetypes.guess_type(message)
    if mime:
        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        else:
            return "file"
    return "unknown"

def upload_to_pcloud(file_path):
    """Upload file to pCloud and return the public or direct link."""
    try:
        url = "https://api.pcloud.com/uploadfile"
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"folderid": PCLOUD_FOLDER_ID, "auth": PCLOUD_TOKEN}
            res = requests.post(url, files=files, data=data)
            res.raise_for_status()
            result = res.json()

        print("UPLOAD RESULT:", result)
        fileid = result["metadata"][0]["fileid"]

        pub_res = requests.get(
            "https://api.pcloud.com/createpublink",
            params={"fileid": fileid, "auth": PCLOUD_TOKEN},
        )
        pub_res.raise_for_status()
        pub_data = pub_res.json()

        # pCloud returns a unique code for the public link
        if "code" in pub_data:
            return f"https://u.pcloud.link/publink/show?code={pub_data['code']}"
        else:
            # Fallback: use getfilelink for direct streaming link
            link_req = requests.get(
                "https://api.pcloud.com/getfilelink",
                params={"fileid": fileid, "auth": PCLOUD_TOKEN},
            )
            link_req.raise_for_status()
            link_data = link_req.json()
            return f"https://{link_data['hosts'][0]}{link_data['path']}"

    except Exception as e:
        #messagebox.showerror("Upload failed", str(e))
        return None

def open_image_popup(image_path):
    """Open a new window to show full-size image."""
    popup = tk.Toplevel()
    popup.title("Image Viewer")

    try:
        if image_path.startswith("http"):
            img_data = requests.get(image_path).content
            img = Image.open(io.BytesIO(img_data))
        else:
            img = Image.open(image_path)
    except Exception as e:
        #messagebox.showerror("Error", f"Cannot load image: {e}")
        popup.destroy()
        return

    # Resize to fit screen
    screen_w = popup.winfo_screenwidth()
    screen_h = popup.winfo_screenheight()
    img.thumbnail((screen_w - 100, screen_h - 100))

    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(popup, image=tk_img)
    label.image = tk_img
    label.pack(expand=True, fill="both")

def get_status_user(username):
    db_ref = firestore.client().collection('users').document(username)
    if db_ref.get().exists:
        status = db_ref.get().to_dict().get('status', 'offline')
        return status
    else:
        print("User not found")
        return "offline"

def _get_or_create_chat_ref(user1_username, user2_username):
    """
    Gets or creates a chat document reference for two users.
    Generates a consistent, sorted ID to prevent duplicate chats.
    """
    # Sort usernames to create a predictable document ID (e.g., 'alice_bob' not 'bob_alice')
    sorted_users = sorted([user1_username, user2_username])
    chat_id = f"{sorted_users[0]}_{sorted_users[1]}"
    db = firestore.client()
    chat_ref = db.collection('chat').document(chat_id)

    # If the chat document doesn't exist, create it so we can add a sub-collection to it.
    if not chat_ref.get().exists:
        chat_ref.set({
            'participants': sorted_users,
            'created_at': firestore.SERVER_TIMESTAMP
        })
    return chat_ref


# --- Sending Functions ---

def send_message_user(from_user, to_username, content):
    print(f"Sending message to {to_username}: {content}")
    try:
        # Kiểm tra block cả hai chiều: người nhận chặn người gửi HOẶC người gửi chặn người nhận
        db = firestore.client()
        to_user_ref = db.collection('users').document(to_username.username)
        from_user_ref = db.collection('users').document(from_user.username)
        
        if not to_user_ref.get().exists:
            print(f"Recipient {to_username.username} not found")
            return False
        
        if not from_user_ref.get().exists:
            print(f"Sender {from_user.username} not found")
            return False
        
        to_user_data = to_user_ref.get().to_dict()
        from_user_data = from_user_ref.get().to_dict()
        
        to_blocked_users = to_user_data.get('blocked_users', [])
        from_blocked_users = from_user_data.get('blocked_users', [])
        
        # Nếu người gửi bị người nhận chặn thì không cho gửi
        if from_user.username in to_blocked_users:
            print(f"Cannot send message: {to_username.username} has blocked {from_user.username}")
            return False
        
        # Nếu người gửi đã chặn người nhận thì cũng không cho gửi
        if to_username.username in from_blocked_users:
            print(f"Cannot send message: {from_user.username} has blocked {to_username.username}")
            return False
        
        # 1. Get the reference to the main chat document
        chat_ref = _get_or_create_chat_ref(from_user.username, to_username.username)

        # 2. Define the message data
        message_data = {
            'sender': from_user.username,
            'content': content,
            'is_media': False,
            'media_type': None,
            'timestamp': firestore.SERVER_TIMESTAMP  # Use server timestamp for reliability
        }

        # 3. Add a new document to the 'conversation' sub-collection.
        #    Firestore will auto-generate a unique, chronologically-sortable ID.
        chat_ref.collection('conversation').add(message_data)

        print("Message sent")
        # Assuming notify_user can handle a username string
        notify_user(user=to_username, from_username=from_user.username)
        return True
    except Exception as e:
        print(f"An error occurred sending message: {e}")
        return False

def send_file_user(to_username, from_user):
    file_path = filedialog.askopenfilename()
    if not file_path or not os.path.exists(file_path):
        print("File not selected or does not exist")
        return False

    file_type = detect_message_type(file_path)
    print(f"Sending file to {to_username}: {file_path}")
    
    upload_url = upload_to_pcloud(file_path)
    if not upload_url:
        print("File upload failed")
        return False
        
    try:
        chat_ref = _get_or_create_chat_ref(from_user.username, to_username)
        
        message_data = {
            'sender': from_user.username,
            'content': upload_url,
            'is_media': True,
            'media_type': file_type,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        # Add to sub-collection, same as a text message
        chat_ref.collection('conversation').add(message_data)
        
        print("File sent")
        notify_user(user=to_username, from_username=from_user.username)
        return True
    except Exception as e:
        print(f"An error occurred sending file: {e}")
        return False

def send_message_group(to_groupname, from_user, content):
    print(f"Sending message to group {to_groupname}: {content}")
    try:
        db = firestore.client()
        group_ref = db.collection('groups').document(to_groupname)
        group_doc = group_ref.get()

        if not group_doc.exists:
            print("Group not found")
            return False

        group_data = group_doc.to_dict()
        if from_user.username not in group_data.get('members', []):
            print("You are not a member of this group")
            return False

        message_data = {
            'sender': from_user.username,
            'content': content,
            'is_media': False,
            'media_type': None,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        # Add a new document to the group's 'conversation' sub-collection
        group_ref.collection('conversation').add(message_data)

        print("Message sent to group")
        for member in group_data.get('members', []):
            if member != from_user.username:
                member_user = load_user(member)
                if member_user:
                    notify_user(user=member_user, from_username=from_user.username)
        return True
    except Exception as e:
        print(f"An error occurred sending group message: {e}")
        return False

def send_file_group(to_groupname, from_user):
    # This function would be refactored identically to send_message_group,
    # just with the file handling logic included.
    # (Implementation is omitted for brevity but follows the exact same pattern)
    pass


# --- Loading Functions ---

def load_messages_user(to_username, from_user, limit=50):
    """
    Loads messages for a one-on-one chat and formats them into a JSON list
    for front-end consumption.
    Optimized: Only loads the most recent messages (default 50) for faster loading.
    
    Args:
        to_username: Username of the other user in the chat
        from_user: User object of the current user
        limit: Maximum number of messages to load (default 50)
    """
    try:
        # Get the reference to the main chat document.
        # This helper ensures we look for the correct doc_id (e.g., 'user1_user2')
        chat_ref = _get_or_create_chat_ref(from_user.username, to_username)

        # Query the 'conversation' sub-collection, ordering by timestamp DESCENDING
        # and limit to most recent messages, then reverse to get chronological order
        messages_query = chat_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(limit).stream()

        json_messages = []
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            fs_timestamp = msg_data.get('timestamp')

            # Skip any message that might have failed to save its timestamp
            if fs_timestamp is None:
                continue
            
            # Get the actual sender username from the message
            actual_sender = msg_data.get('sender', '')
            
            # Determine sender context ('me' or 'other')
            is_current_user = actual_sender == from_user.username
            sender_id = 'me' if is_current_user else 'other'
            
            # The sender's display name - use actual sender username, not to_username
            # If it's the current user, show 'Me', otherwise show the actual sender username
            sender_name = 'Me' if is_current_user else actual_sender

            message_json = {
                # Use a unique, sortable ISO 8601 string for the ID
                'id': fs_timestamp.isoformat(),
                'sender': sender_name,
                'senderId': sender_id,
                'content': msg_data.get('content'),
                # Format the timestamp for display (e.g., '10:30 AM')
                'timestamp': fs_timestamp.strftime('%I:%M %p').lstrip('0'),
                'isFile': msg_data.get('is_media', False)
            }
            json_messages.append(message_json)
        
        # Reverse to get chronological order (oldest first)
        json_messages.reverse()
        return json_messages
    
    except Exception as e:
        print(f"An error occurred loading messages for user {to_username}: {e}")
        return [] # Return an empty list on failure

def load_messages_group(to_groupname, from_user, limit=50):
    """
    Loads messages for a group chat and formats them into a JSON list
    for front-end consumption.
    Optimized: Only loads the most recent messages (default 50) for faster loading.
    
    Args:
        to_groupname: Name of the group
        from_user: User object of the current user
        limit: Maximum number of messages to load (default 50)
    """
    try:
        db = firestore.client()
        group_ref = db.collection('groups').document(to_groupname)
        group_doc = group_ref.get()
        
        if not group_doc.exists:
            print("Group not found")
            return []

        # Get group data once
        group_data = group_doc.to_dict()
        
        # Basic check to see if the user is a member
        if from_user.username not in group_data.get('members', []):
            print("You are not a member of this group")
            return []

        # Query the sub-collection, ordering by timestamp DESCENDING
        # and limit to most recent messages, then reverse to get chronological order
        messages_query = group_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(limit).stream()

        json_messages = []
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            fs_timestamp = msg_data.get('timestamp')

            if fs_timestamp is None:
                continue

            msg_sender_username = msg_data.get('sender')
            
            # Determine sender context ('me' or 'other')
            is_current_user = msg_sender_username == from_user.username
            sender_id = 'me' if is_current_user else 'other'
            
            # In a group, the sender name is their actual username unless it's you
            sender_name = 'Me' if is_current_user else msg_sender_username
            
            message_json = {
                'id': fs_timestamp.isoformat(),
                'sender': sender_name,
                'senderId': sender_id,
                'content': msg_data.get('content'),
                'timestamp': fs_timestamp.strftime('%I:%M %p').lstrip('0'),
                'isFile': msg_data.get('is_media', False)
            }
            json_messages.append(message_json)

        # Reverse to get chronological order (oldest first)
        json_messages.reverse()
        return json_messages
        
    except Exception as e:
        print(f"An error occurred loading group messages for {to_groupname}: {e}")
        return []

def view_profile(user):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        user_data = db_ref.get().to_dict()
        # Lấy gmail trực tiếp từ database, không mã hóa
        gmail = user_data.get('gmail', '')
        print(f"View profile - gmail from database for {user.username}: {gmail}")
        selected_user = User(
            user_data['username'],
            user_data['password'],
            gmail,  # Gmail gốc từ database, không mã hóa
            user_data.get('bio', ''),
            user_data.get('status', 'offline'),
            user_data.get('last_active'), 
            user_data.get('avatar'),
            user_data.get('ip_address'), 
            user_data.get('friends', []), 
            user_data.get('groups', []), 
            user_data.get('blocked_users', []), 
            user_data.get('notifications', []), 
            user_data.get('requests', [])
        )
        return selected_user
    else:
        print("User not found")
        return None

def delete_from_pcloud(fileid=None, folderid=None):
    """
    Delete a file or folder from pCloud.
    Either fileid or folderid must be provided.
    """
    try:
        if fileid:
            url = "https://api.pcloud.com/deletefile"
            params = {"fileid": fileid, "auth": PCLOUD_TOKEN}
        elif folderid:
            url = "https://api.pcloud.com/deletefolderrecursive"
            params = {"folderid": folderid, "auth": PCLOUD_TOKEN}
        else:
            raise ValueError("You must specify either fileid or folderid.")

        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()

        if data.get("result") == 0:
            print("✅ Deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete: {data}")
            #messagebox.showerror("Delete failed", data.get("error", "Unknown error"))
            return False

    except Exception as e:
        #messagebox.showerror("Error", str(e))
        return False

def get_fileid_from_path(path):
    url = "https://api.pcloud.com/checkfile"
    params = {"path": path, "auth": PCLOUD_TOKEN}
    res = requests.get(url, params=params)
    data = res.json()
    if data.get("result") == 0:
        return data["metadata"]["fileid"]
    else:
        print("Error:", data)
        return None

def update_avatar(user):
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    print(f"Updating avatar: {file_path}")
    if not os.path.exists(file_path):
        print("File does not exist")
        return False
    upload = upload_to_pcloud(file_path)
    if not upload:
        return False

    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        old_avatar = db_ref.get().to_dict().get('avatar', None)
        if old_avatar:
            old_fileid = get_fileid_from_path(old_avatar)
            # Optionally, delete old avatar from pCloud here
            delete_from_pcloud(fileid=old_fileid, folderid=PCLOUD_FOLDER_ID)
        db_ref.update({
            'avatar': upload
        })
        user.avatar = upload
        _clear_user_cache(user.username)  # Clear cache after update
        print("Avatar updated")
        return True
    else:
        print("User not found")
        return False
    
def update_bio(user, new_bio):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        db_ref.update({
            'bio': new_bio
        })
        user.bio = new_bio
        _clear_user_cache(user.username)  # Clear cache after update
        print("Bio updated")
        return True
    else:
        print("User not found")
        return False

def set_user_status(user, new_status):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        db_ref.update({
            'status': new_status
        })
        user.status = new_status
        _clear_user_cache(user.username)  # Clear cache after update
        print("Status updated")
        return True
    else:
        print("User not found")
        return False

def notify_user(user, from_username):
    if from_username not in user.notifications:
        return False
    #messagebox.showinfo("New Message", f"You have a new message from {from_username}")
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        notifications = db_ref.get().to_dict().get('notifications', [])
        notifications.append(from_username)
        db_ref.update({
            'notifications': notifications
        })
        return True

def set_notification(user, from_username):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        notifications = db_ref.get().to_dict().get('notifications', [])
        if from_username not in notifications:
            notifications.append(from_username)
            db_ref.update({
                'notifications': notifications
            })
            user.notifications = notifications
            print("Notification set")
        return True
    else:
        print("User not found")
        return False
    
def clear_notification(user, from_username):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        notifications = db_ref.get().to_dict().get('notifications', [])
        if from_username in notifications:
            notifications.remove(from_username)
            db_ref.update({
                'notifications': notifications
            })
            user.notifications = notifications
            print("Notification cleared")
        return True
    else:
        print("User not found")
        return False

def clear_all_notifications(user):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        db_ref.update({
            'notifications': []
        })
        user.notifications = []
        print("All notifications cleared")
        return True
    else:
        print("User not found")
        return False

def add_friend(user, friend_username):
    print(friend_username)
    db_ref = firestore.client().collection('users').document(user.username)
    friend_ref = firestore.client().collection('users').document(friend_username)
    if db_ref.get().exists and friend_ref.get().exists and friend_username not in db_ref.get().to_dict().get('blocked_users', []):
        user_data = db_ref.get().to_dict()
        friends = user_data.get('friends', [])
        if friend_username not in friends:
            friends.append(friend_username)
            db_ref.update({
                'friends': friends
            })
            user.friends = friends
            _clear_user_cache(user.username)  # Clear cache after update
            print("Friend added")
        _get_or_create_chat_ref(user.username, friend_username)
        return True
    else:
        print("User or friend not found or you blocked this user.")
        return False
    
def remove_friend(user, friend_username):
    """
    Remove friend: xóa bạn bè 2 chiều và xóa tất cả tin nhắn trước đó.
    
    Args:
        user: User object của người thực hiện hủy kết bạn
        friend_username: Username của người bạn cần xóa
    """
    db_ref = firestore.client().collection('users').document(user.username)
    friend_ref = firestore.client().collection('users').document(friend_username)
    
    if not db_ref.get().exists:
        print("User not found")
        return False
    
    if not friend_ref.get().exists:
        print("Friend not found")
        return False
    
    # Lấy danh sách bạn bè của cả 2 người
    user_data = db_ref.get().to_dict()
    friend_data = friend_ref.get().to_dict()
    
    user_friends = user_data.get('friends', [])
    friend_friends = friend_data.get('friends', [])
    
    # Xóa bạn bè 2 chiều
    removed_from_user = False
    removed_from_friend = False
    
    # Xóa friend_username khỏi danh sách bạn bè của user
    if friend_username in user_friends:
        user_friends.remove(friend_username)
        db_ref.update({
            'friends': user_friends
        })
        user.friends = user_friends
        _clear_user_cache(user.username)  # Clear cache after update
        removed_from_user = True
        print(f"Removed {friend_username} from {user.username}'s friends list")
    
    # Xóa user.username khỏi danh sách bạn bè của friend
    if user.username in friend_friends:
        friend_friends.remove(user.username)
        friend_ref.update({
            'friends': friend_friends
        })
        _clear_user_cache(friend_username)  # Clear cache after update
        removed_from_friend = True
        print(f"Removed {user.username} from {friend_username}'s friends list")
    
    # Xóa tất cả tin nhắn giữa 2 người
    # Tạo chat_id giống như trong _get_or_create_chat_ref
    sorted_users = sorted([user.username, friend_username])
    chat_id = f"{sorted_users[0]}_{sorted_users[1]}"
    db = firestore.client()
    chat_ref = db.collection('chat').document(chat_id)
    
    if chat_ref.get().exists:
        try:
            # Xóa tất cả messages trong subcollection 'conversation'
            messages_ref = chat_ref.collection('conversation')
            messages = messages_ref.stream()
            
            deleted_count = 0
            for msg_doc in messages:
                msg_doc.reference.delete()
                deleted_count += 1
            
            # Xóa chat document (sẽ tự động xóa subcollection nếu còn)
            chat_ref.delete()
            print(f"Deleted chat document and {deleted_count} messages between {user.username} and {friend_username}")
        except Exception as e:
            print(f"Error deleting chat messages: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"No chat document found between {user.username} and {friend_username}")
    
    if removed_from_user or removed_from_friend:
        print(f"Friend relationship removed between {user.username} and {friend_username}")
        return True
    else:
        print(f"{user.username} and {friend_username} are not friends")
        return False
    
def block_user(user, block_username):
    """
    Block user: chặn người dùng - không cho đối phương nhắn tin cho mình.
    - Nếu là bạn bè: KHÔNG hủy kết bạn, KHÔNG xóa tin nhắn, vẫn giữ trong danh sách bạn bè
    - Nếu không phải bạn bè: không cho đối phương search ra mình
    
    Args:
        user: User object của người thực hiện block
        block_username: Username của người bị block
    """
    db_ref = firestore.client().collection('users').document(user.username)
    block_ref = firestore.client().collection('users').document(block_username)
    
    if not db_ref.get().exists:
        print("User not found")
        return False
    
    if not block_ref.get().exists:
        print("Block target not found")
        return False
    
    user_data = db_ref.get().to_dict()
    blocked_users = user_data.get('blocked_users', [])
    
    # Thêm vào danh sách blocked nếu chưa có
    if block_username not in blocked_users:
        blocked_users.append(block_username)
        db_ref.update({
            'blocked_users': blocked_users
        })
        user.blocked_users = blocked_users
        _clear_user_cache(user.username)  # Clear cache after update
        print(f"User {block_username} blocked by {user.username}")
        print(f"Note: Friend relationship and messages are preserved (if they were friends)")
        return True
    else:
        print(f"User {block_username} is already blocked by {user.username}")
        return True
    
def unblock_user(user, unblock_username):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        user_data = db_ref.get().to_dict()
        blocked_users = user_data.get('blocked_users', [])
        if unblock_username in blocked_users:
            blocked_users.remove(unblock_username)
            db_ref.update({
                'blocked_users': blocked_users
            })
            user.blocked_users = blocked_users
            _clear_user_cache(user.username)  # Clear cache after update
            print("User unblocked")
        return True
    else:
        print("User not found")
        return False
    
def create_group(group_name, members, admin_username):
    db_ref = firestore.client().collection('groups').document(group_name)
    if db_ref.get().exists:
        print("Group name already exists")
        return (False, "Group name already exists", None)
    for member in members:
        member_ref = firestore.client().collection('users').document(member)
        if not member_ref.get().exists:
            print(f"Member {member} does not exist")
            return (False, f"Member {member} does not exist", None)
    if admin_username not in members:
        members.append(admin_username)
    admins = [admin_username]
    db_ref.set({
        'group_name': group_name,
        'members': members,
        'admins': admins,
        'messages': [],
        'created_date': datetime.now().isoformat(),
        'description': ''
    })
    
    # Update groups field for all members in Firestore
    db = firestore.client()
    for member_username in members:
        user_ref = db.collection('users').document(member_username)
        if user_ref.get().exists:
            user_data = user_ref.get().to_dict()
            user_groups = user_data.get('groups', [])
            if group_name not in user_groups:
                user_groups.append(group_name)
                user_ref.update({
                    'groups': user_groups
                })
                print(f"Updated groups for user {member_username}")
    
    print("Group created")
    group = Group(group_name, members, admins)
    return (True, "Group created successfully", group)

def leave_group(user, group):
    db_ref = firestore.client().collection('groups').document(group.group_name)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        members = group_data.get('members', [])
        admins = group_data.get('admins', [])
        if user.username in members:
            members.remove(user.username)
            if user.username in admins:
                admins.remove(user.username)
            db_ref.update({
                'members': members,
                'admins': admins
            })
            
            # Update user's groups list in Firestore
            user_ref = firestore.client().collection('users').document(user.username)
            if user_ref.get().exists:
                user_data = user_ref.get().to_dict()
                user_groups = user_data.get('groups', [])
                if group.group_name in user_groups:
                    user_groups.remove(group.group_name)
                    user_ref.update({
                        'groups': user_groups
                    })
            
            user.groups = [g for g in user.groups if g != group.group_name]
            if hasattr(group, 'remove_member'):
                group.remove_member(user.username)
            print("Left group")
            return group
        else:
            print("You are not a member of this group")
            return None
    else:
        print("Group not found")
        return None
    
def add_member_to_group(user, group, new_member_username):
    db_ref = firestore.client().collection('groups').document(group.group_name)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        members = group_data.get('members', [])
        if user.username in group_data.get('admins', []):
            if new_member_username not in members:
                member_ref = firestore.client().collection('users').document(new_member_username)
                if member_ref.get().exists:
                    members.append(new_member_username)
                    db_ref.update({
                        'members': members
                    })
                    print("Member added to group")
                    group.add_member(new_member_username)
                    return group
                else:
                    print("New member does not exist")
                    return None
            else:
                print("User is already a member of the group")
                return None
        else:
            print("You are not an admin of this group")
            return None
    else:
        print("Group not found")
        return None

def remove_member_from_group(user, group, member_username):
    db_ref = firestore.client().collection('groups').document(group.group_name)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        members = group_data.get('members', [])
        admins = group_data.get('admins', [])
        if user.username in admins:
            if member_username in members:
                members.remove(member_username)
                if member_username in admins:
                    admins.remove(member_username)
                db_ref.update({
                    'members': members,
                    'admins': admins
                })
                print("Member removed from group")
                group.remove_member(member_username)
                return group
            else:
                print("User is not a member of the group")
                return None
        else:
            print("You are not an admin of this group")
            return None
    else:
        print("Group not found")
        return None

def promote_member_to_admin(user, group, member_username):
    db_ref = firestore.client().collection('groups').document(group.group_name)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        members = group_data.get('members', [])
        admins = group_data.get('admins', [])
        if user.username in admins:
            if member_username in members:
                if member_username not in admins:
                    admins.append(member_username)
                    db_ref.update({
                        'admins': admins
                    })
                    print("Member promoted to admin")
                    group.admins.append(member_username)
                    return group
                else:
                    print("User is already an admin")
                    return None
            else:
                print("User is not a member of the group")
                return None
        else:
            print("You are not an admin of this group")
            return None
    else:
        print("Group not found")
        return None

def demote_admin_to_member(user, group, admin_username):
    db_ref = firestore.client().collection('groups').document(group.group_name)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        admins = group_data.get('admins', [])
        if user.username in admins:
            if admin_username in admins:
                if admin_username != user.username:  # Prevent self-demotion
                    admins.remove(admin_username)
                    db_ref.update({
                        'admins': admins
                    })
                    print("Admin demoted to member")
                    if hasattr(group, 'demote_from_admin'):
                        group.demote_from_admin(admin_username)
                    else:
                        # Fallback if method doesn't exist
                        if admin_username in group.admins:
                            group.admins.remove(admin_username)
                    return group
                else:
                    print("You cannot demote yourself")
                    return None
            else:
                print("User is not an admin")
                return None
        else:
            print("You are not an admin of this group")
            return None
    else:
        print("Group not found")
        return None

def disband_group(user, group):
    """Disband (delete) a group. Only admins can disband."""
    db_ref = firestore.client().collection('groups').document(group.group_name)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        admins = group_data.get('admins', [])
        if user.username in admins:
            # Remove group from all members' groups list
            members = group_data.get('members', [])
            db = firestore.client()
            for member_username in members:
                user_ref = db.collection('users').document(member_username)
                if user_ref.get().exists:
                    user_data = user_ref.get().to_dict()
                    user_groups = user_data.get('groups', [])
                    if group.group_name in user_groups:
                        user_groups.remove(group.group_name)
                        user_ref.update({
                            'groups': user_groups
                        })
                        print(f"Removed group from user {member_username}")
            
            # Delete the group document
            db_ref.delete()
            print(f"Group {group.group_name} disbanded")
            return True
        else:
            print("You are not an admin of this group")
            return False
    else:
        print("Group not found")
        return False

def display_messages(frame, messages, open_image_popup, play_video_stream):
    """Render messages (text, images, videos) inside a Tkinter frame."""
    # Clear previous widgets
    for widget in frame.winfo_children():
        widget.destroy()

    for msg in messages:
        msg_type = msg.get('type', 'text')
        content = msg.get('content', '')
        sender = msg.get('sender', 'Unknown')

        # --- Text messages ---
        if msg_type == 'text':
            lbl = Label(frame, text=f"{sender}: {content}", 
                        anchor="w", justify="left", wraplength=900,
                        bg="white", fg="black", padx=8, pady=4)
            lbl.pack(anchor="w", fill="x", pady=2)

        # --- Image messages ---
        elif msg_type == 'image' and os.path.exists(content):
            try:
                img = Image.open(content)
                # Scale image down to fit within 900x500
                img.thumbnail((MAX_IMAGE_W, MAX_IMAGE_H))
                img_tk = ImageTk.PhotoImage(img)

                img_lbl = tk.Label(frame, image=img_tk, cursor="hand2")
                img_lbl.image = img_tk  # prevent garbage collection
                img_lbl.pack(anchor="w", pady=5)
                tk.Label(frame, text=f"{sender} sent an image").pack(anchor="w")

                # Clickable event
                img_lbl.bind("<Button-1>", lambda e, path=content: open_image_popup(path))
            except Exception as e:
                tk.Label(frame, text=f"[Image failed to load: {e}]").pack(anchor="w")

        # --- Video messages ---
        elif msg_type == 'video' and os.path.exists(content):
            try:
                # Thumbnail placeholder (you could generate one)
                thumb = Image.open("video_thumbnail.jpg") if os.path.exists("video_thumbnail.jpg") else None
                if thumb:
                    thumb.thumbnail((300, 200))
                    thumb_tk = ImageTk.PhotoImage(thumb)
                    thumb_lbl = tk.Label(frame, image=thumb_tk, cursor="hand2")
                    thumb_lbl.image = thumb_tk
                    thumb_lbl.pack(anchor="w", pady=5)
                else:
                    thumb_lbl = tk.Label(frame, text=f"{sender} sent a video 🎥", fg="blue", cursor="hand2")
                    thumb_lbl.pack(anchor="w", pady=5)

                thumb_lbl.bind("<Button-1>", lambda e, path=content: play_video_stream(path))
            except Exception as e:
                tk.Label(frame, text=f"[Video failed to load: {e}]").pack(anchor="w")

        else:
            tk.Label(frame, text=f"{sender}: [Unsupported message type]").pack(anchor="w", pady=2)

def search_user_or_group(search_entry):
    print(f"Search for user or group: {search_entry}")
    # Search users
    db_ref = firestore.client().collection('users').document(search_entry)
    if db_ref.get().exists:
        if search_entry not in db_ref.get().to_dict().get('blocked_users', []):
            print(f"User {search_entry} found")
            return ("user", search_entry)
    else:
        db_ref = firestore.client().collection('gmail').document(search_entry)
        if db_ref.get().exists:
            username = db_ref.get().to_dict().get('username')
            user_ref = firestore.client().collection('users').document(username)
            if search_entry not in user_ref.get().to_dict().get('blocked_users', []):
                print(f"User with gmail {search_entry} found: {username}")
                return ("user", username)
    # Search groups
    group_ref = firestore.client().collection('groups').document(search_entry)
    if group_ref.get().exists:
        group_data = group_ref.get().to_dict()
        if search_entry in group_data.get('members', []):
            print(f"Group {search_entry} found")
            return ("group", search_entry)
    # Search by gmail
    db_ref = firestore.client().collection('gmail').document(search_entry)
    if db_ref.get().exists:
        username = db_ref.get().to_dict().get('username')
        user_ref = firestore.client().collection('users').document(username)
        user_data = user_ref.get().to_dict()
        return ("user", username)
    print(f"No user or group found for {search_entry}")
    return (None, None)

def search_users_by_pattern(search_query, current_user, limit=20):
    """
    Search for users in Firebase by username or gmail pattern.
    Returns list of users matching the search query.
    - Không hiện người đã chặn mình
    - Không hiện người mình đã chặn
    - Nếu không phải bạn bè và người đó đã chặn mình thì không hiện trong kết quả tìm kiếm
    Optimized: Limits results to improve performance.
    
    Args:
        search_query: Search pattern to match
        current_user: User object of the current user
        limit: Maximum number of results to return (default 20)
    """
    try:
        db = firestore.client()
        search_lower = search_query.lower()
        results = []
        
        # Load current user để lấy danh sách bạn bè và blocked users
        current_user_obj = load_user(current_user.username)
        if not current_user_obj:
            print("Current user not found")
            return []
        
        current_friends = current_user_obj.friends if hasattr(current_user_obj, 'friends') else []
        current_blocked = current_user_obj.blocked_users if hasattr(current_user_obj, 'blocked_users') else []
        
        # Get all users with early exit when limit is reached
        users_ref = db.collection('users').stream()
        
        for user_doc in users_ref:
            # Early exit if we've reached the limit
            if len(results) >= limit:
                break
                
            user_data = user_doc.to_dict()
            username = user_data.get('username', '')
            gmail = user_data.get('gmail', '')
            
            # Skip current user
            if username == current_user.username:
                continue
            
            # Skip nếu người đó đã chặn mình (không cho search ra mình)
            if current_user.username in user_data.get('blocked_users', []):
                continue
            
            # Skip nếu mình đã chặn người đó
            if username in current_blocked:
                continue
            
            # Check if search query matches username or gmail
            if (search_lower in username.lower() or 
                search_lower in gmail.lower()):
                results.append({
                    'username': username,
                    'gmail': gmail,
                    'status': user_data.get('status', 'offline'),
                    'avatar': user_data.get('avatar', username[:2].upper() if username else '?'),
                    'bio': user_data.get('bio', '')
                })
        
        return results
    except Exception as e:
        print(f"Error searching users: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_messages_in_chats(search_query, current_user):
    """
    Search for messages containing the search query across all user's chats.
    Returns list of chat IDs that contain matching messages.
    Includes both possible chat_id formats for direct chats.
    """
    try:
        search_lower = search_query.lower()
        matching_chat_ids = set()
        
        # Get all chats for the user
        db_ref = firestore.client().collection('chat')
        
        # Search in direct chats
        for friend in current_user.friends:
            doc1 = f"{current_user.username}_{friend}"
            doc2 = f"{friend}_{current_user.username}"
            
            # Check both possible document IDs
            found_match = False
            for chat_id in [doc1, doc2]:
                chat_ref = db_ref.document(chat_id)
                if chat_ref.get().exists:
                    # Search in all messages of this chat
                    messages_query = chat_ref.collection('conversation').stream()
                    for msg_doc in messages_query:
                        msg_data = msg_doc.to_dict()
                        content = msg_data.get('content', '')
                        if content and search_lower in content.lower():
                            # Add both formats to ensure matching works regardless of which format is used
                            matching_chat_ids.add(doc1)
                            matching_chat_ids.add(doc2)
                            found_match = True
                            break
                    if found_match:
                        break  # Found a match, no need to check the other format
        
        # Search in group chats
        for group_name in current_user.groups:
            group_ref = firestore.client().collection('groups').document(group_name)
            if group_ref.get().exists:
                group_data = group_ref.get().to_dict()
                if current_user.username in group_data.get('members', []):
                    # Search in all messages of this group
                    messages_query = group_ref.collection('conversation').stream()
                    for msg_doc in messages_query:
                        msg_data = msg_doc.to_dict()
                        content = msg_data.get('content', '')
                        if content and search_lower in content.lower():
                            matching_chat_ids.add(group_name)
                            break  # Found a match, no need to check more messages
        
        return list(matching_chat_ids)
    except Exception as e:
        print(f"Error searching messages in chats: {e}")
        return []

def log_out(user):
    """
    Log out a user by updating their status to offline and setting last_active timestamp.
    
    Args:
        user: User object with username attribute or username string
        
    Returns:
        bool: True if logout successful, False otherwise
    """
    try:
        # Handle both User object and username string
        if hasattr(user, 'username'):
            username = user.username
        else:
            username = str(user)
        
        if not username:
            print("❌ Cannot logout: username is empty")
            return False
        
        print(f"🔄 Logging out user: {username}")
        db_ref = firestore.client().collection('users').document(username)
        user_doc = db_ref.get()
        
        if user_doc.exists:
            # Update status to offline and set last_active timestamp
            db_ref.update({
                'last_active': firestore.SERVER_TIMESTAMP,
                'status': "offline"
            })
            
            # Update user object if it's a User object
            if hasattr(user, 'status'):
                user.status = "offline"
            
            print(f"✅ User {username} logged out successfully (status updated to offline)")
            return True
        else:
            print(f"❌ User {username} not found in database")
            return False
    except Exception as e:
        print(f"❌ Error logging out user: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def translate_text(message, target_language):
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=target_language)
        translated_text = translator.translate(text=message)
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return message  # Return original text if translation fails

def get_final_message_timestamp(chat):
    """Get the timestamp of the last message in a chat by querying the conversation subcollection."""
    try:
        db_ref = firestore.client().collection('chat').document(chat)
        if not db_ref.get().exists:
            return datetime.min
        
        # Query the last message from subcollection (most efficient - only gets 1 document)
        messages_query = db_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(1).stream()
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            fs_timestamp = msg_data.get('timestamp')
            if fs_timestamp:
                return fs_timestamp
        return datetime.min
    except Exception as e:
        print(f"Error getting final message timestamp for {chat}: {e}")
        return datetime.min

def get_final_message_timestamp_group(group):
    """Get the timestamp of the last message in a group by querying the conversation subcollection."""
    try:
        db_ref = firestore.client().collection('groups').document(group)
        if not db_ref.get().exists:
            return datetime.min
        
        # Query the last message from subcollection (most efficient - only gets 1 document)
        messages_query = db_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(1).stream()
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            fs_timestamp = msg_data.get('timestamp')
            if fs_timestamp:
                return fs_timestamp
        return datetime.min
    except Exception as e:
        print(f"Error getting final message timestamp for group {group}: {e}")
        return datetime.min

def get_final_message_content(chat):
    """Get the content of the last message in a chat by querying the conversation subcollection."""
    try:
        db_ref = firestore.client().collection('chat').document(chat)
        if not db_ref.get().exists:
            return 'Chưa có'
        
        # Query the last message from subcollection (most efficient - only gets 1 document)
        messages_query = db_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(1).stream()
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            if msg_data.get('is_media', False):
                media_type = msg_data.get('media_type', 'File')
                return f"[{media_type.capitalize()}]"
            return msg_data.get('content', 'Chưa có')
        return 'Chưa có'
    except Exception as e:
        print(f"Error getting final message content for {chat}: {e}")
        return 'Chưa có'

def get_final_message_content_group(group):
    """Get the content of the last message in a group by querying the conversation subcollection."""
    try:
        db_ref = firestore.client().collection('groups').document(group)
        if not db_ref.get().exists:
            return ''
        
        # Query the last message from subcollection (most efficient - only gets 1 document)
        messages_query = db_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(1).stream()
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            if msg_data.get('is_media', False):
                media_type = msg_data.get('media_type', 'File')
                return f"[{media_type.capitalize()}]"
            return msg_data.get('content', '')
        return ''
    except Exception as e:
        print(f"Error getting final message content for group {group}: {e}")
        return ''

def load_chat_list(user):
    """
    Load chat list for a user, optimized to batch queries and minimize database calls.
    """
    db = firestore.client()
    chat_list = []
    
    # Load user statuses for all friends (optimized: only get status field)
    friends_statuses = {}
    if user.friends:
        users_ref = db.collection('users')
        for friend in user.friends:
            friend_doc = users_ref.document(friend).get()
            if friend_doc.exists:
                friends_statuses[friend] = friend_doc.to_dict().get('status', 'offline')
            else:
                friends_statuses[friend] = 'offline'
    
    # Process direct chats
    chat_ref = db.collection('chat')
    for chat in user.friends:
        doc1 = f"{user.username}_{chat}"
        doc2 = f"{chat}_{user.username}"
        
        # Check both possible document IDs
        chat_doc_ref = None
        chat_id = None
        if chat_ref.document(doc1).get().exists:
            chat_doc_ref = chat_ref.document(doc1)
            chat_id = doc1
        elif chat_ref.document(doc2).get().exists:
            chat_doc_ref = chat_ref.document(doc2)
            chat_id = doc2
        
        if chat_doc_ref:
            # Get last message in one query
            last_msg_query = chat_doc_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(1).stream()
            last_message_content = 'Chưa có'
            last_timestamp = datetime.min
            
            for msg_doc in last_msg_query:
                msg_data = msg_doc.to_dict()
                fs_timestamp = msg_data.get('timestamp')
                if fs_timestamp:
                    last_timestamp = fs_timestamp
                    if msg_data.get('is_media', False):
                        media_type = msg_data.get('media_type', 'File')
                        last_message_content = f"[{media_type.capitalize()}]"
                    else:
                        last_message_content = msg_data.get('content', 'Chưa có')
                break
            
            chat_ele = {
                "id": chat_id,
                "type": 'direct',
                "name": chat,
                "lastMessage": last_message_content,
                "timestamp": last_timestamp,
                "avatar": chat[:2].upper() if chat else '?',  # Generate avatar from name
                "status": friends_statuses.get(chat, 'offline'),
                "unread": 0
            }
            chat_list.append(chat_ele)
    
    # Process group chats
    if user.groups:
        groups_ref = db.collection('groups')
        
        for group in user.groups:
            group_doc = groups_ref.document(group).get()
            if not group_doc.exists:
                continue
                
            group_data = group_doc.to_dict()
            if user.username not in group_data.get('members', []):
                continue
            
            # Get last message in one query
            group_ref = groups_ref.document(group)
            last_msg_query = group_ref.collection('conversation').order_by('timestamp', direction='DESCENDING').limit(1).stream()
            last_message_content = ''
            last_timestamp = datetime.min
            
            for msg_doc in last_msg_query:
                msg_data = msg_doc.to_dict()
                fs_timestamp = msg_data.get('timestamp')
                if fs_timestamp:
                    last_timestamp = fs_timestamp
                    if msg_data.get('is_media', False):
                        media_type = msg_data.get('media_type', 'File')
                        last_message_content = f"[{media_type.capitalize()}]"
                    else:
                        last_message_content = msg_data.get('content', '')
                break
            
            group_ele = {
                "id": group,
                "type": 'group',
                "name": group,
                "lastMessage": last_message_content,
                "timestamp": last_timestamp,
                "avatar": 'GR',  # placeholder for real avatar url
                "status": 'group',
                "unread": 0
            }
            chat_list.append(group_ele)

    # Helper function to get sortable timestamp value (convert to timestamp float for safe comparison)
    def get_sortable_timestamp(ts):
        """Convert timestamp to sortable float value, handling both naive and aware datetimes."""
        if not isinstance(ts, datetime):
            return 0.0  # Use 0.0 for missing timestamps
        
        # Check if it's the minimum datetime
        try:
            if ts == datetime.min:
                return 0.0
        except TypeError:
            # If comparison fails (naive vs aware), treat as minimum
            return 0.0
        
        # Convert to timestamp (seconds since epoch) for safe comparison
        # This works for both timezone-aware and naive datetimes
        try:
            if ts.tzinfo is not None:
                # Timezone-aware: convert to UTC timestamp
                return ts.timestamp()
            else:
                # Timezone-naive: assume UTC and convert to timestamp
                # Create a timezone-aware version in UTC
                from datetime import timezone
                ts_utc = ts.replace(tzinfo=timezone.utc)
                return ts_utc.timestamp()
        except (OSError, OverflowError, ValueError):
            # Fallback for very old dates or invalid timestamps
            return 0.0
    
    # Sort by timestamp (most recent first)
    sorted_chat = sorted(chat_list, key=lambda x: get_sortable_timestamp(x['timestamp']), reverse=True)
    
    # Format the timestamp before sending
    for chat in sorted_chat:
        # Check if the timestamp is a datetime object
        if isinstance(chat['timestamp'], datetime):
            # Convert to ISO 8601 string format (e.g., "2025-10-31T15:30:00")
            if chat['timestamp'] == datetime.min:
                chat['timestamp'] = ""
            else:
                # Handle both timezone-aware and naive datetimes
                if chat['timestamp'].tzinfo is not None:
                    # Timezone-aware: convert to UTC then to ISO string
                    chat['timestamp'] = chat['timestamp'].isoformat()
                else:
                    # Timezone-naive: convert directly to ISO string
                    chat['timestamp'] = chat['timestamp'].isoformat()
    
    return sorted_chat

def load_friends_list(user):
    db_ref = firestore.client().collection('chat')
    return_val = []
    for friend in user.friends:
        db_ref = firestore.client().collection('users').document(friend)
        if db_ref.get().exists:
            friend_data = db_ref.get().to_dict()
            friend_ele = {
                "username": friend,
                "avatar": friend_data.get('avatar', friend[:2].upper()),
                "status": friend_data.get('status', 'offline'),
                "bio": friend_data.get('bio', ''),
                "gmail": friend_data.get('gmail', '')
            }
            return_val.append(friend_ele)
    return return_val

def load_user(username):
    """
    Load user from database with caching to improve performance.
    Cache expires after CACHE_TTL_SECONDS (30 seconds by default).
    """
    global _user_cache, _cache_timestamps
    
    # Check cache first
    if username in _user_cache:
        cache_time = _cache_timestamps.get(username, 0)
        current_time = datetime.now().timestamp()
        # Use cache if it's still valid (within TTL)
        if current_time - cache_time < CACHE_TTL_SECONDS:
            return _user_cache[username]
        else:
            # Cache expired, remove it
            _user_cache.pop(username, None)
            _cache_timestamps.pop(username, None)
    
    # Load from database
    user = User(username, None, None)
    db_ref = firestore.client().collection('users').document(username).get()
    if db_ref.exists:
        data = db_ref.to_dict()
        user.password = data.get('password')
        # Lấy gmail trực tiếp từ database, không mã hóa
        user.gmail = data.get('gmail', '')
        print(f"Loaded gmail from database for {username}: {user.gmail}")
        user.friends = data.get('friends', [])
        user.groups = data.get('groups', [])
        user.avatar = data.get('avatar')
        user.bio = data.get('bio')
        user.ip_address = data.get('ip_address')
        user.last_active = data.get('last_active')
        user.status = data.get('status', 'offline')
        user.blocked_users = data.get('blocked_users', [])
        user.password = data.get('password')
        user.notifications = data.get('notifications', [])
        user.requests = data.get('requests', [])
        
        # Store in cache
        _user_cache[username] = user
        _cache_timestamps[username] = datetime.now().timestamp()
        
        return user
    else:
        print("User does not exist")
        return None

def send_group_invite(from_username, to_username, group_name):
    # Lấy dữ liệu user và group
    from_user_data = db.collection('users').document(from_username).get()
    to_user_doc_ref = db.collection('users').document(to_username)
    to_user_data = to_user_doc_ref.get()
    group_data = db.collection('groups').document(group_name).get()

    # Khởi tạo tham chiếu đến subcollection 'requests' của người nhận
    to_user_requests_subcollection = to_user_doc_ref.collection('requests')

    # Kiểm tra điều kiện cơ bản
    if (from_user_data.exists and
        to_user_data.exists and
        group_data.exists and
        to_username not in group_data.to_dict().get('members', []) and
        to_username not in from_user_data.to_dict().get('blocked_users', []) and
        from_username not in to_user_data.to_dict().get('blocked_users', [])):
        
        # 1. Kiểm tra lời mời đã được gửi chưa (Query subcollection)
        existing_invite_query = to_user_requests_subcollection.where('from_username', '==', from_username).where('type', '==', 'group').where('group_name', '==', group_name).limit(1).get()

        if existing_invite_query:
            print("Group invite already sent")
            return True
            
        # 2. Gửi lời mời mới (Thêm Document vào Subcollection)
        new_request = {
            'to_username': to_username, # Vẫn giữ để làm đầy đủ metadata
            'from_username': from_username,
            'type': 'group',
            'group_name': group_name,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'group_member_count': len(group_data.to_dict().get('members', []))
        }
        
        try:
            # Lưu request vào subcollection 'requests' của document user 'to_username'
            to_user_requests_subcollection.add(new_request) 
            print(f"Group invite for '{group_name}' sent from '{from_username}' to '{to_username}'.")
            return True
        except Exception as e:
            print(f"Error sending group invite: {e}")
            return False

    else:
        print("User or group not found, user is already a member, or you blocked/are blocked by this user.")
        return False

def send_friend_request(from_username, to_username):
    # Kiểm tra không gửi cho chính mình
    if from_username == to_username:
        print("Cannot send friend request to yourself")
        return False
    
    # Lấy dữ liệu user
    from_user_doc_ref = db.collection('users').document(from_username)
    from_user_data = from_user_doc_ref.get()
    to_user_doc_ref = db.collection('users').document(to_username)
    to_user_data = to_user_doc_ref.get()
    
    # Kiểm tra user tồn tại
    if not from_user_data.exists:
        print(f"From user {from_username} not found")
        return False
    
    if not to_user_data.exists:
        print(f"To user {to_username} not found")
        return False
    
    from_user_dict = from_user_data.to_dict()
    to_user_dict = to_user_data.to_dict()
    
    # Kiểm tra blocked users
    if to_username in from_user_dict.get('blocked_users', []):
        print(f"You have blocked {to_username}")
        return False
    
    if from_username in to_user_dict.get('blocked_users', []):
        print(f"You are blocked by {to_username}")
        return False
    
    # Kiểm tra đã là bạn chưa
    from_friends = from_user_dict.get('friends', [])
    to_friends = to_user_dict.get('friends', [])
    
    if to_username in from_friends or from_username in to_friends:
        print(f"{from_username} and {to_username} are already friends")
        return False
    
    # Khởi tạo tham chiếu đến subcollection 'requests' của người nhận
    to_user_requests_subcollection = to_user_doc_ref.collection('requests')

    # Kiểm tra request đã được gửi chưa (Query subcollection)
    existing_request_query = to_user_requests_subcollection.where('from_username', '==', from_username).where('type', '==', 'friend').limit(1).get()
    
    if list(existing_request_query):
        print("Friend request already sent")
        return True

    # Gửi request mới (Thêm Document vào Subcollection)
    new_request = {
        'to_username': to_username, # Vẫn giữ để làm đầy đủ metadata
        'from_username': from_username,
        'type': 'friend',
        'timestamp': firestore.SERVER_TIMESTAMP,
    }
    
    try:
        # Lưu request vào subcollection 'requests' của document user 'to_username'
        to_user_requests_subcollection.add(new_request)
        print(f"Friend request sent from {from_username} to {to_username}")
        return True
    except Exception as e:
        print(f"Error sending friend request: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_request(user):
    """
    Tải tất cả các yêu cầu (friend requests, group invites) đang chờ 
    dành cho người dùng được truyền vào từ subcollection 'requests'.
    """
    try:
        username = user.username
    except AttributeError:
        # Giả định user là username string
        username = str(user)
    print(3231)
    # Tham chiếu đến subcollection requests của user
    requests_ref = db.collection('users').document(username).collection('requests')
    
    # Query collection con và sắp xếp theo timestamp giảm dần (mới nhất lên đầu)
    requests_stream = requests_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    requests_list = []
    for doc in requests_stream:
        # Lấy dữ liệu của request
        request_data = doc.to_dict()
        # THÊM request_id là ID của document subcollection
        request_data['request_id'] = doc.id
        
        requests_list.append(request_data)
        
    # requests_list chứa: [{..., 'request_id': 'unique_firestore_id', ...}]
    return requests_list

def accept_friend_request(to_username, request_id, from_username):
    """
    Accept friend request: thêm bạn vào cả 2 phía và xóa request khỏi subcollection.
    
    Args:
        to_username: Người nhận request (người đang accept)
        request_id: ID của request document trong subcollection
        from_username: Người gửi request (người muốn kết bạn)
    """
    try:
        # Kiểm tra user tồn tại
        to_user_ref = db.collection('users').document(to_username)
        from_user_ref = db.collection('users').document(from_username)
        
        to_user_data = to_user_ref.get()
        from_user_data = from_user_ref.get()
        
        if not to_user_data.exists:
            print(f"To user {to_username} not found")
            return False
        
        if not from_user_data.exists:
            print(f"From user {from_username} not found")
            return False
        
        # Kiểm tra request tồn tại
        request_ref = to_user_ref.collection('requests').document(request_id)
        request_data = request_ref.get()
        
        if not request_data.exists:
            print(f"Request {request_id} not found")
            return False
        
        # Kiểm tra request có đúng type và from_username không
        req_dict = request_data.to_dict()
        if req_dict.get('type') != 'friend' or req_dict.get('from_username') != from_username:
            print("Request type or from_username mismatch")
            return False
        
        # Kiểm tra đã là bạn chưa
        to_user_dict = to_user_data.to_dict()
        from_user_dict = from_user_data.to_dict()
        
        to_friends = to_user_dict.get('friends', [])
        from_friends = from_user_dict.get('friends', [])
        
        if from_username in to_friends or to_username in from_friends:
            print(f"{from_username} and {to_username} are already friends")
            # Vẫn xóa request dù đã là bạn
            request_ref.delete()
            return True
        
        # Thêm bạn vào cả 2 phía
        if from_username not in to_friends:
            to_friends.append(from_username)
        
        if to_username not in from_friends:
            from_friends.append(to_username)
        
        # Update friends list cho cả 2 user
        to_user_ref.update({'friends': to_friends})
        from_user_ref.update({'friends': from_friends})
        
        # Tạo chat reference nếu chưa có
        _get_or_create_chat_ref(to_username, from_username)
        
        # Xóa request khỏi subcollection
        request_ref.delete()
        
        print(f"Friend request accepted: {from_username} and {to_username} are now friends")
        return True
        
    except Exception as e:
        print(f"Error accepting friend request: {e}")
        import traceback
        traceback.print_exc()
        return False

def reject_friend_request(to_username, request_id, from_username):
    """
    Reject friend request: xóa request khỏi subcollection.
    
    Args:
        to_username: Người nhận request (người đang reject)
        request_id: ID của request document trong subcollection
        from_username: Người gửi request (người bị từ chối)
    """
    try:
        # Kiểm tra user tồn tại
        to_user_ref = db.collection('users').document(to_username)
        to_user_data = to_user_ref.get()
        
        if not to_user_data.exists:
            print(f"To user {to_username} not found")
            return False
        
        # Kiểm tra request tồn tại
        request_ref = to_user_ref.collection('requests').document(request_id)
        request_data = request_ref.get()
        
        if not request_data.exists:
            print(f"Request {request_id} not found")
            return False
        
        # Kiểm tra request có đúng type và from_username không (optional validation)
        req_dict = request_data.to_dict()
        if req_dict.get('type') != 'friend':
            print("Request is not a friend request")
            return False
        
        # Xóa request khỏi subcollection
        request_ref.delete()
        
        print(f"Friend request rejected: {to_username} rejected request from {from_username}")
        return True
        
    except Exception as e:
        print(f"Error rejecting friend request: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_blocked_user(user):
    return firestore.client().collection('users').document(user.username).get().to_dict().get('blocked_users', [])

def load_group_from_name(group_name):
    group_doc = firestore.client().collection('groups').document(group_name).get()
    if group_doc.exists:
        group_data = group_doc.to_dict()
        return Group(
            group_data.get('group_name', group_name),
            group_data.get('members', []),
            group_data.get('admins', [])
        )
    return None

def get_group_info(group_name):
    """Get group information including members and admins"""
    group_doc = firestore.client().collection('groups').document(group_name).get()
    if group_doc.exists:
        group_data = group_doc.to_dict()
        return {
            'group_name': group_data.get('group_name', group_name),
            'members': group_data.get('members', []),
            'admins': group_data.get('admins', []),
            'created_date': group_data.get('created_date'),  # If exists in Firestore
            'description': group_data.get('description', '')  # If exists in Firestore
        }
    return None


def translate_message(messages, target_lang = 'vi'):
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source='auto', target=target_lang)
    translated_text = translator.translate(text=messages)
    return translated_text

