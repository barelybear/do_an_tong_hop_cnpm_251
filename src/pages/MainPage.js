import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import UserProfile from '../components/UserProfile';
import '../styles/MainPage.css';

function MainPage({ currentUser, onLogout }) {
  const [selectedChat, setSelectedChat] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [activeTab, setActiveTab] = useState('chats'); // 'chats', 'friends', 'requests'

  return (
    <div className="main-page">
      <Sidebar
        currentUser={currentUser}
        selectedChat={selectedChat}
        onSelectChat={setSelectedChat}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      <div className="main-content">
        <ChatWindow
          selectedChat={selectedChat}
          currentUser={currentUser}
          onShowProfile={() => setShowProfile(true)}
        />
      </div>

      {showProfile && (
        <UserProfile
          currentUser={currentUser}
          onClose={() => setShowProfile(false)}
          onLogout={onLogout}
        />
      )}
    </div>
  );
}

export default MainPage;

