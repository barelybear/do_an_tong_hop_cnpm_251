import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatWindow.css';
import { apiCall, formatTimestamp } from '../utils/api';
import { io } from 'socket.io-client';

// Tạo một kết nối Socket.IO dùng chung cho toàn bộ file
const socket = io('http://127.0.0.1:5000', {
  autoConnect: false,
});

function ChatWindow({ selectedChat, onShowFriendOrGroupProfile, userLanguage = 'vi', currentUser }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [translatedMessages, setTranslatedMessages] = useState({});
  // Cần thêm marker cho biết đây là group hay là user
  // Tam thoi chua ap dung cho group
  // Hàm load tin nhắn (dùng lại cho initial load + realtime qua socket)
  const loadMessages = async () => {
    if (!selectedChat) {
      setMessages([]);
      return;
    }

    try {
      const response = await apiCall('load_message_user', [selectedChat.name]);
      console.log('Load messages response:', response); // Debug log
      
      if (response && response.status === 'success' && response.output) {
        const result = response.output;
        if (Array.isArray(result)) {
          setMessages(result);
        } else if (result && typeof result === 'object') {
          setMessages([result]);
        } else {
          setMessages([]);
        }
      } else {
        console.error('Failed to load messages:', response);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      setMessages([]);
    }
  };

  // Initial load khi đổi selectedChat
  useEffect(() => {
    loadMessages();
  }, [selectedChat]);

  // Lắng nghe Socket.IO để nhận tin nhắn realtime
  useEffect(() => {
    if (!selectedChat || !currentUser || !currentUser.username) return;

    if (!socket.connected) {
      socket.connect();
    }

    const isGroup = selectedChat.type === 'group';
    let room;
    if (isGroup) {
      room = selectedChat.name;
    } else {
      const users = [currentUser.username, selectedChat.name].sort();
      room = `${users[0]}_${users[1]}`;
    }

    // Join room tương ứng với cuộc chat đang mở
    socket.emit('join', { room });

    const handleNewMessage = (data) => {
      if (!data || data.room !== room) return;
      // Khi có tin mới trong room này thì reload lại messages
      loadMessages();
    };

    socket.on('new_message', handleNewMessage);

    return () => {
      socket.off('new_message', handleNewMessage);
      socket.emit('leave', { room });
    };
  }, [selectedChat, currentUser]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (message.trim() && selectedChat) {
      const messageContent = message.trim();
      const currentMessages = messages; // Save current messages
      setMessage(''); // Clear input immediately for better UX
      
      // Optimistically add message to UI
      const tempMessage = {
        id: `temp-${Date.now()}`,
        sender: 'Me',
        senderId: 'me',
        content: messageContent,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        isFile: false
      };
      setMessages([...currentMessages, tempMessage]);
      
      try {
        // Send message to backend
        const res = await apiCall("send_message_user", [selectedChat.name, messageContent]);
        console.log('Send message response:', res); // Debug log
        
        if (res && res.status === 'success') {
          // Sau khi backend xử lý xong, Socket.IO sẽ bắn sự kiện new_message
          // nên ở đây chỉ cần sync lại nếu muốn chắc chắn
          const response = await apiCall('load_message_user', [selectedChat.name]);
          if (response && response.status === 'success' && response.output) {
            setMessages(response.output);
          }
        } else {
          // If send failed, remove the optimistic message
          setMessages(currentMessages);
          setMessage(messageContent); // Restore message
          console.error('Failed to send message:', res);
        }
      } catch (error) {
        console.error('Error sending message:', error);
        // Remove optimistic message on error
        setMessages(currentMessages);
        setMessage(messageContent); // Restore message
      }
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Kiểm tra kích thước file
      if (file.size > 4 * 1024 * 1024) {
        alert('File gửi đi không được quá 4MB');
        return;
      }
      // Mock upload file
      const newMessage = {
        id: messages.length + 1,
        sender: 'Me',
        senderId: 'me',
        content: file.name,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        isFile: true
      };
      setMessages([...messages, newMessage]);
    }
  };

  // Handle click vào message content để hiện option dịch
  const handleMessageClick = (e, msg) => {
    e.preventDefault();
    e.stopPropagation();
    if (msg.isFile) return; // Không dịch file
    
    setSelectedMessage(msg);
    setContextMenu({
      x: e.clientX,
      y: e.clientY
    });
  };

  // Đóng context menu
  useEffect(() => {
    const handleClick = () => {
      setContextMenu(null);
    };
    if (contextMenu) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [contextMenu]);

  // Function dịch tin nhắn
  const translateMessage = async (msg) => {
    if (translatedMessages[msg.id]) {
      // Nếu đã dịch, hiển thị lại bản gốc
      const newTranslated = { ...translatedMessages };
      delete newTranslated[msg.id];
      setTranslatedMessages(newTranslated);
      setContextMenu(null);
      return;
    }

    try {
      // Gọi API backend để dịch
      const data = await apiCall('translate_message', [msg.content, userLanguage]);
      
      if (data.status === 'success' && data.output) {
        setTranslatedMessages({
          ...translatedMessages,
          [msg.id]: data.output
        });
      } else if (data.output) {
        // If API returns original message (error case), use it
        setTranslatedMessages({
          ...translatedMessages,
          [msg.id]: data.output
        });
      } else {
        // If translation fails completely, keep original message
        console.error('Translation failed, keeping original message');
      }
    } catch (error) {
      console.error('Translation error:', error);
      // On error, keep original message (don't use mock data)
    }
    
    setContextMenu(null);
  };

  if (!selectedChat) {
    return (
      <div className="chat-window empty">
        <div className="empty-state">
          <h2>Chào mừng đến với Chat Desktop</h2>
          <p>Chọn một cuộc trò chuyện để bắt đầu</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="header-left">
          <div className="chat-avatar">
            <div className="avatar">{selectedChat.avatar}</div>
            {selectedChat.status && selectedChat.status !== 'hidden' && (
              <span className={`status-indicator ${selectedChat.status === 'online' ? 'online' : selectedChat.status === 'busy' ? 'busy' : 'offline'}`}></span>
            )}
          </div>
          <div className="chat-info">
            <h2 className="chat-name">{selectedChat.name}</h2>
            {selectedChat.status && selectedChat.status !== 'hidden' && (
              <p className="chat-status">
                {selectedChat.status === 'online' ? '🟢 Online' : 
                 selectedChat.status === 'busy' ? '🔴 Bận' : 
                 '⚫ Offline'}
              </p>
            )}
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-btn" title="Gọi thoại">📞</button>
          <button className="icon-btn" title="Gọi video">📹</button>
          <button 
            className="icon-btn" 
            onClick={() => selectedChat && onShowFriendOrGroupProfile && onShowFriendOrGroupProfile(selectedChat)} 
            title="Thông tin"
          >
            ⋮
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${msg.senderId === 'me' ? 'sent' : 'received'}`}
          >
            {msg.senderId !== 'me' && (
              <div className="message-avatar">
                <div className="avatar small">{selectedChat.avatar}</div>
              </div>
            )}
            <div className="message-content">
              <div 
                className="message-bubble"
                onClick={(e) => handleMessageClick(e, msg)}
                style={{ cursor: msg.isFile ? 'default' : 'pointer' }}
              >
                {msg.isFile ? (
                  <div className="file-message">
                    <span>📎 {msg.content}</span>
                  </div>
                ) : (
                  <p>{translatedMessages[msg.id] || msg.content}</p>
                )}
              </div>
              <span className="message-time">{msg.timestamp}</span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Context Menu */}
      {contextMenu && selectedMessage && !selectedMessage.isFile && (
        <div 
          className="context-menu"
          style={{
            position: 'fixed',
            left: `${contextMenu.x}px`,
            top: `${contextMenu.y}px`,
            zIndex: 1000,
            backgroundColor: 'white',
            border: '1px solid #ddd',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            padding: '4px 0',
            minWidth: '120px'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div 
            className="context-menu-item"
            onClick={() => translateMessage(selectedMessage)}
            style={{
              padding: '8px 16px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f0f0'}
            onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
          >
            {translatedMessages[selectedMessage.id] ? '📖 Hiển thị bản gốc' : '🌐 Dịch'}
          </div>
        </div>
      )}

      <form className="message-input-container" onSubmit={handleSend}>
        <button type="button" className="emoji-btn" title="Emoji">😊</button>
        <label className="attach-btn" title="Đính kèm">
          📎
          <input
            type="file"
            accept="image/*,video/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </label>
        <input
          type="text"
          className="message-input"
          placeholder="Nhập tin nhắn..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button type="submit" className="send-btn" disabled={!message.trim()}>
          ➤
        </button>
      </form>
    </div>
  );
}

export default ChatWindow;
