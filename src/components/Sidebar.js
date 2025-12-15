import React, { useState } from 'react';
import ChatList from './ChatList';
import FriendList from './FriendList';
import RequestList from './RequestList';
import CreateGroupModal from './CreateGroupModal';
import '../styles/Sidebar.css';

function Sidebar({ selectedChat, onSelectChat, activeTab, onTabChange, onShowProfile, onShowFriendOrGroupProfile, currentUser }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateGroup, setShowCreateGroup] = useState(false);

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Chats</h1>
        <div className="sidebar-actions">
          <button className="icon-btn" onClick={() => setShowCreateGroup(true)} title="Tạo nhóm mới">
            <span>+</span>
          </button>
          <button className="icon-btn" onClick={() => onShowProfile && onShowProfile()} title="Tài khoản">
            <span>👤</span>
          </button>
        </div>
      </div>

      <div className="sidebar-tabs">
        <button
          className={`tab ${activeTab === 'chats' ? 'active' : ''}`}
          onClick={() => onTabChange('chats')}
        >
          Trò chuyện
        </button>
        <button
          className={`tab ${activeTab === 'friends' ? 'active' : ''}`}
          onClick={() => onTabChange('friends')}
        >
          Bạn bè
        </button>
        <button
          className={`tab ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => onTabChange('requests')}
        >
          Lời mời
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder={
            activeTab === 'chats' ? 'Tìm bạn bè, nhóm...' :
            activeTab === 'friends' ? 'Tìm bạn bè hoặc bạn mới...' :
            activeTab === 'requests' ? 'Tìm tên bạn bè, nhóm...' :
            'Tìm kiếm...'
          }
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="sidebar-content">
        {activeTab === 'chats' && (
          <ChatList
            selectedChat={selectedChat}
            onSelectChat={onSelectChat}
            searchQuery={searchQuery}
            currentUser={currentUser}
          />
        )}
        {activeTab === 'friends' && (
          <FriendList 
            searchQuery={searchQuery}
            onSelectChat={onSelectChat}
            onShowFriendOrGroupProfile={onShowFriendOrGroupProfile}
            currentUser={currentUser}
          />
        )}
        {activeTab === 'requests' && (
          <RequestList searchQuery={searchQuery} currentUser={currentUser} />
        )}
      </div>

      {showCreateGroup && (
        <CreateGroupModal 
          onClose={() => setShowCreateGroup(false)} 
          currentUser={currentUser}
        />
      )}
    </div>
  );
}

export default Sidebar;


