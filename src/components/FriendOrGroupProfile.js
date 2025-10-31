import React, { useState, useRef, useEffect } from 'react';
import '../styles/FriendOrGroupProfile.css';

function FriendOrGroupProfile({ chat, currentUser, onClose }) {
  const profileRef = useRef(null);
  const isGroup = chat?.type === 'group';
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  // Mock data - sẽ thay thế bằng dữ liệu từ Firestore
  const friendInfo = isGroup ? null : {
    username: chat?.name || 'Người dùng',
    gmail: 'friend@example.com',
    bio: 'Luôn sẵn sàng chat 😊',
    joinedDate: '2024-01-15',
    mutualFriends: 12
  };

  const groupInfo = isGroup ? {
    name: chat?.name || 'Nhóm',
    avatar: chat?.avatar || '👥',
    members: [
      { id: '1', name: 'Nguyễn Hoàng', avatar: 'NH', status: 'online' },
      { id: '2', name: 'Phạm Thảo', avatar: 'PT', status: 'offline' },
      { id: '3', name: 'Lê Minh', avatar: 'LM', status: 'online' },
      { id: '4', name: currentUser?.username || 'Me', avatar: currentUser?.username?.substring(0, 2).toUpperCase() || 'ME', status: 'online' }
    ],
    createdDate: '2024-01-10',
    description: 'Nhóm làm việc chung về dự án'
  } : null;

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  return (
    <div className="friend-group-profile-sidebar" ref={profileRef}>
      <div className="profile-header">
        <h2>{isGroup ? 'THÔNG TIN NHÓM' : 'THÔNG TIN'}</h2>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <div className="profile-avatar-large">
            <div className={`avatar-circle ${isGroup ? 'group' : ''}`}>
              {chat?.avatar || (isGroup ? '👥' : chat?.name?.substring(0, 2).toUpperCase() || 'U')}
            </div>
          </div>
          <h3 className="profile-name">{chat?.name || 'Không xác định'}</h3>
          {!isGroup && chat?.status && chat?.status !== 'hidden' && (
            <p className="profile-status">
              {chat.status === 'online' ? '🟢 Đang hoạt động' : 
               chat.status === 'busy' ? '🔴 Bận' : 
               '⚫ Không hoạt động'}
            </p>
          )}
          {!isGroup && chat?.status === 'hidden' && (
            <p className="profile-status" style={{ color: 'transparent' }}>Ẩn</p>
          )}
          {isGroup && groupInfo && (
            <p className="profile-status">{groupInfo.members.length} thành viên</p>
          )}
        </div>

        {!isGroup && friendInfo && (
          <>
            <div className="profile-section">
              <h4 className="section-title">THÔNG TIN CÁ NHÂN</h4>
              
              <div className="profile-item">
                <span className="item-icon">📧</span>
                <div className="item-content">
                  <span className="item-label">Gmail</span>
                  <span className="item-value">{friendInfo.gmail}</span>
                </div>
              </div>

              <div className="profile-item">
                <span className="item-icon">👥</span>
                <div className="item-content">
                  <span className="item-label">Bạn chung</span>
                  <span className="item-value">{friendInfo.mutualFriends} bạn</span>
                </div>
              </div>

              <div className="profile-item">
                <span className="item-icon">📅</span>
                <div className="item-content">
                  <span className="item-label">Ngày kết bạn</span>
                  <span className="item-value">{friendInfo.joinedDate}</span>
                </div>
              </div>
            </div>

            <div className="profile-section">
              <h4 className="section-title">CÀI ĐẶT</h4>
              
              <div className="profile-item clickable">
                <span className="item-icon">🔔</span>
                <div className="item-content">
                  <span className="item-label">Thông báo</span>
                </div>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={notificationsEnabled} 
                    onChange={(e) => setNotificationsEnabled(e.target.checked)} 
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>

              <div className="profile-item clickable" onClick={() => {
                if (window.confirm('Bạn có chắc chắn muốn chặn người dùng này?')) {
                  alert('Đã chặn ' + chat?.name);
                  // TODO: Implement block functionality
                }
              }}>
                <span className="item-icon">🚫</span>
                <div className="item-content">
                  <span className="item-label">Chặn đối phương</span>
                </div>
                <span className="item-arrow">›</span>
              </div>

              <div className="profile-item clickable" onClick={() => {
                if (window.confirm('Bạn có chắc chắn muốn hủy kết bạn với ' + chat?.name + '?')) {
                  alert('Đã hủy kết bạn');
                  // TODO: Implement unfriend functionality
                }
              }}>
                <span className="item-icon">🗑️</span>
                <div className="item-content">
                  <span className="item-label">Hủy kết bạn</span>
                </div>
                <span className="item-arrow">›</span>
              </div>
            </div>
          </>
        )}

        {isGroup && groupInfo && (
          <>
            <div className="profile-section">
              <h4 className="section-title">MÔ TẢ NHÓM</h4>
              <p className="group-description">{groupInfo.description}</p>
            </div>

            <div className="profile-section">
              <div className="section-header">
                <h4 className="section-title">THÀNH VIÊN ({groupInfo.members.length})</h4>
              </div>
              <div className="members-list">
                {groupInfo.members.map((member) => (
                  <div key={member.id} className="member-item">
                    <div className="member-avatar">
                      <div className="avatar small">{member.avatar}</div>
                      {member.status === 'online' && (
                        <span className="status-indicator online"></span>
                      )}
                    </div>
                    <div className="member-info">
                      <span className="member-name">{member.name}</span>
                      {member.status === 'online' && (
                        <span className="member-status">Đang hoạt động</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="profile-section">
              <h4 className="section-title">CÀI ĐẶT</h4>
              
              <div className="profile-item clickable">
                <span className="item-icon">🔔</span>
                <div className="item-content">
                  <span className="item-label">Thông báo</span>
                </div>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={notificationsEnabled} 
                    onChange={(e) => setNotificationsEnabled(e.target.checked)} 
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>

            <div className="profile-section">
              <div className="action-buttons">
                <button className="action-btn danger">
                  <span>🚪</span>
                  <span>Rời nhóm</span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default FriendOrGroupProfile;

