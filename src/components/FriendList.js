import React, { useState, useEffect } from 'react';
import '../styles/FriendList.css';

function FriendList({ searchQuery }) {
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
      status: 'offline',
      gmail: 'phamthao@gmail.com'
    },
    {
      id: 'user3',
      username: 'Lê Minh',
      avatar: 'LM',
      status: 'offline',
      gmail: 'leminh@gmail.com'
    }
  ]);

  const [filteredFriends, setFilteredFriends] = useState(friends);

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

  return (
    <div className="friend-list">
      {filteredFriends.map((friend) => (
        <div key={friend.id} className="friend-item">
          <div className="friend-avatar">
            <div className="avatar">{friend.avatar}</div>
            <span className={`status-indicator ${friend.status}`}></span>
          </div>
          <div className="friend-info">
            <h3 className="friend-name">{friend.username}</h3>
            <p className="friend-status">
              {friend.status === 'online' ? 'Online' : 'Offline'}
            </p>
          </div>
          <div className="friend-actions">
            <button className="btn-icon" title="Nhắn tin">💬</button>
            <button className="btn-icon" title="Xem profile">👤</button>
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

