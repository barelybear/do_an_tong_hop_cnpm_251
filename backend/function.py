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
                notify_user(user=member, from_username=from_user.username)
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

def load_messages_user(to_username, from_user):
    """
    Loads messages for a one-on-one chat and formats them into a JSON list
    for front-end consumption.
    """
    try:
        # Get the reference to the main chat document.
        # This helper ensures we look for the correct doc_id (e.g., 'user1_user2')
        chat_ref = _get_or_create_chat_ref(from_user.username, to_username)

        # Query the 'conversation' sub-collection, ordering by timestamp
        messages_query = chat_ref.collection('conversation').order_by('timestamp', direction='ASCENDING').stream()

        json_messages = []
        for msg_doc in messages_query:
            msg_data = msg_doc.to_dict()
            fs_timestamp = msg_data.get('timestamp')

            # Skip any message that might have failed to save its timestamp
            if fs_timestamp is None:
                continue
            
            # Determine sender context ('me' or 'other')
            is_current_user = msg_data.get('sender') == from_user.username
            sender_id = 'me' if is_current_user else 'other'
            
            # The sender's display name
            sender_name = 'Me' if is_current_user else to_username

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
            
        return json_messages
    
    except Exception as e:
        print(f"An error occurred loading messages for user {to_username}: {e}")
        return [] # Return an empty list on failure

def load_messages_group(to_groupname, from_user):
    """
    Loads messages for a group chat and formats them into a JSON list
    for front-end consumption.
    """
    try:
        db = firestore.client()
        group_ref = db.collection('groups').document(to_groupname)
        group_doc = group_ref.get()
        
        if not group_doc.exists:
            print("Group not found")
            return []

        # Basic check to see if the user is a member
        if from_user.username not in group_doc.to_dict().get('members', []):
            print("You are not a member of this group")
            return []

        # Query the sub-collection, ordering by timestamp
        messages_query = group_ref.collection('conversation').order_by('timestamp', direction='ASCENDING').stream()

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

        return json_messages
        
    except Exception as e:
        print(f"An error occurred loading group messages for {to_groupname}: {e}")
        return []

def view_profile(user):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        user_data = db_ref.get().to_dict()
        selected_user = User(
            user_data['username'],
            user_data['password'],
            user_data['gmail'],
            user_data['bio'],
            user_data['status'],
            user_data['last_active'], user_data['avatar'],
            user_data['ip_address'], user_data['friends'], user_data['groups'], user_data['blocked_users'], user_data['notifications'], user_data['requests']
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
            print("Friend added")
        _get_or_create_chat_ref(user.username, friend_username)
        return True
    else:
        print("User or friend not found or you blocked this user.")
        return False
    
def remove_friend(user, friend_username):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        user_data = db_ref.get().to_dict()
        friends = user_data.get('friends', [])
        if friend_username in friends:
            friends.remove(friend_username)
            db_ref.update({
                'friends': friends
            })
            user.friends = friends
            print("Friend removed")
        return True
    else:
        print("User not found")
        return False
    
def block_user(user, block_username):
    db_ref = firestore.client().collection('users').document(user.username)
    block_ref = firestore.client().collection('users').document(block_username)
    if db_ref.get().exists and block_ref.get().exists:
        user_data = db_ref.get().to_dict()
        blocked_users = user_data.get('blocked_users', [])
        friends = user_data.get('friends', [])
        if block_username not in blocked_users:
            blocked_users.append(block_username)
            if block_username in friends:
                friends.remove(block_username)
            db_ref.update({
                'blocked_users': blocked_users,
                'friends': friends
            })
            user.blocked_users = blocked_users
            user.friends = friends
            print("User blocked")
        return True
    else:
        print("User or block target not found")
        return False
    
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
            print("User unblocked")
        return True
    else:
        print("User not found")
        return False
    
def create_group(group_name, members, admin_username):
    db_ref = firestore.client().collection('groups').document(group_name)
    if db_ref.get().exists:
        print("Group name already exists")
        return None
    for member in members:
        member_ref = firestore.client().collection('users').document(member)
        if not member_ref.get().exists:
            print(f"Member {member} does not exist")
            return None
    if admin_username not in members:
        members.append(admin_username)
    db_ref.set({
        'group_name': group_name,
        'members': members,
        'admins': [admin_username],
        'messages': []
    })
    print("Group created")
    return Group(group_name, members)

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
            user.groups = [g for g in user.groups if g != group.group_name]
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
                    group.remove_admin(admin_username)
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

def search_users_by_pattern(search_query, current_user):
    """
    Search for users in Firebase by username or gmail pattern.
    Returns list of users matching the search query.
    """
    try:
        db = firestore.client()
        search_lower = search_query.lower()
        results = []
        
        # Get all users (Note: In production, consider pagination or limiting results)
        users_ref = db.collection('users').stream()
        
        for user_doc in users_ref:
            user_data = user_doc.to_dict()
            username = user_data.get('username', '')
            gmail = user_data.get('gmail', '')
            
            # Skip current user and blocked users
            if username == current_user.username:
                continue
            if current_user.username in user_data.get('blocked_users', []):
                continue
            if username in current_user.blocked_users:
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
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        last_active = firestore.firestore.SERVER_TIMESTAMP
        db_ref.update({
            'last_active': last_active,
            'status': "offline"
        })
        user.status = "offline"
        print("User logged out")
        return True
    else:
        print("User not found")
        return False
    
def translate_text(message, target_language):
    return True # Placeholder for translation functionality

def get_final_message_timestamp(chat):
    db_ref = firestore.client().collection('chat').document(chat)
    if db_ref.get().exists:
        messages = db_ref.get().to_dict().get('messages', [])
        if messages:
            last_message = messages[-1]
            return last_message.get('timestamp', datetime.min)
    return datetime.min

def get_final_message_timestamp_group(group):
    db_ref = firestore.client().collection('groups').document(group)
    if db_ref.get().exists:
        messages = db_ref.get().to_dict().get('messages', [])
        if messages:
            last_message = messages[-1]
            return last_message.get('timestamp', datetime.min)
    return datetime.min

def get_final_message_content(chat):
    db_ref = firestore.client().collection('chat').document(chat)
    if db_ref.get().exists:
        messages = db_ref.get().to_dict().get('messages', [])
        if messages:
            last_message = messages[-1]
            if last_message.get('is_media', True):
                return f"[{last_message.get('media_type').capitalize()}]"
            return last_message.get('content', 'Chưa có')
    return 'Chưa có'

def get_final_message_content_group(group):
    db_ref = firestore.client().collection('groups').document(group)
    if db_ref.get().exists:
        messages = db_ref.get().to_dict().get('messages', [])
        if messages:
            last_message = messages[-1]
            if last_message.get('is_media', True):
                return f"[{last_message.get('media_type').capitalize()}]"
            return last_message.get('content', '')
    return ''

def load_chat_list(user):
    db_ref = firestore.client().collection('chat')
    chat_list = []
    for chat in user.friends:
        doc1 = f"{user.username}_{chat}"
        doc2 = f"{chat}_{user.username}"
        print(doc1)
        print(doc2)
        if db_ref.document(doc1).get().exists:
            chat_ele = {
                        "id": f"{user.username}_{chat}",
                        "type": 'direct',
                        "name": chat,
                        "lastMessage": get_final_message_content(doc1),
                        "timestamp": get_final_message_timestamp(doc1),
                        "avatar": 'JD', # placeholder for real avatar url
                        "status": get_status_user(chat),
                        "unread": 0
                    }
            chat_list.append(chat_ele)
        elif db_ref.document(doc2).get().exists:
            chat_ele = {
                        "id": f"{chat}_{user.username}",
                        "type": 'direct',
                        "name": chat,
                        "lastMessage": get_final_message_content(doc2),
                        "timestamp": get_final_message_timestamp(doc2),
                        "avatar": 'JD', # placeholder for real avatar url
                        "status": get_status_user(chat),
                        "unread": 0
                    }
            chat_list.append(chat_ele)
    for group in user.groups:
        group_ref = firestore.client().collection('groups').document(group)
        if group_ref.get().exists:
            group_data = group_ref.get().to_dict()
            if user.username in group_data.get('members', []):
                group_ele = {
                    "id": group,
                    "type": 'group',
                    "name": group,
                    "lastMessage": get_final_message_content_group(group),
                    "timestamp": get_final_message_timestamp_group(group),
                    "avatar": 'GR', # placeholder for real avatar url
                    "status": 'group',
                    "unread": 0
                }
                chat_list.append(group_ele)

    sorted_chat = sorted(chat_list, key=lambda x: x['timestamp'] if x['timestamp'] != datetime.min else datetime(1970, 1, 1), reverse=True)
    # --- FORMAT THE TIMESTAMP BEFORE SENDING ---
    for chat in sorted_chat:
        # Check if the timestamp is a datetime object
        if isinstance(chat['timestamp'], datetime):
            # Convert to ISO 8601 string format (e.g., "2025-10-31T15:30:00")
            chat['timestamp'] = chat['timestamp'].isoformat() if chat['timestamp'] != datetime.min else ""
    print(sorted_chat)
    return sorted_chat

def load_user(username):
    user = User(username, None, None)
    db_ref = firestore.client().collection('users').document(username).get()
    if db_ref.exists:
        data = db_ref.to_dict()
        user.password = data.get('password')
        user.gmail = data.get('gmail')
        user.friends = data.get('friends', [])
        user.groups = data.get('groups', [])
        user.avatar = data.get('avatar')
        user.bio = data.get('bio')
        user.ip_address = data.get('ip_address')
        user.last_active = data.get('last_active')
        user.password = data.get('password')
        user.notifications = data.get('notifications', [])
        user.requests = data.get('requests', [])
    else:
        print("User does not exist")
        return None
    return user

def send_friend_request(from_username, to_username):
    from_user_data = firestore.client().collection('user').document(from_username).get()
    to_user_data = firestore.client().collection('user').document(to_username).get()
    if from_user_data.exists and to_user_data.exists and to_user_data not in from_user_data.to_dict().get('blocked_users', []) and from_user_data not in to_user_data.to_dict().get('blocked_users', []):
        requests = to_user_data.to_dict().get('requests', [])
        if from_username not in requests:
            requests.append(from_username)
            firestore.client().collection('user').document(to_username).update({
                'requests': requests
            })
            print("Friend request sent")
        return True
    else:
        print("User or friend not found or you blocked this user.")
        return False
    
def load_friend_request(user):
    return firestore.client().collection('user').document(user.username).get().to_dict().get('requests', [])

def load_blocked_user(user):
    return firestore.client().collection('user').document(user.username).get().to_dict().get('blocked_users', [])

def load_group_from_name(group_name):
    group = firestore.client().collection('groups').document(group_name).get().to_dict()
    return Group(group.get('group_name'), group.get('members', []), group.get('admins',[]))

