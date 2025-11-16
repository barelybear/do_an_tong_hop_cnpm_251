import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatWindow.css';
import { apiCall, formatTimestamp } from '../utils/api';
function ChatWindow({ selectedChat, onShowFriendOrGroupProfile, userLanguage = 'vi', currentUser }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [translatedMessages, setTranslatedMessages] = useState({});
  // Cần thêm marker cho biết đây là group hay là user
  // Tam thoi chua ap dung cho group
  useEffect(() => {
    if (selectedChat) {
      const result = apiCall('load_message_user', [selectedChat.name]).output;
      if (Array.isArray(result)) {
        setMessages(result);
      } else if (result && typeof result === 'object') {
        setMessages([result]);
      } else {
        setMessages([]);
      }
    } else {
      setMessages([]);
    }
  }, [selectedChat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (message.trim() && selectedChat) {
      const newMessage = {
        id: messages.length + 1,
        sender: 'Me',
        senderId: 'me',
        content: message,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        isFile: false
      };
      // Cần thêm logic để xử lý gửi fail
      // Logic để gửi message, không gửi file
      const res = apiCall("send_message_user", [selectedChat.name, message])
      setMessages([...messages, newMessage]);
      setMessage('');
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
      const response = await fetch('http://127.0.0.1:5000/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          function_name: 'translate_text',
          args: [msg.content, userLanguage]
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success' && data.output) {
        setTranslatedMessages({
          ...translatedMessages,
          [msg.id]: data.output
        });
      } else {
        // Mock translation nếu API chưa sẵn sàng
        const mockTranslations = {
          'vi': {
            'en': { 'Chào bạn! Bạn có khỏe không?': 'Hello! How are you?', 'Dự án của bạn tiến triển thế nào rồi?': 'How is your project going?' },
            'ja': { 'Chào bạn! Bạn có khỏe không?': 'こんにちは！お元気ですか？', 'Dự án của bạn tiến triển thế nào rồi?': 'プロジェクトはどう進んでいますか？' },
            'ko': { 'Chào bạn! Bạn có khỏe không?': '안녕하세요! 잘 지내세요?', 'Dự án của bạn tiến triển thế nào rồi?': '프로젝트는 어떻게 진행되고 있나요?' },
            'zh': { 'Chào bạn! Bạn có khỏe không?': '你好！你好吗？', 'Dự án của bạn tiến triển thế nào rồi?': '你的项目进展如何？' }
          }
        };
        
        const translated = mockTranslations['vi']?.[userLanguage]?.[msg.content] || msg.content;
        setTranslatedMessages({
          ...translatedMessages,
          [msg.id]: translated
        });
      }
    } catch (error) {
      console.error('Translation error:', error);
      // Mock fallback
      const mockTranslations = {
        'vi': {
          'en': { 'Chào bạn! Bạn có khỏe không?': 'Hello! How are you?', 'Dự án của bạn tiến triển thế nào rồi?': 'How is your project going?' },
          'ja': { 'Chào bạn! Bạn có khỏe không?': 'こんにちは！お元気ですか？', 'Dự án của bạn tiến triển thế nào rồi?': 'プロジェクトはどう進んでいますか？' },
        }
      };
      const translated = mockTranslations['vi']?.[userLanguage]?.[msg.content] || msg.content;
      setTranslatedMessages({
        ...translatedMessages,
        [msg.id]: translated
      });
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


