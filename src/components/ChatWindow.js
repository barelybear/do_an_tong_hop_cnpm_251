import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatWindow.css';
import callPython from '../callApiPython';

function ChatWindow({ selectedChat, currentUser, onShowProfile }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Mock messages khi chọn chat
    if (selectedChat) {
      setMessages([callPython("load_message_user", currentUser.name, selectedChat.name)]);
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
        isFile: true,
        fileType: file.type.startsWith('image/') ? 'image' : 'video'
      };
      setMessages([...messages, newMessage]);
    }
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
            {selectedChat.status === 'online' && (
              <span className="status-indicator online"></span>
            )}
          </div>
          <div className="chat-info">
            <h2 className="chat-name">{selectedChat.name}</h2>
            {selectedChat.status && (
              <p className="chat-status">{selectedChat.status === 'online' ? 'Online' : 'Offline'}</p>
            )}
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-btn" title="Gọi thoại">📞</button>
          <button className="icon-btn" title="Gọi video">📹</button>
          <button className="icon-btn" onClick={onShowProfile} title="Thông tin">⋮</button>
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
              <div className="message-bubble">
                {msg.isFile ? (
                  <div className="file-message">
                    <span>📎 {msg.content}</span>
                  </div>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>
              <span className="message-time">{msg.timestamp}</span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

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

