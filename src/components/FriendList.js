import React, { useState, useEffect, useRef } from 'react';
import '../styles/FriendList.css';
import { apiCall } from '../utils/api';

function FriendList({ searchQuery, onSelectChat, onShowFriendOrGroupProfile, currentUser }) {
  const [friends, setFriends] = useState([]);
  const [filteredFriends, setFilteredFriends] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [openDropdownId, setOpenDropdownId] = useState(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState({});
  const dropdownRefs = useRef({});

  // ============================
  // 🔥 1. Load Friend List (NEW)
  // ============================
  useEffect(() => {
    const loadFriendList = async () => {
      if (!currentUser || !currentUser.username) return;

      try {
        const res = await apiCall("load_friend_list", [currentUser.username]);
        if (res.status === "success" && res.output) {
          setFriends(res.output.map(f => ({
            ...f,
            avatar: f.avatar || f.username.substring(0,2).toUpperCase()
          })));
        }
      } catch (err) {
        console.error("Error loading friend list:", err);
      }
    };

    loadFriendList();
  }, [currentUser]);

  // ===============================
  // 🔥 2. Search in friends + Firebase
  // ===============================
  useEffect(() => {
    if (!searchQuery) {
      setFilteredFriends(friends);
      setSearchResults([]);
      return;
    }

    const queryLower = searchQuery.toLowerCase();

    // Local filter
    const localResults = friends.filter(friend =>
      friend.username.toLowerCase().includes(queryLower) ||
      friend.gmail.toLowerCase().includes(queryLower)
    );
    setFilteredFriends(localResults);

    // Search on Firebase
    if (!currentUser || !currentUser.username) return;

    const searchFirebase = async () => {
      try {
        const response = await apiCall("search_users", [searchQuery]);

        if (response.status === "success" && response.output) {
          const existingFriendUsernames = new Set(
            friends.map(f => f.username.toLowerCase())
          );

          // Only users NOT already in friends list
          const formatted = response.output
            .filter(user => !existingFriendUsernames.has(user.username.toLowerCase()))
            .map(user => ({
              id: user.username,
              username: user.username,
              gmail: user.gmail,
              status: user.status || "offline",
              avatar: user.avatar || user.username.substring(0,2).toUpperCase(),
              isNewUser: true
            }));

          setSearchResults(formatted);
        }
      } catch (err) {
        console.error("Error searching users:", err);
        setSearchResults([]);
      }
    };

    const timeoutId = setTimeout(searchFirebase, 300);
    return () => clearTimeout(timeoutId);

  }, [searchQuery, friends, currentUser]);

  // ===============================
  // 🔥 3. Add friend API
  // ===============================
  const handleAddFriend = async (user) => {
    try {
      const response = await apiCall("send_friend_request", [
        currentUser.username,
        user.username
      ]);

      if (response.status === "success") {
        alert(`Đã gửi lời mời kết bạn đến ${user.username}`);
      } else {
        alert("Không thể gửi lời mời");
      }

    } catch (err) {
      console.error("Add friend error:", err);
    }
  };

  // ===============================
  // (Các event handler còn lại giữ nguyên)
  // ===============================

  const handleMessageClick = (friend) => {
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
    onSelectChat?.(chat);
  };

  const toggleDropdown = (friendId, e) => {
    e.stopPropagation();
    setOpenDropdownId(openDropdownId === friendId ? null : friendId);
  };

  const handleNotificationToggle = (friendId) => {
    setNotificationsEnabled(prev => ({
      ...prev,
      [friendId]: !prev[friendId]
    }));
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
    onShowFriendOrGroupProfile?.(chat);
    setOpenDropdownId(null);
  };

  return (
    <div className="friend-list">

      {/* === EXISTING FRIENDS === */}
      {filteredFriends.map(friend => (
        <div key={friend.id} className="friend-item">
          <div className="friend-avatar">
            <div className="avatar">{friend.avatar}</div>
          </div>

          <div className="friend-info">
            <h3 className="friend-name">{friend.username}</h3>
            <p className="friend-status">
              {friend.status === 'online' ? '🟢 Online' :
               friend.status === 'busy' ? '🔴 Bận' : '⚫ Offline'}
            </p>
          </div>

          <div className="friend-actions">
            <button className="btn-icon" onClick={() => handleMessageClick(friend)}>💬</button>
          </div>
        </div>
      ))}

      {/* === SEARCH RESULTS (NEW USERS) === */}
      {searchQuery && searchResults.length > 0 && (
        <>
          <div className="search-section-title">Kết quả tìm kiếm</div>

          {searchResults.map(user => (
            <div key={user.id} className="friend-item">
              <div className="friend-avatar">
                <div className="avatar">{user.avatar}</div>
              </div>

              <div className="friend-info">
                <h3 className="friend-name">{user.username}</h3>
                <p className="friend-status">
                  {user.status === 'online' ? '🟢 Online' :
                   user.status === 'busy' ? '🔴 Bận' : '⚫ Offline'}
                </p>
              </div>

              <div className="friend-actions">
                <button
                  className="btn-icon"
                  style={{ color: 'var(--primary-color)' }}
                  onClick={() => handleAddFriend(user)}
                >
                  ➕
                </button>
              </div>
            </div>
          ))}
        </>
      )}

      {!searchQuery && friends.length === 0 && (
        <div className="empty-state">Không có bạn bè</div>
      )}

      {searchQuery && filteredFriends.length === 0 && searchResults.length === 0 && (
        <div className="empty-state">Không tìm thấy</div>
      )}
    </div>
  );
}

export default FriendList;
