# Listen for changes then load
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials, firestore
import function
from pathlib import Path
import time

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

# end of set up
curr_time = time.time()
def read_changes_on_chat_list(user):
    pass

def read_changes_on_chat(user, chat):
    pass

def read_changes_on_friend_list(user):
    pass