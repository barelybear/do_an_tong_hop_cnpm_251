import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import UserProfile from '../components/UserProfile';
import FriendOrGroupProfile from '../components/FriendOrGroupProfile';
import '../styles/MainPage.css';

function MainPage({ currentUser, onLogout }) {
  const [selectedChat, setSelectedChat] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [showFriendOrGroupProfile, setShowFriendOrGroupProfile] = useState(false);
  const [profileChat, setProfileChat] = useState(null);
  const [activeTab, setActiveTab] = useState('chats'); // 'chats', 'friends', 'requests'
  const [userLanguage, setUserLanguage] = useState(() => {
    return localStorage.getItem('userLanguage') || 'vi';
  });

  // Listen for language changes from UserProfile
  useEffect(() => {
    const handleLanguageChange = () => {
      setUserLanguage(localStorage.getItem('userLanguage') || 'vi');
    };
    window.addEventListener('storage', handleLanguageChange);
    // Check periodically (in case same window)
    const interval = setInterval(() => {
      const lang = localStorage.getItem('userLanguage') || 'vi';
      if (lang !== userLanguage) {
        setUserLanguage(lang);
      }
    }, 500);
    return () => {
      window.removeEventListener('storage', handleLanguageChange);
      clearInterval(interval);
    };
  }, [userLanguage]);

  return (
    <div className="main-page">
      <Sidebar
        selectedChat={selectedChat}
        onSelectChat={setSelectedChat}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onShowProfile={() => setShowProfile(true)}
        onShowFriendOrGroupProfile={(chat) => {
          setProfileChat(chat);
          setShowFriendOrGroupProfile(true);
        }}
      />
      
      <div className="main-content">
        <ChatWindow
          selectedChat={selectedChat}
          userLanguage={userLanguage}
          onShowFriendOrGroupProfile={(chat) => {
            setProfileChat(chat);
            setShowFriendOrGroupProfile(true);
          }}
        />
      </div>

      {showProfile && (
        <>
          <div className="profile-overlay" onClick={() => setShowProfile(false)}></div>
          <UserProfile
            currentUser={currentUser}
            onClose={() => setShowProfile(false)}
            onLogout={onLogout}
          />
        </>
      )}

      {showFriendOrGroupProfile && profileChat && (
        <>
          <div className="profile-overlay" onClick={() => setShowFriendOrGroupProfile(false)}></div>
          <FriendOrGroupProfile
            chat={profileChat}
            currentUser={currentUser}
            onClose={() => setShowFriendOrGroupProfile(false)}
          />
        </>
      )}
    </div>
  );
}

export default MainPage;

