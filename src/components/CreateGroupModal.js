import React, { useState, useEffect } from 'react';
import '../styles/CreateGroupModal.css';
import { apiCall } from '../utils/api';

function CreateGroupModal({ onClose, currentUser }) {
  const [groupName, setGroupName] = useState('');
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [friends, setFriends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  // Load friends list from API
  useEffect(() => {
    const loadFriends = async () => {
      if (!currentUser || !currentUser.username) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await apiCall('load_friend_list', [currentUser.username]);
        if (response.status === 'success' && response.output) {
          setFriends(response.output.map(f => ({
            id: f.username,
            username: f.username,
            avatar: f.avatar || f.username.substring(0, 2).toUpperCase()
          })));
        }
      } catch (error) {
        console.error('Error loading friends:', error);
      } finally {
        setLoading(false);
      }
    };

    loadFriends();
  }, [currentUser]);

  const toggleMember = (friendId) => {
    if (selectedMembers.includes(friendId)) {
      setSelectedMembers(selectedMembers.filter(id => id !== friendId));
    } else {
      setSelectedMembers([...selectedMembers, friendId]);
    }
  };

  const handleCreate = async () => {
    if (!groupName.trim()) {
      alert('Vui lòng nhập tên nhóm');
      return;
    }
    if (selectedMembers.length === 0) {
      alert('Vui lòng chọn ít nhất một thành viên');
      return;
    }
    if (!currentUser || !currentUser.username) {
      alert('Bạn cần đăng nhập để tạo nhóm');
      return;
    }
    
    try {
      setCreating(true);
      const response = await apiCall('create_group', [
        groupName.trim(),
        selectedMembers,
        currentUser.username
      ]);

      if (response.status === 'success') {
        alert(`Đã tạo nhóm "${groupName}" thành công!`);
        onClose();
        // Refresh the page or reload chat list if needed
      } else {
        alert(`Không thể tạo nhóm: ${response.message || 'Có lỗi xảy ra'}`);
      }
    } catch (error) {
      console.error('Error creating group:', error);
      alert('Đã xảy ra lỗi khi tạo nhóm');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2 className="modal-title">Tạo nhóm mới</h2>
        
        <div className="form-group">
          <label>Tên nhóm</label>
          <input
            type="text"
            placeholder="Nhập tên nhóm"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Chọn thành viên</label>
          {loading ? (
            <div className="empty-state">Đang tải danh sách bạn bè...</div>
          ) : friends.length === 0 ? (
            <div className="empty-state">Bạn chưa có bạn bè để thêm vào nhóm</div>
          ) : (
            <div className="member-list">
              {friends.map((friend) => (
                <div key={friend.id} className="member-item">
                  <input
                    type="checkbox"
                    id={friend.id}
                    checked={selectedMembers.includes(friend.id)}
                    onChange={() => toggleMember(friend.id)}
                  />
                  <label htmlFor={friend.id} className="member-label">
                    <div className="avatar small">{friend.avatar}</div>
                    <span>{friend.username}</span>
                  </label>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-actions">
          <button className="btn-primary" onClick={handleCreate} disabled={creating || loading}>
            {creating ? 'Đang tạo...' : 'Tạo nhóm'}
          </button>
          <button className="btn-secondary" onClick={onClose}>
            Hủy
          </button>
        </div>
      </div>
    </div>
  );
}

export default CreateGroupModal;