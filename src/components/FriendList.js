import React, { useState, useEffect, useRef } from 'react';
import '../styles/FriendList.css';

function FriendList({ searchQuery, onSelectChat, onShowFriendOrGroupProfile }) {
  // Mock data - sẽ thay thế bằng dữ liệu từ Firestore
  const [friends] = useState([
    {
      id: 'user1',
      username: 'Nguyễn Hoàng',
      avatar: 'NH',
      status: 'online',
      gmail: 'nguyenhoang@gmail.com'
    },
    {
      id: 'user2',
      username: 'Phạm Thảo',
      avatar: 'PT',
      status: 'busy',
      gmail: 'phamthao@gmail.com'
    },
    {
      id: 'user3',
      username: 'Lê Minh',
      avatar: 'LM',
      status: 'hidden',
      gmail: 'leminh@gmail.com'
    }
  ]);

  const [filteredFriends, setFilteredFriends] = useState(friends);
  const [openDropdownId, setOpenDropdownId] = useState(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState({});
  const dropdownRefs = useRef({});

  useEffect(() => {
    if (searchQuery) {
      setFilteredFriends(
        friends.filter(friend =>
          friend.username.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredFriends(friends);
    }
  }, [searchQuery, friends]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (openDropdownId && dropdownRefs.current[openDropdownId]) {
        if (!dropdownRefs.current[openDropdownId].contains(event.target)) {
          setOpenDropdownId(null);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [openDropdownId]);

  const handleMessageClick = (friend) => {
    // Tạo chat object từ friend (tương tự format trong ChatList)
    const chat = {
      id: `friend-${friend.id}`,
      type: 'direct',
      name: friend.username,
      avatar: friend.avatar,
      status: friend.status,
      gmail: friend.gmail,
      lastMessage: '',
      timestamp: '',
      unread: 0
    };
    if (onSelectChat) {
      onSelectChat(chat);
    }
  };

  const toggleDropdown = (friendId, event) => {
    event.stopPropagation();
    setOpenDropdownId(openDropdownId === friendId ? null : friendId);
  };

  const handleNotificationToggle = (friendId) => {
    setNotificationsEnabled(prev => ({
      ...prev,
      [friendId]: !prev[friendId]
    }));
  };

  const handleBlock = (friend) => {
    if (window.confirm(`Bạn có chắc chắn muốn chặn ${friend.username}?`)) {
      alert(`Đã chặn ${friend.username}`);
      setOpenDropdownId(null);
      // TODO: Implement block functionality
    }
  };

  const handleUnfriend = (friend) => {
    if (window.confirm(`Bạn có chắc chắn muốn hủy kết bạn với ${friend.username}?`)) {
      alert(`Đã hủy kết bạn với ${friend.username}`);
      setOpenDropdownId(null);
      // TODO: Implement unfriend functionality
    }
  };

  const handleViewProfile = (friend) => {
    const chat = {
      id: friend.id,
      type: 'direct',
      name: friend.username,
      avatar: friend.avatar,
      status: friend.status,
      gmail: friend.gmail
    };
    if (onShowFriendOrGroupProfile) {
      onShowFriendOrGroupProfile(chat);
    }
    setOpenDropdownId(null);
  };

  return (
    <div className="friend-list">
      {filteredFriends.map((friend) => (
        <div key={friend.id} className="friend-item">
          <div className="friend-avatar">
            <div className="avatar">{friend.avatar}</div>
            {friend.status && friend.status !== 'hidden' && (
              <span className={`status-indicator ${friend.status === 'online' ? 'online' : friend.status === 'busy' ? 'busy' : 'offline'}`}></span>
            )}
          </div>
          <div className="friend-info">
            <h3 className="friend-name">{friend.username}</h3>
            <p className="friend-status">
              {friend.status === 'online' ? '🟢 Online' : 
               friend.status === 'busy' ? '🔴 Bận' : 
               friend.status === 'hidden' ? '' : '⚫ Offline'}
            </p>
          </div>
          <div className="friend-actions">
            <button 
              className="btn-icon" 
              title="Nhắn tin"
              onClick={() => handleMessageClick(friend)}
            >
              💬
            </button>
            <div className="dropdown-container" ref={el => dropdownRefs.current[friend.id] = el}>
              <button 
                className="btn-icon" 
                title="Tùy chọn"
                onClick={(e) => toggleDropdown(friend.id, e)}
              >
                ⋮
              </button>
              {openDropdownId === friend.id && (
                <div className="dropdown-menu">
                  <div 
                    className="dropdown-item"
                    onClick={() => handleViewProfile(friend)}
                  >
                    <span className="dropdown-icon">👤</span>
                    <span>Xem profile</span>
                  </div>
                  <div 
                    className="dropdown-item"
                    onClick={() => handleNotificationToggle(friend.id)}
                  >
                    <span className="dropdown-icon">🔔</span>
                    <span>Thông báo</span>
                    <label className="toggle-switch small">
                      <input 
                        type="checkbox" 
                        checked={notificationsEnabled[friend.id] !== false}
                        onChange={() => handleNotificationToggle(friend.id)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                  <div className="dropdown-divider"></div>
                  <div 
                    className="dropdown-item danger"
                    onClick={() => handleBlock(friend)}
                  >
                    <span className="dropdown-icon">🚫</span>
                    <span>Chặn</span>
                  </div>
                  <div 
                    className="dropdown-item danger"
                    onClick={() => handleUnfriend(friend)}
                  >
                    <span className="dropdown-icon">🗑️</span>
                    <span>Hủy kết bạn</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
      {filteredFriends.length === 0 && (
        <div className="empty-state">Không tìm thấy bạn bè</div>
      )}
    </div>
  );
}

export default FriendList;


