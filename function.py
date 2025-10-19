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
import vlc
from firebase_admin import firestore
MAX_IMAGE_W, MAX_IMAGE_H = 900, 500
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
    
def login(username_entry, password_entry, user):
    print(f"Login Clicked with Username: {username_entry} and Password: {password_entry}")
    user = User(username_entry, password_entry, "None")
    db_ref = firestore.client().collection('users').document(user.username)
    doc = db_ref.get()
    if doc.exists:
        last_active = datetime.now().isoformat()
        user_data = doc.to_dict()
        if bcrypt.checkpw(user.password.encode('utf-8'), user_data['password'].encode('utf-8')):
            print("Login Successful")
            db_ref.get().to_dict()
            user.friends = user_data.get('friends', [])
            user.groups = user_data.get('groups', [])
            user.last_active = last_active
            user.ip_address = get_outbound_ip()
            db_ref.update({
                'last_active': last_active,
                'ip_address': user.ip_address,
                'status': "online"
            })
            user.status = "online"
            user.avatar = user_data.get('avatar', None)
            user.bio = user_data.get('bio', "")
            user.blocked_users = user_data.get('blocked_users', [])
            user.notifications = user_data.get('notifications', [])
            user.gmail = user_data.get('gmail', "")
            user.password = user_data.get('password', "")
            return user
        else:
            print("Incorrect Password")
            messagebox.showerror("Login Failed", "Incorrect password or username.")
            return False

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
        messagebox.showerror("Sign Up Failed", "Username already exists.")
        return False
    if firestore.client().collection('gmail').document(user.gmail).get().exists:
        print("Gmail already registered")
        messagebox.showerror("Sign Up Failed", "Gmail already registered.")
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
        'ip_address': user.ip_address,
        'last_active': user.last_active,
        'blocked_users': user.blocked_users,
        'notifications': user.notifications
    })
    firestore.client().collection('gmail').document(user.gmail).set({
        'username': user.username,
    })

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
        messagebox.showerror("Upload failed", str(e))
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
        messagebox.showerror("Error", f"Cannot load image: {e}")
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

def play_video_stream(video_url):
    """Stream video using VLC."""
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(video_url)
    player.set_media(media)

    # Create popup window for video
    video_popup = tk.Toplevel()
    video_popup.title("Video Player")
    video_popup.geometry("800x450")

    # Embed VLC in Tkinter window
    video_frame = tk.Frame(video_popup, bg="black")
    video_frame.pack(fill="both", expand=True)
    video_popup.update()

    handle = video_frame.winfo_id()
    player.set_hwnd(handle)  # Windows

    player.play()

    def on_close():
        player.stop()
        video_popup.destroy()

    video_popup.protocol("WM_DELETE_WINDOW", on_close)

def send_message_user(to_username, from_user, content):
    print(f"Sending message to {to_username}: {content}")
    db_ref = firestore.client().collection('chat').document(f"{from_user}_{to_username}")
    if not db_ref.get().exists:
        db_ref = firestore.client().collection('chat').document(f"{to_username}_{from_user}")

    if db_ref.get().exists:
        message = {
            'sender': from_user.username,
            'content': content,
            'is_media': False,
            'media_type': None,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        db_ref.update({
            'messages': firestore.ArrayUnion([message])
        })
        print("Message sent")
        notify_user(user=to_username, from_username=from_user)
        return True
    else:
        print("User not found")
        return False


def send_message_group(to_groupname, from_user, content):
    print(f"Sending message to group {to_groupname}: {content}")
    db_ref = firestore.client().collection('groups').document(to_groupname)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        if from_user.username in group_data.get('members', []):
            message = {
                'sender': from_user.username,
                'content': content,
                'is_media': False,
                'media_type': None,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            db_ref.update({
                'messages': firestore.ArrayUnion([message])
            })
            print("Message sent to group")
            for member in group_data.get('members', []):
                if member != from_user.username:
                    notify_user(user=member, from_username=from_user)
            return True
        else:
            print("You are not a member of this group")
            return False
    else:
        print("Group not found")
        return False


def load_messages_user(to_username, from_user):
    db_ref = firestore.client().collection('chat').document(f"{from_user}_{to_username}")
    if not db_ref.get().exists:
        db_ref = firestore.client().collection('chat').document(f"{to_username}_{from_user}")
    if db_ref.get().exists:
        messages = db_ref.get().to_dict().get('messages', [])
        # Sort by Firestore timestamp if present
        messages.sort(key=lambda m: m.get('timestamp', datetime.min))
        return messages
    else:
        print("User not found")
        return []

def load_messages_group(to_groupname, from_user):
    db_ref = firestore.client().collection('groups').document(to_groupname)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        if from_user.username in group_data.get('members', []):
            messages = group_data.get('messages', [])
            # Sort by Firestore timestamp if present
            messages.sort(key=lambda m: m.get('timestamp', datetime.min))
            return messages
        else:
            print("You are not a member of this group")
            return []
    else:
        print("Group not found")
        return []

def send_file_user(to_username, from_user):
    file_path = filedialog.askopenfilename()
    file_type = detect_message_type(file_path)
    if not file_path:
        return
    print(f"Sending file to {to_username}: {file_path}")
    if not os.path.exists(file_path):
        print("File does not exist")
        return False
    upload = upload_to_pcloud(file_path)
    if not upload:
        return False

    db_ref = firestore.client().collection('chat').document(f"{from_user}_{to_username}")
    if not db_ref.get().exists:
        db_ref = firestore.client().collection('chat').document(f"{to_username}_{from_user}")

    if db_ref.get().exists:
        message = {
            'sender': from_user.username,
            'content': upload,
            'is_media': True,
            'media_type': file_type,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        db_ref.update({
            'messages': firestore.ArrayUnion([message])
        })
        print("File sent")
        notify_user(user=to_username, from_username=from_user)
        return True
    else:
        print("User not found")
        return False


def send_file_group(to_groupname, from_user):
    file_path = filedialog.askopenfilename()
    file_type = detect_message_type(file_path)
    if not file_path:
        return
    print(f"Sending file to group {to_groupname}: {file_path}")
    if not os.path.exists(file_path):
        print("File does not exist")
        return False
    upload = upload_to_pcloud(file_path)
    if not upload:
        return False

    db_ref = firestore.client().collection('groups').document(to_groupname)
    if db_ref.get().exists:
        group_data = db_ref.get().to_dict()
        if from_user.username in group_data.get('members', []):
            message = {
                'sender': from_user.username,
                'content': upload,
                'is_media': True,
                'media_type': file_type,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            db_ref.update({
                'messages': firestore.ArrayUnion([message])
            })
            print("File sent to group")
            for member in group_data.get('members', []):
                if member != from_user.username:
                    notify_user(user=member, from_username=from_user)
            return True
        else:
            print("You are not a member of this group")
            return False
    else:
        print("Group not found")
        return False
    
def view_profile(user):
    db_ref = firestore.client().collection('users').document(user.username)
    if db_ref.get().exists:
        user_data = db_ref.get().to_dict()
        user = User(
            user_data['username'],
            user_data['password'],
            user_data['gmail'],
            user_data['bio'],
            user_data['status'],
            user_data['last_active'], user_data['avatar'],
            user_data['ip_address'], user_data['friends'], user_data['groups'], user_data['blocked_users'], user_data['notifications']
        )
        return user
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
            messagebox.showerror("Delete failed", data.get("error", "Unknown error"))
            return False

    except Exception as e:
        messagebox.showerror("Error", str(e))
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
    messagebox.showinfo("New Message", f"You have a new message from {from_username}")
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
    if db_ref.get().exists and friend_ref.get().exists:
        user_data = db_ref.get().to_dict()
        friends = user_data.get('friends', [])
        if friend_username not in friends:
            friends.append(friend_username)
            db_ref.update({
                'friends': friends
            })
            user.friends = friends
            print("Friend added")
        db_ref = firestore.client().collection('chat').document(f"{friend_username}_{user.username}")
        if not db_ref.get().exists:
            db_ref.set({
                'messages': []
            })
        return True
    else:
        print("User or friend not found")
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
        return False
    for member in members:
        member_ref = firestore.client().collection('users').document(member)
        if not member_ref.get().exists:
            print(f"Member {member} does not exist")
            return False
    if admin_username not in members:
        members.append(admin_username)
    db_ref.set({
        'group_name': group_name,
        'members': members,
        'admins': [admin_username],
        'messages': []
    })
    print("Group created")
    return True

def leave_group(user, group_name):
    db_ref = firestore.client().collection('groups').document(group_name)
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
            user.groups = [g for g in user.groups if g != group_name]
            print("Left group")
            return True
        else:
            print("You are not a member of this group")
            return False
    else:
        print("Group not found")
        return False
    
def add_member_to_group(user, group_name, new_member_username):
    db_ref = firestore.client().collection('groups').document(group_name)
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
                    return True
                else:
                    print("New member does not exist")
                    return False
            else:
                print("User is already a member of the group")
                return False
        else:
            print("You are not an admin of this group")
            return False
    else:
        print("Group not found")
        return False
    
def remove_member_from_group(user, group_name, member_username):
    db_ref = firestore.client().collection('groups').document(group_name)
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
                return True
            else:
                print("User is not a member of the group")
                return False
        else:
            print("You are not an admin of this group")
            return False
    else:
        print("Group not found")
        return False
    
def promote_member_to_admin(user, group_name, member_username):
    db_ref = firestore.client().collection('groups').document(group_name)
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
                    return True
                else:
                    print("User is already an admin")
                    return False
            else:
                print("User is not a member of the group")
                return False
        else:
            print("You are not an admin of this group")
            return False
    else:
        print("Group not found")
        return False
    
def demote_admin_to_member(user, group_name, admin_username):
    db_ref = firestore.client().collection('groups').document(group_name)
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
                    return True
                else:
                    print("You cannot demote yourself")
                    return False
            else:
                print("User is not an admin")
                return False
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