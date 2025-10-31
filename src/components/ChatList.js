import React, { useState, useEffect } from 'react';
import '../styles/ChatList.css';

function ChatList({ selectedChat, onSelectChat, searchQuery }) {
  // Mock data - sẽ thay thế bằng dữ liệu từ Firestore
  const [chats] = useState([
    {
      id: 'chat1',
      type: 'direct',
      name: 'Nguyễn Hoàng',
      lastMessage: 'Dự án của bạn tiến triển thế nào rồi?',
      timestamp: '10:32 AM',
      avatar: 'NH',
      status: 'online',
      unread: 0
    },
    {
      id: 'chat2',
      type: 'direct',
      name: 'Phạm Thảo',
      lastMessage: 'Hẹn gặp lại nhé!',
      timestamp: 'Hôm qua',
      avatar: 'PT',
      status: 'busy',
      unread: 0
    },
    {
      id: 'chat3',
      type: 'group',
      name: 'Nhóm Dự Án',
      lastMessage: 'Mai họp lúc 9h nhé',
      timestamp: 'Hôm qua',
      avatar: '👥',
      unread: 2
    },
    {
      id: 'chat4',
      type: 'direct',
      name: 'Lê Minh',
      lastMessage: 'OK bạn!',
      timestamp: '2 ngày trước',
      avatar: 'LM',
      status: 'hidden',
      unread: 0
    }
  ]);

  const [filteredChats, setFilteredChats] = useState(chats);

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
      {filteredChats.map((chat) => (
        <div
          key={chat.id}
          className={`chat-item ${selectedChat?.id === chat.id ? 'selected' : ''}`}
          onClick={() => onSelectChat(chat)}
        >
          <div className="chat-avatar">
            <div className={`avatar ${chat.type === 'group' ? 'group' : ''}`}>
              {chat.avatar}
            </div>
            {chat.type === 'direct' && chat.status && chat.status !== 'hidden' && (
              <span className={`status-indicator ${chat.status === 'online' ? 'online' : chat.status === 'busy' ? 'busy' : 'offline'}`}></span>
            )}
          </div>
          <div className="chat-info">
            <div className="chat-header">
              <h3 className="chat-name">{chat.name}</h3>
              <span className="chat-time">{chat.timestamp}</span>
            </div>
            <div className="chat-preview">
              <p className="last-message">{chat.lastMessage}</p>
              {chat.unread > 0 && (
                <span className="unread-badge">{chat.unread}</span>
              )}
            </div>
          </div>
        </div>
      ))}
      {filteredChats.length === 0 && (
        <div className="empty-state">Không tìm thấy cuộc trò chuyện</div>
      )}
    </div>
  );
}

export default ChatList;


