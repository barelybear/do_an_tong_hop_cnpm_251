import React, { useState, useRef, useEffect } from 'react';
import '../styles/UserProfile.css';

function UserProfile({ currentUser, onClose, onLogout }) {
  const profileRef = useRef(null);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [status, setStatus] = useState(() => {
    return localStorage.getItem('userStatus') || 'online';
  });
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('userLanguage') || 'vi';
  });
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const [profile] = useState({
    username: currentUser.username,
    gmail: currentUser.gmail,
    bio: 'Always available 🚀'
  });

  const handleLogoutClick = () => {
    if (window.confirm('Bạn có chắc chắn muốn đăng xuất?')) {
      onLogout();
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        onClose();
        setShowStatusDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', isDarkMode);
  }, [isDarkMode]);

  useEffect(() => {
    localStorage.setItem('userStatus', status);
    // TODO: Update status in real-time to server/Firebase
  }, [status]);

  useEffect(() => {
    localStorage.setItem('userLanguage', language);
    // TODO: Update language to server/Firebase
  }, [language]);

  const handleDarkModeToggle = (e) => {
    setIsDarkMode(e.target.checked);
  };

  const handleStatusChange = (newStatus) => {
    setStatus(newStatus);
    setShowStatusDropdown(false);
  };

  const getStatusDisplay = () => {
    switch (status) {
      case 'online':
        return { text: '🟢 Online', color: '#4CAF50' };
      case 'busy':
        return { text: '🔴 Bận', color: '#F44336' };
      case 'hidden':
        return { text: '⚫ Ẩn', color: '#9E9E9E' };
      default:
        return { text: '🟢 Online', color: '#4CAF50' };
    }
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="user-profile-sidebar" ref={profileRef}>
      <div className="profile-header">
        <h2>ME</h2>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <div className="profile-avatar-large">
            <div className="avatar-circle">
              {currentUser.username.substring(0, 2).toUpperCase()}
            </div>
          </div>
          <h3 className="profile-name">Khải CaCa</h3>
          <p className="profile-status">{profile.bio}</p>
        </div>

        <div className="profile-section">
          <h4 className="section-title">THÔNG TIN CÁ NHÂN</h4>
          
          <div 
            className="profile-item clickable status-item" 
            onClick={(e) => {
              e.stopPropagation();
              setShowStatusDropdown(!showStatusDropdown);
            }}
          >
            <span className="item-icon">💚</span>
            <div className="item-content">
              <span className="item-label">Trạng thái hoạt động</span>
              <span className="item-value" style={{ color: statusDisplay.color }}>
                {statusDisplay.text}
              </span>
            </div>
            <span className="item-arrow">{showStatusDropdown ? '⌄' : '›'}</span>
          </div>

          {showStatusDropdown && (
            <div className="status-dropdown" onClick={(e) => e.stopPropagation()}>
              <div 
                className={`status-option ${status === 'online' ? 'active' : ''}`}
                onClick={() => handleStatusChange('online')}
              >
                <span className="status-indicator-badge" style={{ backgroundColor: '#4CAF50' }}></span>
                <span>🟢 Online</span>
              </div>
              <div 
                className={`status-option ${status === 'busy' ? 'active' : ''}`}
                onClick={() => handleStatusChange('busy')}
              >
                <span className="status-indicator-badge" style={{ backgroundColor: '#F44336' }}></span>
                <span>🔴 Bận</span>
              </div>
              <div 
                className={`status-option ${status === 'hidden' ? 'active' : ''}`}
                onClick={() => handleStatusChange('hidden')}
              >
                <span className="status-indicator-badge" style={{ backgroundColor: '#9E9E9E' }}></span>
                <span>⚫ Ẩn</span>
              </div>
            </div>
          )}
          
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
          
          <div 
            className="profile-item clickable language-item" 
            onClick={(e) => {
              e.stopPropagation();
              setShowLanguageDropdown(!showLanguageDropdown);
            }}
          >
            <span className="item-icon">🌐</span>
            <div className="item-content">
              <span className="item-label">Ngôn ngữ của bạn</span>
              <span className="item-value">
                {language === 'vi' ? '🇻🇳 Tiếng Việt' :
                 language === 'en' ? '🇬🇧 English' :
                 language === 'ja' ? '🇯🇵 日本語' :
                 language === 'ko' ? '🇰🇷 한국어' :
                 language === 'zh' ? '🇨🇳 中文' :
                 '🇻🇳 Tiếng Việt'}
              </span>
            </div>
            <span className="item-arrow">{showLanguageDropdown ? '⌄' : '›'}</span>
          </div>

          {showLanguageDropdown && (
            <div className="language-dropdown" onClick={(e) => e.stopPropagation()}>
              <div 
                className={`language-option ${language === 'vi' ? 'active' : ''}`}
                onClick={() => {
                  setLanguage('vi');
                  setShowLanguageDropdown(false);
                }}
              >
                <span>🇻🇳 Tiếng Việt</span>
              </div>
              <div 
                className={`language-option ${language === 'en' ? 'active' : ''}`}
                onClick={() => {
                  setLanguage('en');
                  setShowLanguageDropdown(false);
                }}
              >
                <span>🇬🇧 English</span>
              </div>
              <div 
                className={`language-option ${language === 'ja' ? 'active' : ''}`}
                onClick={() => {
                  setLanguage('ja');
                  setShowLanguageDropdown(false);
                }}
              >
                <span>🇯🇵 日本語</span>
              </div>
              <div 
                className={`language-option ${language === 'ko' ? 'active' : ''}`}
                onClick={() => {
                  setLanguage('ko');
                  setShowLanguageDropdown(false);
                }}
              >
                <span>🇰🇷 한국어</span>
              </div>
              <div 
                className={`language-option ${language === 'zh' ? 'active' : ''}`}
                onClick={() => {
                  setLanguage('zh');
                  setShowLanguageDropdown(false);
                }}
              >
                <span>🇨🇳 中文</span>
              </div>
            </div>
          )}
          
          <div className="profile-item clickable">
            <span className="item-icon">🔔</span>
            <div className="item-content">
              <span className="item-label">Thông báo</span>
            </div>
            <span className="item-arrow">›</span>
          </div>

          <div className="profile-item clickable">
            <span className="item-icon">🌙</span>
            <div className="item-content">
              <span className="item-label">Chế độ tối</span>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" checked={isDarkMode} onChange={handleDarkModeToggle} />
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


