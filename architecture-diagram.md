# Sơ Đồ Kiến Trúc Phần Mềm

## Tổng Quan Hệ Thống

```mermaid
graph TB
    subgraph "FRONTEND LAYER"
        EL[ElectronJS Desktop App]
        REACT[React Components]
        UTILS[Utils & API Client]
    end
    
    subgraph "BACKEND LAYER"
        FLASK[Flask API Server]
        CTRL[Controller Managers]
        FUNC[Business Logic]
    end
    
    subgraph "EXTERNAL SERVICES"
        FB[(Firebase Firestore)]
        FBAUTH[Firebase Auth]
        PCLOUD[pCloud Storage]
        TRANS[Google Translate API]
    end
    
    EL --> REACT
    REACT --> UTILS
    UTILS -->|HTTP REST| FLASK
    FLASK --> CTRL
    CTRL --> FUNC
    FUNC --> FB
    FUNC --> FBAUTH
    FUNC --> PCLOUD
    FUNC --> TRANS
```

## Cấu Trúc Frontend

```mermaid
graph LR
    APP[App.js Router] --> LOGIN[LoginPage]
    APP --> MAIN[MainPage]
    
    MAIN --> SIDEBAR[Sidebar]
    MAIN --> CHATWIN[ChatWindow]
    MAIN --> PROFILE[UserProfile]
    
    SIDEBAR --> CHATLIST[ChatList]
    SIDEBAR --> FRIENDLIST[FriendList]
    SIDEBAR --> REQLIST[RequestList]
    
    CHATLIST --> API[api.js]
    FRIENDLIST --> API
    LOGIN --> API
    
    API -->|HTTP| BACKEND[Flask Backend]
```

## Backend Architecture

```mermaid
graph TB
    subgraph "API Layer"
        FLASKAPP[Flask App /api/process]
    end
    
    subgraph "Controller Layer"
        SYSTEM[SystemController]
        AUTH[AuthManager]
        USER[UserManager]
        CHAT[ChatManager]
        FILE[FileManager]
        GROUP[GroupManager]
        NOTIF[NotificationManager]
    end
    
    subgraph "Function Layer"
        DBOPS[Database Operations]
        CLOUD[Cloud Operations]
        TRANSAPI[Translation API]
    end
    
    subgraph "Data Layer"
        FIRESTORE[(Firestore)]
        PCLOUD_STORE[(pCloud)]
    end
    
    FLASKAPP --> SYSTEM
    SYSTEM --> AUTH
    SYSTEM --> USER
    SYSTEM --> CHAT
    SYSTEM --> FILE
    SYSTEM --> GROUP
    SYSTEM --> NOTIF
    
    AUTH --> DBOPS
    USER --> DBOPS
    CHAT --> DBOPS
    CHAT --> TRANSAPI
    FILE --> DBOPS
    FILE --> CLOUD
    GROUP --> DBOPS
    
    DBOPS --> FIRESTORE
    CLOUD --> PCLOUD_STORE
```

## Data Flow - Send Message

```mermaid
sequenceDiagram
    actor User
    participant CW as ChatWindow
    participant API as api.js
    participant FLASK as Flask Backend
    participant CM as ChatManager
    participant FIRE as Firestore
    participant NOTIF as NotificationManager
    
    User->>CW: Nhập tin nhắn & gửi
    CW->>API: POST /api/process
    API->>FLASK: HTTP Request
    FLASK->>CM: send_message_user()
    CM->>FIRE: Save message
    FIRE-->>CM: Success
    CM->>NOTIF: notify_user()
    NOTIF->>FIRE: Update notifications
    FIRE-->>CM: Success
    CM-->>FLASK: Response
    FLASK-->>API: JSON Response
    API-->>CW: Success
    CW->>User: Hiển thị tin nhắn
```

## Data Flow - Upload File

```mermaid
sequenceDiagram
    actor User
    participant CW as ChatWindow
    participant API as api.js
    participant FLASK as Flask Backend
    participant FM as FileManager
    participant PCLOUD as pCloud API
    participant FIRE as Firestore
    
    User->>CW: Chọn file
    CW->>API: POST /api/process
    API->>FLASK: HTTP Request
    FLASK->>FM: send_file_user()
    FM->>PCLOUD: Upload file
    PCLOUD-->>FM: Public URL
    FM->>FIRE: Save message with URL
    FIRE-->>FM: Success
    FM-->>FLASK: Response
    FLASK-->>API: JSON Response
    API-->>CW: Success
    CW->>User: Hiển thị file
```

## Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant LP as LoginPage
    participant API as api.js
    participant FLASK as Flask Backend
    participant AUTH as AuthManager
    participant FIRE as Firestore
    participant BCRYPT as Bcrypt
    
    User->>LP: Nhập username/password
    LP->>API: POST /api/process (login)
    API->>FLASK: HTTP Request
    FLASK->>AUTH: login()
    AUTH->>FIRE: Get user data
    FIRE-->>AUTH: Hashed password
    AUTH->>BCRYPT: verify_password()
    BCRYPT-->>AUTH: Valid/Invalid
    AUTH->>FIRE: Update last_active, status
    FIRE-->>AUTH: Success
    AUTH-->>FLASK: User object
    FLASK->>FIRE: Load full user data
    FLASK-->>API: User info
    API-->>LP: Success
    LP->>User: Navigate to MainPage
```

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ CHAT : participates
    USERS ||--o{ GROUPS : member_of
    CHAT ||--o{ MESSAGES : contains
    GROUPS ||--o{ MESSAGES : contains
    
    USERS {
        string username PK
        string password
        string gmail
        array friends
        array groups
        string avatar
        string bio
        string status
        timestamp last_active
        array blocked_users
        array notifications
    }
    
    CHAT {
        string chat_id PK
        array participants
        timestamp created_at
    }
    
    MESSAGES {
        string message_id PK
        string chat_id FK
        string sender
        string content
        boolean is_media
        string media_type
        timestamp timestamp
    }
    
    GROUPS {
        string group_name PK
        array members
        array admins
    }
```

## Component Interaction

```mermaid
stateDiagram-v2
    [*] --> Login
    Login --> Authenticating : Submit credentials
    Authenticating --> Login : Invalid credentials
    Authenticating --> MainPage : Success
    MainPage --> ChatList : Load chats
    MainPage --> FriendList : Manage friends
    MainPage --> ChatWindow : Select chat
    ChatWindow --> Sending : Send message
    Sending --> ChatWindow : Message sent
    ChatWindow --> Translating : Translate message
    Translating --> ChatWindow : Show translation
    MainPage --> Profile : Open settings
    Profile --> Logout : Click logout
    Logout --> Login : Confirm logout
```

## Technology Stack

```mermaid
graph LR
    subgraph "Client Stack"
        EL[ElectronJS]
        REACT[React 18]
        WEBPACK[Webpack]
        BABEL[Babel]
    end
    
    subgraph "Server Stack"
        PYTHON[Python 3.x]
        FLASK[Flask]
        CORS[Flask-CORS]
    end
    
    subgraph "Data Stack"
        FIREBASE[Firebase Admin SDK]
        BCRYPT[bcrypt]
    end
    
    subgraph "External APIs"
        PCLOUD[pCloud API]
        TRANSAPI[Google Translate]
    end
    
    EL --> REACT
    REACT --> WEBPACK
    WEBPACK --> BABEL
    PYTHON --> FLASK
    FLASK --> CORS
    FLASK --> FIREBASE
    FIREBASE --> BCRYPT
    FLASK --> PCLOUD
    FLASK --> TRANSAPI
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        FE_DEV[Frontend Dev<br/>npm run dev]
        BE_DEV[Backend Dev<br/>python api.py]
    end
    
    subgraph "Production"
        FE_PROD[Electron App<br/>Built & Packaged]
        BE_PROD[Gunicorn Server<br/>Process Pool]
    end
    
    subgraph "Cloud Services"
        FB_PROD[Firebase Production]
        PCLOUD_PROD[pCloud Production]
        TRANS_PROD[Google Cloud]
    end
    
    FE_DEV --> BE_DEV
    FE_PROD --> BE_PROD
    BE_DEV --> FB_PROD
    BE_DEV --> PCLOUD_PROD
    BE_DEV --> TRANS_PROD
    BE_PROD --> FB_PROD
    BE_PROD --> PCLOUD_PROD
    BE_PROD --> TRANS_PROD
```

