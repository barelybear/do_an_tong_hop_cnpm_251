# Kiến Trúc Phần Mềm - Ứng Dụng Chat Desktop

## 📐 Tổng Quan Kiến Trúc

Ứng dụng chat desktop được xây dựng theo kiến trúc **Client-Server** với **3 lớp chính**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                            │
│                    (ElectronJS + React)                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           BACKEND LAYER                             │
│                         (Python Flask)                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │   Firebase    │  │     pCloud    │  │   Translation │
        │               │  │               │  │      API      │
        │ - Firestore   │  │ - Cloud       │  │ - Google      │
        │ - Auth        │  │   Storage     │  │   Translate   │
        └───────────────┘  └───────────────┘  └───────────────┘
```

---

## 🏗️ Chi Tiết Các Lớp

### 1️⃣ LỚP FRONTEND (Client)

#### **Công nghệ:**
- **ElectronJS**: Desktop application framework
- **React 18**: UI library
- **Webpack**: Module bundler
- **Babel**: JavaScript transpiler

#### **Cấu trúc Components:**

```
src/
├── index.js                    # Entry point
├── App.js                      # Main app router
├── pages/
│   ├── LoginPage.js           # Authentication UI
│   └── MainPage.js            # Main chat interface
├── components/
│   ├── Sidebar.js             # Side navigation
│   ├── ChatList.js            # Conversation list
│   ├── ChatWindow.js          # Message display & input
│   ├── FriendList.js          # Friends management
│   ├── RequestList.js         # Friend requests
│   ├── CreateGroupModal.js    # Group creation
│   ├── UserProfile.js         # User settings
│   └── FriendOrGroupProfile.js
└── utils/
    └── api.js                 # HTTP client

main.js                         # Electron main process
```

#### **Luồng dữ liệu Frontend:**

```
User Action → Component → api.js → Backend API → Response → Component Update
```

---

### 2️⃣ LỚP BACKEND (Server)

#### **Công nghệ:**
- **Python 3.x**
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin support
- **Firebase Admin SDK**: Database & Auth integration

#### **Cấu trúc Backend:**

```
backend/
├── api.py                     # Flask app & routes
├── controller.py              # Business logic managers
├── function.py                # Database & external API calls
└── helper.py                  # Models & utilities
```

#### **Component Managers:**

```python
SystemController
├── AuthManager          # login, sign_up, forget_password
├── UserManager          # profile, friends, blocks
├── ChatManager          # messages, chat list, translation
├── FileManager          # file upload/download
├── GroupManager         # group operations
├── NotificationManager  # notifications
└── UIManager           # legacy
```

#### **API Endpoints:**

```
POST /api/process
Body: {
  "function_name": "function_name",
  "args": [arg1, arg2, ...]
}

Response: {
  "status": "success|error",
  "output": ...,
  "running": false,
  ...
}
```

---

### 3️⃣ LỚP DỊCH VỤ BÊN NGOÀI

#### 🔥 **Firebase**

##### **Firestore Database**

**Collections:**

```
📁 users/
   └── {username}/
       ├── username: string
       ├── password: string (hashed)
       ├── gmail: string
       ├── friends: string[]
       ├── groups: string[]
       ├── avatar: string (URL)
       ├── bio: string
       ├── status: 'online'|'offline'|'busy'|'hidden'
       ├── last_active: timestamp
       ├── ip_address: string
       ├── blocked_users: string[]
       ├── notifications: string[]
       └── requests: string[]

📁 gmail/
   └── {gmail}/
       └── username: string

📁 chat/
   └── {user1_user2}/           # Direct chat ID
       ├── participants: [user1, user2]
       ├── created_at: timestamp
       └── conversation/         # Sub-collection
           └── {messageId}/
               ├── sender: string
               ├── content: string
               ├── is_media: boolean
               ├── media_type: 'image'|'video'|'file'
               └── timestamp: timestamp

📁 groups/
   └── {groupName}/
       ├── group_name: string
       ├── members: string[]
       ├── admins: string[]
       ├── messages: array (legacy)
       └── conversation/         # Sub-collection
           └── {messageId}/
               ├── sender: string
               ├── content: string
               ├── is_media: boolean
               ├── media_type: string
               └── timestamp: timestamp
```

##### **Firebase Authentication**

- **Bcrypt hashing**: Passwords hashed trước khi lưu
- **Session management**: `last_active`, `status` tracking
- **IP tracking**: User IP address logging

#### ☁️ **pCloud**

##### **Chức năng:**
- **Cloud Storage** cho files/media
- **Public links** generation
- **Streaming support**

##### **API Usage:**

```
1. Upload file → pCloud → Get fileid
2. Create public link → Get URL
3. Return URL → Store in Firestore
```

##### **File Types:**
- Images (jpg, png, gif, etc.)
- Videos
- Documents
- MIME type detection

#### 🌐 **Google Translation API**

##### **Chức năng:**
- **Real-time translation** của tin nhắn
- **Multi-language support**: vi, en, ja, ko, zh

##### **Implementation:**

```python
def translate_message(message, target_language):
    # Call Google Cloud Translation API
    # Return translated text
    return translated_message
```

---

## 🔄 Luồng Dữ Liệu Chính

### 📤 **Gửi Tin Nhắn**

```
User nhập text
    ↓
ChatWindow.handleSend()
    ↓
POST /api/process → function_name: "send_message_user"
    ↓
ChatManager.send_message_user()
    ↓
function.send_message_user() → Firestore
    ↓
function.notify_user() → Update recipient notifications
    ↓
Return success → Frontend update
```

### 📎 **Upload File**

```
User chọn file
    ↓
POST /api/process → function_name: "send_file_user"
    ↓
FileManager.send_file_user()
    ↓
function.upload_to_pcloud() → pCloud API
    ↓
Get public URL
    ↓
function.send_message_user(url) → Firestore
    ↓
Return success → Frontend hiển thị
```

### 🔄 **Dịch Tin Nhắn**

```
User click "Translate"
    ↓
POST /api/process → function_name: "translate_message"
    ↓
ChatManager.translate_message()
    ↓
function.translate_text() → Google Translation API
    ↓
Return translated text → Frontend hiển thị
```

### 👥 **Đăng Nhập**

```
User nhập credentials
    ↓
POST /api/process → function_name: "login"
    ↓
AuthManager.login()
    ↓
function.login() → Firestore verify
    ↓
Update last_active, status, IP
    ↓
Load current_user → system.current_user
    ↓
Return user data → Frontend store
```

---

## 🔐 Bảo Mật

### **Authentication & Authorization**

1. **Password Hashing**: Bcrypt với salt
2. **Session Tracking**: IP + last_active
3. **Status Management**: online/offline states
4. **Block Mechanism**: blocked_users list

### **Data Protection**

1. **Firestore Rules**: Server-side validation
2. **CORS**: Origin restrictions
3. **Input Validation**: Sanitization
4. **Error Handling**: Generic error messages

---

## 🚀 Deployment Architecture

### **Local Development**

```
Frontend: npm run dev (Webpack watch) + npm start (Electron)
Backend:  python backend/api.py (Flask dev server)
```

### **Production**

```
Frontend: npm run build → Electron executable
Backend:  Gunicorn/WSGI server → HTTP/HTTPS
```

### **External Services**

```
Firebase:  Managed service (Google Cloud)
pCloud:    Managed service
Translate: Google Cloud Translation API
```

---

## 📊 Kiến Trúc Component Interaction

```
┌──────────────┐
│   Electron   │
│  Main Process│
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│                   React App                          │
│  ┌────────────┐         ┌──────────────┐            │
│  │LoginPage   │────────►│  MainPage    │            │
│  └────────────┘         └──────┬───────┘            │
│                                │                     │
│         ┌──────────────────────┼─────────────────┐   │
│         ▼                      ▼                 ▼   │
│  ┌──────────┐         ┌──────────────┐   ┌─────────┐│
│  │ Sidebar  │         │ ChatWindow   │   │Profile  ││
│  └─────┬────┘         └──────────────┘   └─────────┘│
│        │                                         │    │
│        ▼                                         ▼    │
│  ┌──────────┐                              ┌─────────┐│
│  │ChatList  │                              │CreateGrp││
│  │FriendList│                              └─────────┘│
│  │RequestList│                                        │
│  └─────┬────┘                                         │
└────────┼──────────────────────────────────────────────┘
         │
         ▼
┌────────────────────┐
│  api.js (HTTP)     │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│          Flask Backend Server               │
│  ┌────────────────────────────────────────┐ │
│  │  POST /api/process                     │ │
│  │  ├─ Controller Router                  │ │
│  │  ├─ Manager Dispatch                   │ │
│  │  └─ Function Execution                 │ │
│  └────────────────────────────────────────┘ │
└─────────┬───────────────────────────────────┘
          │
    ┌─────┼─────┬────────────────┐
    ▼     ▼     ▼                ▼
┌────────┐ ┌────────┐  ┌─────────────┐  ┌────────┐
│Firebase│ │ pCloud │  │Translation  │  │ Helper │
│Firestore│ │  API  │  │   API       │  │ Models │
└────────┘ └────────┘  └─────────────┘  └────────┘
```

---

## 📝 Ghi Chú Kiến Trúc

### **Design Patterns**

1. **MVC**: Model (helper), View (React), Controller (controller.py)
2. **Manager Pattern**: Separation of concerns
3. **Singleton**: SystemController instance
4. **Factory**: Function dispatcher

### **Scalability**

- **Horizontal**: Add more Flask workers
- **Vertical**: Database indexing, caching
- **Microservices**: Split managers to separate services

### **Future Enhancements**

- WebSocket for real-time messaging
- Redis for session caching
- S3 alternative to pCloud
- GraphQL API layer
- Message encryption
- Voice/Video calls

---

## 🎯 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend Framework** | ElectronJS | Desktop app shell |
| **UI Library** | React 18 | Component-based UI |
| **Backend Framework** | Flask (Python) | REST API server |
| **Database** | Firebase Firestore | NoSQL database |
| **Authentication** | Firebase + Bcrypt | User auth & hashing |
| **Cloud Storage** | pCloud | Media file storage |
| **Translation** | Google Translate API | Multi-language support |
| **Build Tool** | Webpack | Bundling |
| **Transpiler** | Babel | ES6+ to ES5 |

---

**Phiên bản:** 1.0  
**Ngày tạo:** 2024  
**Tác giả:** Development Team

