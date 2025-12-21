import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatWindow.css';
import { apiCall, formatTimestamp } from '../utils/api';
import { io } from 'socket.io-client';

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
  const [videoToPlay, setVideoToPlay] = useState(null);

  // --- HÀM XỬ LÝ HIỂN THỊ TÊN FILE ---
  const getDisplayFileName = (url) => {
    if (!url) return '';
    const fileNameWithTimestamp = url.split('/').pop();
    return fileNameWithTimestamp.replace(/_\d+(?=\.[^.]+$)/, '');
  };

  const loadMessages = async () => {
    if (!selectedChat) {
      setMessages([]);
      return;
    }
    try {
      const method = selectedChat.type === 'group' ? 'load_message_group' : 'load_message_user';
      const response = await apiCall(method, [selectedChat.name]);
      if (response && response.status === 'success' && response.output) {
        setMessages(Array.isArray(response.output) ? response.output : [response.output]);
      } else {
        setMessages([]);
      }
    } catch (error) {
      setMessages([]);
    }
  };

  useEffect(() => {
    loadMessages();
  }, [selectedChat]);

  useEffect(() => {
    if (!selectedChat || !currentUser?.username) return;
    if (!socket.connected) socket.connect();
    const isGroup = selectedChat.type === 'group';
    let room = isGroup ? selectedChat.name : [currentUser.username, selectedChat.name].sort().join('_');
    socket.emit('join', { room });
    const handleNewMessage = (data) => { if (data?.room === room) loadMessages(); };
    socket.on('new_message', handleNewMessage);
    return () => {
      socket.off('new_message', handleNewMessage);
      socket.emit('leave', { room });
    };
  }, [selectedChat, currentUser]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (message.trim() && selectedChat) {
      const messageContent = message.trim();
      setMessage('');
      try {
        const method = selectedChat.type === 'group' ? "send_message_group" : "send_message_user";
        await apiCall(method, [selectedChat.name, messageContent]);
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  };

  // --- SỬA LẠI: GỌI THẲNG API KHI BẤM NÚT 📎 ---
  const handleAttachClick = async () => {
    if (!selectedChat) return;
    try {
      const method = selectedChat.type === 'group' ? 'send_file_group' : 'send_file_user';
      // Gọi API - Backend sẽ tự mở cửa sổ chọn file
      const res = await apiCall(method, [selectedChat.name]);
      if (res.status !== 'success' && res.status !== 'cancel') {
        alert('Gửi file thất bại: ' + (res.message || 'Lỗi không xác định'));
      }
    } catch (error) {
      alert('Lỗi kết nối khi gửi file');
    }
  };

  const handleContextMenu = (e, msg) => {
    e.preventDefault();
    setSelectedMessage(msg);
    setContextMenu({ x: e.clientX, y: e.clientY });
  };

  useEffect(() => {
    const closeMenu = () => setContextMenu(null);
    window.addEventListener('click', closeMenu);
    return () => window.removeEventListener('click', closeMenu);
  }, []);

  const translateMessage = async (msg) => {
    if (translatedMessages[msg.id]) {
      const newT = { ...translatedMessages };
      delete newT[msg.id];
      setTranslatedMessages(newT);
      setContextMenu(null);
      return;
    }
    const data = await apiCall('translate_message', [msg.content, userLanguage]);
    if (data.status === 'success') {
      setTranslatedMessages({ ...translatedMessages, [msg.id]: data.output });
    }
    setContextMenu(null);
  };

  if (!selectedChat) {
    return <div className="chat-window empty"><div className="empty-state"><h2>Chào mừng đến với Chat Desktop</h2><p>Chọn một cuộc trò chuyện để bắt đầu</p></div></div>;
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="header-left">
          <div className="chat-avatar"><div className="avatar">{selectedChat.avatar}</div>
            {selectedChat.status && selectedChat.status !== 'hidden' && (
              <span className={`status-indicator ${selectedChat.status === 'online' ? 'online' : 'offline'}`}></span>
            )}
          </div>
          <div className="chat-info">
            <h2 className="chat-name">{selectedChat.name}</h2>
            {selectedChat.status && selectedChat.status !== 'hidden' && (
              <p className="chat-status">{selectedChat.status === 'online' ? '🟢 Online' : '⚫ Offline'}</p>
            )}
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-btn" onClick={() => onShowFriendOrGroupProfile(selectedChat)}>⋮</button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.senderId === 'me' || msg.sender === currentUser.username ? 'sent' : 'received'}`}>
            <div className="message-content">
              <div className="message-bubble" onContextMenu={(e) => handleContextMenu(e, msg)}>
                {msg.is_media ? (
                  <div className="file-preview">
                    {msg.media_type === 'image' ? (
                      <img src={msg.content} alt="preview" className="msg-image" style={{ maxWidth: '280px', maxHeight: '200px', borderRadius: '8px', objectFit: 'contain' }} />
                    ) : msg.media_type === 'video' ? (
                      <div className="video-thumb" onClick={() => setVideoToPlay(msg.content)}>
                        <video src={msg.content} className="msg-video-preview" style={{ maxWidth: '280px' }} />
                        <div className="play-icon-overlay">▶</div>
                      </div>
                    ) : (
                      <div className="generic-file"><span>📎 {getDisplayFileName(msg.content)}</span></div>
                    )}
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

      {videoToPlay && (
        <div className="video-overlay" onClick={() => setVideoToPlay(null)}>
          <div className="video-container" onClick={e => e.stopPropagation()}>
            <video controls autoPlay className="full-video"><source src={videoToPlay} /></video>
            <button className="close-video-btn" onClick={() => setVideoToPlay(null)}>✕</button>
          </div>
        </div>
      )}

      {contextMenu && selectedMessage && (
        <div className="message-actions-frame" style={{ position: 'fixed', left: `${contextMenu.x}px`, top: `${contextMenu.y}px`, zIndex: 1000 }}>
          <div className="actions-container" style={{ background: 'white', borderRadius: '8px', border: '1px solid #ccc', padding: '5px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            {selectedMessage.is_media ? (
              <>
                <button className="action-button" onClick={() => { window.open(selectedMessage.content, '_blank'); setContextMenu(null); }} style={{ display: 'block', width: '100%', padding: '8px', border: 'none', background: 'none', textAlign: 'left', cursor: 'pointer' }}>
                  📥 Tải về
                </button>
                {selectedMessage.media_type === 'video' && (
                  <button className="action-button" onClick={() => { setVideoToPlay(selectedMessage.content); setContextMenu(null); }} style={{ display: 'block', width: '100%', padding: '8px', border: 'none', background: 'none', textAlign: 'left', cursor: 'pointer' }}>
                    ▶ Phát video
                  </button>
                )}
              </>
            ) : (
              <button className="action-button" onClick={() => translateMessage(selectedMessage)} style={{ display: 'block', width: '100%', padding: '8px', border: 'none', background: 'none', textAlign: 'left', cursor: 'pointer' }}>
                {translatedMessages[selectedMessage.id] ? '📖 Hiện văn bản gốc' : '🌐 Dịch tin nhắn'}
              </button>
            )}
          </div>
        </div>
      )}

      <form className="message-input-container" onSubmit={handleSend}>
        <button type="button" className="emoji-btn">😊</button>
        {/* SỬA LẠI THÀNH BUTTON ĐỂ GỌI API TRỰC TIẾP */}
        <button type="button" className="attach-btn" onClick={handleAttachClick} title="Gửi file">
          📎
        </button>
        <input
          type="text"
          className="message-input"
          placeholder="Nhập tin nhắn..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button type="submit" className="send-btn" disabled={!message.trim()}>➤</button>
      </form>
    </div>
  );
}

export default ChatWindow;