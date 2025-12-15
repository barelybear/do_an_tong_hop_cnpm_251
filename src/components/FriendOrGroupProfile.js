import React, { useState, useRef, useEffect } from 'react';
import '../styles/FriendOrGroupProfile.css';
import { apiCall } from '../utils/api';

function FriendOrGroupProfile({ chat, currentUser, onClose, onRefresh }) {
  const profileRef = useRef(null);
  const isGroup = chat?.type === 'group';
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [friendInfo, setFriendInfo] = useState(null);
  const [groupInfo, setGroupInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [availableFriends, setAvailableFriends] = useState([]);
  const [selectedFriends, setSelectedFriends] = useState([]);
  const [isBlocked, setIsBlocked] = useState(false);

  // Load friend or group info from API
  useEffect(() => {
    const loadProfileInfo = async () => {
      if (!chat) return;
      
      setLoading(true);
      try {
        if (isGroup) {
          // Load group info
          const response = await apiCall('get_group_info', [chat.name]);
          if (response.status === 'success' && response.output) {
            const groupData = response.output;
            // Get member statuses by loading friend list
            const friendListRes = currentUser?.username 
              ? await apiCall('load_friend_list', [currentUser.username])
              : { status: 'success', output: [] };
            
            const friendsMap = {};
            if (friendListRes.status === 'success' && friendListRes.output) {
              friendListRes.output.forEach(f => {
                friendsMap[f.username] = f.status || 'offline';
              });
            }

            const members = groupData.members.map((username) => ({
              id: username,
              name: username,
              avatar: username.substring(0, 2).toUpperCase(),
              status: friendsMap[username] || 'offline',
              isAdmin: groupData.admins?.includes(username) || false
            }));

            setGroupInfo({
              name: groupData.group_name || chat.name,
              avatar: chat?.avatar || '👥',
              members: members,
              admins: groupData.admins || [],
              createdDate: groupData.created_date || '',
              description: groupData.description || ''
            });
          }
        } else {
          // Load friend info
          const response = await apiCall('view_profile', [chat.name]);
          // Check if response is successful (has username field)
          if (response && response.username) {
            // Gmail được lấy trực tiếp từ database, không mã hóa
            const gmail = response.gmail || '';
            console.log('Loaded friend gmail from server (original, not encoded):', gmail);
            
            setFriendInfo({
              username: response.username || chat.name,
              gmail: gmail,  // Gmail gốc từ database, không mã hóa
              bio: response.bio || '',
              status: response.status || 'offline',  // response.status là user online status
              joinedDate: response.last_active ? new Date(response.last_active).toLocaleDateString('vi-VN') : '',
              mutualFriends: response.friends ? response.friends.length : 0
            });

            // Check if currentUser has blocked this friend
            if (currentUser?.username) {
              const currentUserProfile = await apiCall('view_profile', [currentUser.username]);
              if (currentUserProfile && currentUserProfile.blocked_users) {
                const blocked = currentUserProfile.blocked_users.includes(chat.name);
                setIsBlocked(blocked);
              }
            }
          }
        }
      } catch (error) {
        console.error('Error loading profile info:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProfileInfo();
  }, [chat, isGroup, currentUser]);

  // Load available friends for invite modal
  useEffect(() => {
    const loadFriendsForInvite = async () => {
      if (!showInviteModal || !currentUser?.username) return;
      
      try {
        const response = await apiCall('load_friend_list', [currentUser.username]);
        if (response.status === 'success' && response.output && groupInfo) {
          // Filter out friends who are already members
          const memberUsernames = groupInfo.members.map(m => m.name);
          const available = response.output
            .filter(f => !memberUsernames.includes(f.username))
            .map(f => ({
              id: f.username,
              name: f.username,
              avatar: f.username.substring(0, 2).toUpperCase(),
              status: f.status || 'offline'
            }));
          setAvailableFriends(available);
        }
      } catch (error) {
        console.error('Error loading friends for invite:', error);
      }
    };

    loadFriendsForInvite();
  }, [showInviteModal, currentUser, groupInfo]);

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

  const handleBlockUser = async () => {
    const confirmMessage = isGroup 
      ? 'Bạn có chắc chắn muốn chặn người dùng này?'
      : 'Bạn có chắc chắn muốn chặn ' + chat?.name + '?\n\n' +
        'Lưu ý: Cả hai người sẽ không thể nhắn tin cho nhau:\n' +
        '- Vẫn giữ trong danh sách bạn bè (nếu đang là bạn)\n' +
        '- Tin nhắn trước đó vẫn được giữ lại';
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      const response = await apiCall('block_user', [chat.name]);
      if (response.status === 'success') {
        alert('Đã chặn ' + chat?.name + '\n\nCả hai người sẽ không thể nhắn tin cho nhau.');
        setIsBlocked(true);
        if (onRefresh) onRefresh();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể chặn người dùng'));
      }
    } catch (error) {
      console.error('Error blocking user:', error);
      alert('Lỗi khi chặn người dùng');
    }
  };

  const handleUnblockUser = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn bỏ chặn ' + chat?.name + '?\n\nCả hai người sẽ có thể nhắn tin cho nhau trở lại.')) {
      return;
    }

    try {
      const response = await apiCall('unblock_user', [chat.name]);
      if (response.status === 'success') {
        alert('Đã bỏ chặn ' + chat?.name + '\n\nCả hai người đã có thể nhắn tin cho nhau trở lại.');
        setIsBlocked(false);
        if (onRefresh) onRefresh();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể bỏ chặn người dùng'));
      }
    } catch (error) {
      console.error('Error unblocking user:', error);
      alert('Lỗi khi bỏ chặn người dùng');
    }
  };

  const handleUnfriend = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn hủy kết bạn với ' + chat?.name + '?')) {
      return;
    }

    try {
      const response = await apiCall('remove_friend', [chat.name]);
      if (response.status === 'success') {
        alert('Đã hủy kết bạn');
        if (onRefresh) onRefresh();
        onClose();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể hủy kết bạn'));
      }
    } catch (error) {
      console.error('Error removing friend:', error);
      alert('Lỗi khi hủy kết bạn');
    }
  };

  const handleKickMember = async (memberUsername) => {
    if (!window.confirm(`Bạn có chắc chắn muốn kích ${memberUsername} ra khỏi nhóm?`)) {
      return;
    }

    try {
      const response = await apiCall('remove_member_from_group', [chat.name, memberUsername]);
      if (response.status === 'success') {
        alert('Đã kích thành viên ra khỏi nhóm');
        // Reload group info
        const groupRes = await apiCall('get_group_info', [chat.name]);
        if (groupRes.status === 'success' && groupRes.output) {
          const groupData = groupRes.output;
          const friendListRes = currentUser?.username 
            ? await apiCall('load_friend_list', [currentUser.username])
            : { status: 'success', output: [] };
          
          const friendsMap = {};
          if (friendListRes.status === 'success' && friendListRes.output) {
            friendListRes.output.forEach(f => {
              friendsMap[f.username] = f.status || 'offline';
            });
          }

          const members = groupData.members.map((username) => ({
            id: username,
            name: username,
            avatar: username.substring(0, 2).toUpperCase(),
            status: friendsMap[username] || 'offline',
            isAdmin: groupData.admins?.includes(username) || false
          }));

          setGroupInfo({
            ...groupInfo,
            members: members,
            admins: groupData.admins || []
          });
        }
        if (onRefresh) onRefresh();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể kích thành viên'));
      }
    } catch (error) {
      console.error('Error kicking member:', error);
      alert('Lỗi khi kích thành viên');
    }
  };

  const handleTransferAdmin = async (memberUsername) => {
    if (!window.confirm(`Bạn có chắc chắn muốn chuyển quyền admin cho ${memberUsername}?`)) {
      return;
    }

    try {
      const response = await apiCall('promote_member_to_admin', [chat.name, memberUsername]);
      if (response.status === 'success') {
        alert('Đã chuyển quyền admin');
        // Reload group info
        const groupRes = await apiCall('get_group_info', [chat.name]);
        if (groupRes.status === 'success' && groupRes.output) {
          const groupData = groupRes.output;
          const friendListRes = currentUser?.username 
            ? await apiCall('load_friend_list', [currentUser.username])
            : { status: 'success', output: [] };
          
          const friendsMap = {};
          if (friendListRes.status === 'success' && friendListRes.output) {
            friendListRes.output.forEach(f => {
              friendsMap[f.username] = f.status || 'offline';
            });
          }

          const members = groupData.members.map((username) => ({
            id: username,
            name: username,
            avatar: username.substring(0, 2).toUpperCase(),
            status: friendsMap[username] || 'offline',
            isAdmin: groupData.admins?.includes(username) || false
          }));

          setGroupInfo({
            ...groupInfo,
            members: members,
            admins: groupData.admins || []
          });
        }
        if (onRefresh) onRefresh();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể chuyển quyền admin'));
      }
    } catch (error) {
      console.error('Error transferring admin:', error);
      alert('Lỗi khi chuyển quyền admin');
    }
  };

  const handleInviteFriends = async () => {
    if (selectedFriends.length === 0) {
      alert('Vui lòng chọn ít nhất một bạn bè để mời');
      return;
    }

    try {
      let successCount = 0;
      let failCount = 0;

      for (const friend of selectedFriends) {
        const response = await apiCall('add_member_to_group', [chat.name, friend.name]);
        if (response.status === 'success') {
          successCount++;
        } else {
          failCount++;
        }
      }

      if (successCount > 0) {
        alert(`Đã mời ${successCount} bạn bè vào nhóm${failCount > 0 ? ` (${failCount} thất bại)` : ''}`);
        setShowInviteModal(false);
        setSelectedFriends([]);
        
        // Reload group info
        const groupRes = await apiCall('get_group_info', [chat.name]);
        if (groupRes.status === 'success' && groupRes.output) {
          const groupData = groupRes.output;
          const friendListRes = currentUser?.username 
            ? await apiCall('load_friend_list', [currentUser.username])
            : { status: 'success', output: [] };
          
          const friendsMap = {};
          if (friendListRes.status === 'success' && friendListRes.output) {
            friendListRes.output.forEach(f => {
              friendsMap[f.username] = f.status || 'offline';
            });
          }

          const members = groupData.members.map((username) => ({
            id: username,
            name: username,
            avatar: username.substring(0, 2).toUpperCase(),
            status: friendsMap[username] || 'offline',
            isAdmin: groupData.admins?.includes(username) || false
          }));

          setGroupInfo({
            ...groupInfo,
            members: members,
            admins: groupData.admins || []
          });
        }
        if (onRefresh) onRefresh();
      } else {
        alert('Không thể mời bạn bè vào nhóm');
      }
    } catch (error) {
      console.error('Error inviting friends:', error);
      alert('Lỗi khi mời bạn bè');
    }
  };

  const handleDisbandGroup = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn giải tán nhóm này? Hành động này không thể hoàn tác.')) {
      return;
    }

    try {
      const response = await apiCall('disband_group', [chat.name]);
      if (response.status === 'success') {
        alert('Đã giải tán nhóm');
        if (onRefresh) onRefresh();
        onClose();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể giải tán nhóm. Chỉ admin mới có thể giải tán nhóm.'));
      }
    } catch (error) {
      console.error('Error disbanding group:', error);
      alert('Lỗi khi giải tán nhóm');
    }
  };

  const handleLeaveGroup = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn rời nhóm này?')) {
      return;
    }

    try {
      const response = await apiCall('leave_group', [chat.name]);
      if (response.status === 'success') {
        alert('Đã rời nhóm');
        if (onRefresh) onRefresh();
        onClose();
      } else {
        alert('Lỗi: ' + (response.message || 'Không thể rời nhóm'));
      }
    } catch (error) {
      console.error('Error leaving group:', error);
      alert('Lỗi khi rời nhóm');
    }
  };

  const isCurrentUserAdmin = groupInfo?.admins?.includes(currentUser?.username) || false;

  if (loading) {
    return (
      <div className="friend-group-profile-sidebar" ref={profileRef}>
        <div className="profile-header">
          <h2>{isGroup ? 'THÔNG TIN NHÓM' : 'THÔNG TIN'}</h2>
        </div>
        <div className="profile-content">
          <div className="empty-state">Đang tải...</div>
        </div>
      </div>
    );
  }

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
          {!isGroup && friendInfo && (
            <p className="profile-status">
              {friendInfo.status === 'online' ? '🟢 Đang hoạt động' : 
               friendInfo.status === 'busy' ? '🔴 Bận' : 
               friendInfo.status === 'hidden' ? '⚫ Ẩn' :
               '⚫ Không hoạt động'}
            </p>
          )}
          {isGroup && groupInfo && (
            <p className="profile-status">{groupInfo.members?.length || 0} thành viên</p>
          )}
        </div>

        {!isGroup && friendInfo && (
          <>
            {friendInfo.bio && (
              <div className="profile-section">
                <h4 className="section-title">GIỚI THIỆU</h4>
                <p className="group-description">{friendInfo.bio}</p>
              </div>
            )}

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

              <div className="profile-item clickable" onClick={isBlocked ? handleUnblockUser : handleBlockUser}>
                <span className="item-icon">{isBlocked ? '✅' : '🚫'}</span>
                <div className="item-content">
                  <span className="item-label">{isBlocked ? 'Bỏ chặn đối phương' : 'Chặn đối phương'}</span>
                </div>
                <span className="item-arrow">›</span>
              </div>

              <div className="profile-item clickable" onClick={handleUnfriend}>
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
            {groupInfo.description && (
              <div className="profile-section">
                <h4 className="section-title">MÔ TẢ NHÓM</h4>
                <p className="group-description">{groupInfo.description}</p>
              </div>
            )}

            <div className="profile-section">
              <div className="section-header">
                <h4 className="section-title">THÀNH VIÊN ({groupInfo.members?.length || 0})</h4>
                {isCurrentUserAdmin && (
                  <button 
                    className="invite-btn"
                    onClick={() => setShowInviteModal(true)}
                    style={{ 
                      padding: '4px 12px', 
                      fontSize: '12px', 
                      background: '#007bff', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    + Mời
                  </button>
                )}
              </div>
              <div className="members-list">
                {groupInfo.members?.map((member) => (
                  <div key={member.id} className="member-item" style={{ position: 'relative' }}>
                    <div className="member-avatar">
                      <div className="avatar small">{member.avatar}</div>
                      {member.status === 'online' && (
                        <span className="status-indicator online"></span>
                      )}
                    </div>
                    <div className="member-info">
                      <span className="member-name">
                        {member.name}
                        {member.isAdmin && (
                          <span style={{ marginLeft: '8px', color: '#ff9800', fontSize: '12px' }}>👑 Admin</span>
                        )}
                      </span>
                      {member.status === 'online' && (
                        <span className="member-status">Đang hoạt động</span>
                      )}
                    </div>
                    {isCurrentUserAdmin && member.name !== currentUser?.username && (
                      <div className="member-actions" style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
                        {!member.isAdmin && (
                          <button
                            onClick={() => handleTransferAdmin(member.name)}
                            style={{
                              padding: '4px 8px',
                              fontSize: '11px',
                              background: '#ff9800',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                            title="Chuyển quyền admin"
                          >
                            👑
                          </button>
                        )}
                        <button
                          onClick={() => handleKickMember(member.name)}
                          style={{
                            padding: '4px 8px',
                            fontSize: '11px',
                            background: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                          title="Kích ra khỏi nhóm"
                        >
                          🚪
                        </button>
                      </div>
                    )}
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
                {isCurrentUserAdmin && (
                  <button className="action-btn danger" onClick={handleDisbandGroup}>
                    <span>💥</span>
                    <span>Giải tán nhóm</span>
                  </button>
                )}
                <button className="action-btn danger" onClick={handleLeaveGroup}>
                  <span>🚪</span>
                  <span>Rời nhóm</span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Invite Friends Modal */}
      {showInviteModal && (
        <div className="modal-overlay" onClick={() => setShowInviteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Mời bạn bè vào nhóm</h3>
              <button className="modal-close" onClick={() => setShowInviteModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {availableFriends.length === 0 ? (
                <p>Tất cả bạn bè đã là thành viên của nhóm</p>
              ) : (
                <>
                  <div className="friends-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {availableFriends.map((friend) => (
                      <div
                        key={friend.id}
                        className="friend-item"
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '8px',
                          cursor: 'pointer',
                          backgroundColor: selectedFriends.some(f => f.id === friend.id) ? '#e3f2fd' : 'transparent',
                          borderRadius: '4px',
                          marginBottom: '4px'
                        }}
                        onClick={() => {
                          const isSelected = selectedFriends.some(f => f.id === friend.id);
                          if (isSelected) {
                            setSelectedFriends(selectedFriends.filter(f => f.id !== friend.id));
                          } else {
                            setSelectedFriends([...selectedFriends, friend]);
                          }
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={selectedFriends.some(f => f.id === friend.id)}
                          onChange={() => {}}
                          style={{ marginRight: '8px' }}
                        />
                        <div className="avatar small" style={{ marginRight: '8px' }}>{friend.avatar}</div>
                        <span>{friend.name}</span>
                      </div>
                    ))}
                  </div>
                  <div className="modal-footer" style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                    <button onClick={() => { setShowInviteModal(false); setSelectedFriends([]); }}>Hủy</button>
                    <button onClick={handleInviteFriends} style={{ background: '#007bff', color: 'white' }}>
                      Mời ({selectedFriends.length})
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FriendOrGroupProfile;
