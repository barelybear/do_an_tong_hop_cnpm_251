# Chat Desktop Application

Ứng dụng chat desktop được xây dựng với ElectronJS và React.

📖 **[Xem Kiến Trúc Phần Mềm Chi Tiết](./SOFTWARE_ARCHITECTURE.md)**

🎨 **[Xem Sơ Đồ Kiến Trúc (Mermaid Diagrams)](./architecture-diagram.md)**

## Tính năng

### Quản lý tài khoản
- ✅ Đăng ký tài khoản với email, username và mật khẩu
- ✅ Xác thực Gmail
- ✅ Đăng nhập/Đăng xuất
- ✅ Đặt lại mật khẩu qua email
- ✅ Chỉnh sửa thông tin cá nhân và avatar

### Quản lý bạn bè
- ✅ Gửi lời mời kết bạn
- ✅ Chấp nhận/Từ chối lời mời kết bạn
- ✅ Xóa bạn (Hủy kết bạn)
- ✅ Chặn/Bỏ chặn người dùng
- ✅ Tìm kiếm người dùng theo username hoặc gmail

### Trò chuyện
- ✅ Gửi tin nhắn văn bản
- ✅ Gửi tệp đa phương tiện (ảnh, video) - tối đa 4MB
- ✅ Hiển thị lịch sử trò chuyện
- ✅ Tạo nhóm chat
- ✅ Dịch tin nhắn (tích hợp Cloud Translation API)

### Cài đặt
- ✅ Thiết lập thông báo
- ✅ Quyền riêng tư
- ✅ Chế độ tối

## Cài đặt

### Yêu cầu
- Node.js (phiên bản 14 trở lên)
- npm hoặc yarn

### Cài đặt dependencies
1. Cài các dependencies
\`\`\`bash
npm install
\`\`\`
2. Cài key(tạo một file json như sau với tên trans-chat-key.json)
{
  "type": "service_account",
  "project_id": "trans-chat-373cf",
  "private_key_id": "2e63e6dd5ab371105207e19cd4b5c7f407e508d7",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDSlzx3ubChSGhm\nOhEZUQQxhaD0x1beaUSBC6FWdv0W/UWA9jmC4DAVtxc6deIStdlEh8wYPfY/LETK\n26o/UZzl6mWB38quiJ0geDtdVOM8jO6OU8yM44JVHXEBiVtbw5TB/l/AuEC/mxIj\nthAvTT82BiPx0OU50DFVB0meK4WXRtQ7TWnVkNOHcMBRB5tY45Ln6e5wJ+mqB8Gg\nN2RQRiMmjRLLts1/Qu1Oee7Rt2VtaqxNRJP39vojaWe4u2l9Elfl56nncSk7m9E7\nS2b2od3+qK0YnwpBXlH0O/ZUoOh42PJlD5MqlntcgSkXCYsrVkTaTvYW4Vi0uQmX\nVv9icdv/AgMBAAECggEAVVgMHdsnnV0qTg+HQXLHV8h3b+vfJRiVNhUAB/oF3Iy8\n36Qpr4PqiMpgBAWlHn8K845zJHnr8zMeF/YI20tYYgbpp0YKLkxYHUIMkOjnhHD6\n9rw4P/qtpY/ebch8OUacYTgVFxW0y9Hs+oL8sSbFkL/RTl0hoJnifDqNV6f8pk7F\nwGVmq4wSaryEkmC9IMfYQg+sA2VL04bTczUrC1xy/u5KgwFISrq7FiDZKhDYsFVV\nXiiG+r+xdIET4aYTSYfVoNWG8PywRjiNScv9SzMb6a/l4Q69V72d26MjkrhNdZcw\nZzPxxvZqIkUYud8R5TUlA6ZZzsiGmDJ+cmfSWTaEyQKBgQD7yt4oGbdqwlr7QZRD\nFcYowf5MwDhbvgCtU7Miho8LWpU6/k4Tz5SZtBqX+IvCZGwkjRwmtlQxU6UHNJzS\nwVRYG9BuZ9XMHuXQQQH1uYD7hqvLZuHMkp8qqpISNBsUYtHcL6b0DVUqPCDNUgJQ\nNpxwYe3if4rl4RRePHHndJYApwKBgQDWHB0MH6a1uPl/ExJdVPsF9FH3H9Vr8ACN\n2Qxafx7/+cws3IKZAE3PlSYbP37DgGEh8kVNmGW05ChTtXclMpscONkURgOiDxQh\nfFvj125cFmDPgaVGcwBajv2Ci7xRv00+Cq+7Q922zvwU+TMqeJaWrt+DV2QfTNSI\nr3yWfX8c6QKBgQCog3Q9GED19U9YuuIUJ71wR6z/BuJxG+9uEQdhgva3HY+kZNAy\nWAnW+H+X1+MJXZY2vC3sBrjALn/TG7YdIwBk23Cag2nF66PYxbkfEGCvdckCHz/d\nXv+hWXjbL/4znZNgLpAo48dstcMqRsl/j50RZakEnmGCSioMi52bzx4ZHwKBgFyp\ngBy+Gf0tl7TaQSlpXNY/3bVQ7qGvFd5N4B3ORFFN/4Iu0Mp8qjA7gWlremYLyn3R\nhxLE8MdvstA/idfsZdq586DliC77zZ+MXYxmsNljyfQkTK4HmVCX77ku1oqee0Rt\nhY5LGcpDHC/LhcxMsgd2mT8TdD5jltus7wOGPpv5AoGBAOQWw3bMY09K+Wesc5p8\nk0VNZgHa8L20CTKfzAl3Rl8I79SiM5aO0EETCIh4nA0U+MCqui/6YfnaJ4b65rlw\nEwX5Sn08ep3ofgEAA/DXGqwmr1tXKruzxS1NRdtmerr21JuS92bhsz4Jz86du6Om\nXNNRoM3rzzbccmlmeh+StPpN\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@trans-chat-373cf.iam.gserviceaccount.com",
  "client_id": "113665527059340126977",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40trans-chat-373cf.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

### Chạy ứng dụng

1. Build React app:
\`\`\`bash
npm run dev
\`\`\`

2. Trong terminal khác, chạy Electron:
\`\`\`bash
npm start
\`\`\`

3. Trong terminal khác chạy api python:
\`\`\`bash
py backend\api.py
### Build production

\`\`\`bash
npm run build
npm start
\`\`\`

## Cấu trúc thư mục

```text
chatDessktop/
├── main.js                 # Electron main process
├── webpack.config.js       # Webpack configuration
├── package.json
├── public/
│   └── index.html
├── src/
│   ├── index.js           # React entry point
│   ├── App.js             # Main App component
│   ├── pages/
│   │   ├── LoginPage.js   # Login/Register page
│   │   └── MainPage.js    # Main application page
│   ├── components/
│   │   ├── Sidebar.js     # Left sidebar with tabs
│   │   ├── ChatList.js    # Chat list component
│   │   ├── FriendList.js  # Friends list component
│   │   ├── RequestList.js # Friend requests component
│   │   ├── ChatWindow.js  # Chat window component
│   │   ├── CreateGroupModal.js  # Create group modal
│   │   └── UserProfile.js # User profile sidebar
│   └── styles/
│       ├── global.css
│       ├── LoginPage.css
│       ├── MainPage.css
│       ├── Sidebar.css
│       ├── ChatList.css
│       ├── FriendList.css
│       ├── RequestList.css
│       ├── ChatWindow.css
│       ├── CreateGroupModal.css
│       └── UserProfile.css
└── dist/                   # Build output
```

## Công nghệ sử dụng

### Frontend
- **ElectronJS**: Framework để xây dựng ứng dụng desktop
- **React 18**: Thư viện UI component-based
- **Webpack**: Module bundler
- **Babel**: JavaScript compiler

### Backend
- **Python 3.x**: Server-side logic
- **Flask**: REST API framework
- **Flask-CORS**: Cross-origin support
- **Firebase Admin SDK**: Database & Auth integration
- **Bcrypt**: Password hashing

### External Services
- **Firebase Firestore**: NoSQL database cho users, chats, messages
- **Firebase Authentication**: Xác thực người dùng
- **pCloud API**: Lưu trữ file đa phương tiện (ảnh, video)
- **Google Translation API**: Dịch tin nhắn đa ngôn ngữ

### Kiến Trúc
- **Client-Server Architecture**: 3 lớp (Frontend → Backend → Services)
- **RESTful API**: HTTP/JSON communication
- **Manager Pattern**: Separation of concerns

## Tích hợp Firebase

Để kết nối với Firebase Firestore, bạn cần:

1. Tạo project trên Firebase Console
2. Tạo file `src/firebase.js`:

\`\`\`javascript
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
\`\`\`

3. Cài đặt Firebase SDK:
\`\`\`bash
npm install firebase
\`\`\`

## Database Schema (Firestore)

### Collection: users
\`\`\`
users/{userId}
  - username: string
  - hashed_passwords: string
  - profiles: string
  - gmail: string
  - friends: array
  - friend_request: array
  - blocked_users: array
  - URL_jpg_avatar: string
  - session: timestamp
  - status: 'online' | 'offline'
\`\`\`

### Collection: chat
\`\`\`
chat/{chatId}
  - -1 (metadata document)
    - type: 'direct' | 'group'
    - chat_name: string (for group)
    - date_created: timestamp
    - array_nickname: array of objects
  
  - {timestamp} (message documents)
    - nội_dung_tin_nhắn: string
    - người_gửi: string (userId)
    - được_ghim: boolean
    - tin_nhắn_phản_hồi: boolean
    - array_emoji: array
    - có_phải_file_đa_phương_tiện: boolean
    - có_phải_ảnh: boolean (if file)
\`\`\`

## Ghi chú

- Hiện tại ứng dụng sử dụng mock data để demo
- Cần tích hợp Firebase để có chức năng đầy đủ
- Cần cấu hình Google Drive API để upload file
- Cần cấu hình Cloud Translation API để dịch tin nhắn

## License

MIT License


