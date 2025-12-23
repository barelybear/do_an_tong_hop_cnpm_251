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
2. Cài key từ đường link này vào thư mục gốc:
https://u.pcloud.link/publink/show?code=XZWvmx5ZXj1N5g1cEOFAJlA9Ky8cRRnjdskk


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


