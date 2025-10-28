import React, { useState } from 'react';
import '../styles/UserProfile.css';

function UserProfile({ currentUser, onClose, onLogout }) {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    username: currentUser.username,
    gmail: currentUser.gmail,
    bio: 'Always available 🚀'
  });

  const handleSave = () => {
    // Mock save profile
    alert('Cập nhật thành công!');
    setIsEditing(false);
  };

  const handleLogoutClick = () => {
    if (window.confirm('Bạn có chắc chắn muốn đăng xuất?')) {
      onLogout();
    }
  };

  return (
    <div className="user-profile-sidebar">
      <div className="profile-header">
        <button className="close-btn" onClick={onClose}>✕</button>
        <h2>ME</h2>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <div className="profile-avatar-large">
            <div className="avatar-circle">
              {currentUser.username.substring(0, 2).toUpperCase()}
            </div>
          </div>
          <h3 className="profile-name">Tài khoản của tôi</h3>
          <p className="profile-status">{profile.bio}</p>
        </div>

        <div className="profile-section">
          <h4 className="section-title">THÔNG TIN CÁ NHÂN</h4>
          
          <div className="profile-item">
            <span className="item-icon">✏️</span>
            <div className="item-content">
              <span className="item-label">Chỉnh sửa hồ sơ</span>
            </div>
            <span className="item-arrow">›</span>
          </div>

          <div className="profile-item">
            <span className="item-icon">📧</span>
            <div className="item-content">
              <span className="item-label">Gmail</span>
              <span className="item-value">{profile.gmail}</span>
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
            <span className="item-arrow">›</span>
          </div>

          <div className="profile-item clickable">
            <span className="item-icon">🔒</span>
            <div className="item-content">
              <span className="item-label">Quyền riêng tư</span>
            </div>
            <span className="item-arrow">›</span>
          </div>

          <div className="profile-item clickable">
            <span className="item-icon">🌙</span>
            <div className="item-content">
              <span className="item-label">Chế độ tối</span>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div className="profile-section">
          <button className="logout-btn" onClick={handleLogoutClick}>
            <span className="item-icon">🚪</span>
            <span>Đăng xuất</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default UserProfile;

