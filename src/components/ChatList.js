import React, { useState, useEffect } from 'react';
import '../styles/ChatList.css';
import { apiCall, formatTimestamp } from '../utils/api';

function ChatList({ selectedChat, onSelectChat, searchQuery, currentUser }) {
  const [chats, setChats] = useState([]);
  const [filteredChats, setFilteredChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Helper function to generate avatar initials
  const generateAvatar = (name) => {
    if (!name) return '?';
    const words = name.trim().split(' ');
    if (words.length === 1) {
      return name.substring(0, 2).toUpperCase();
    }
    return (words[0][0] + words[words.length - 1][0]).toUpperCase();
  };

  // Load chat list from backend
  useEffect(() => {
    const loadChatList = async () => {
      if (!currentUser || !currentUser.username) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await apiCall('load_chat_list', []);
        
        if (response.status === 'success' && response.output) {
          // Format timestamps and process chat list
          const formattedChats = response.output.map(chat => ({
            ...chat,
            timestamp: formatTimestamp(chat.timestamp),
            // Generate avatar initials from name
            avatar: generateAvatar(chat.name)
          }));
          setChats(formattedChats);
          setError(null);
        } else {
          setError('Không thể tải danh sách chat');
          setChats([]);
        }
      } catch (err) {
        console.error('Error loading chat list:', err);
        setError('Lỗi kết nối đến server');
        setChats([]);
      } finally {
        setLoading(false);
      }
    };

    loadChatList();
  }, [currentUser]);

  // Filter chats based on search query
  useEffect(() => {
    if (searchQuery) {
      setFilteredChats(
        chats.filter(chat =>
          chat.name.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredChats(chats);
    }
  }, [searchQuery, chats]);

  return (
    <div className="chat-list">
      {loading && (
        <div className="empty-state">Đang tải...</div>
      )}
      {error && (
        <div className="empty-state error">{error}</div>
      )}
      {!loading && !error && filteredChats.map((chat) => (
        <div
          key={chat.id}
          className={`chat-item ${selectedChat?.id === chat.id ? 'selected' : ''}`}
          onClick={() => onSelectChat(chat)}
        >
          <div className="chat-avatar">
            <div className={`avatar ${chat.type === 'group' ? 'group' : ''}`}>
              {chat.avatar}
            </div>
            {chat.type === 'direct' && chat.status && chat.status !== 'hidden' && chat.status !== 'group' && (
              <span className={`status-indicator ${chat.status === 'online' ? 'online' : chat.status === 'busy' ? 'busy' : 'offline'}`}></span>
            )}
          </div>
          <div className="chat-info">
            <div className="chat-header">
              <h3 className="chat-name">{chat.name}</h3>
              <span className="chat-time">{chat.timestamp}</span>
            </div>
            <div className="chat-preview">
              <p className="last-message">{chat.lastMessage || 'Chưa có tin nhắn'}</p>
              {chat.unread > 0 && (
                <span className="unread-badge">{chat.unread}</span>
              )}
            </div>
          </div>
        </div>
      ))}
      {!loading && !error && filteredChats.length === 0 && (
        <div className="empty-state">Không tìm thấy cuộc trò chuyện</div>
      )}
    </div>
  );
}

export default ChatList;


