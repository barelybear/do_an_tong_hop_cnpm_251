# Chat Desktop Application

Ứng dụng chat desktop được xây dựng với ElectronJS và React.

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

\`\`\`bash
npm install
\`\`\`

### Chạy ứng dụng

1. Build React app:
\`\`\`bash
npm run dev
\`\`\`

2. Trong terminal khác, chạy Electron:
\`\`\`bash
npm start
\`\`\`

### Build production

\`\`\`bash
npm run build
npm start
\`\`\`

## Cấu trúc thư mục

\`\`\`
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
\`\`\`

## Công nghệ sử dụng

- **ElectronJS**: Framework để xây dựng ứng dụng desktop
- **React**: Thư viện UI
- **Webpack**: Module bundler
- **Babel**: JavaScript compiler
- **Firebase Firestore**: Database (cần cấu hình)
- **Google Drive API**: Lưu trữ file đa phương tiện (cần cấu hình)
- **Cloud Translation API**: Dịch tin nhắn (cần cấu hình)

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

MIT

