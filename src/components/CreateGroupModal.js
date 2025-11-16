import React, { useState } from 'react';
import '../styles/CreateGroupModal.css';
import callPython from '../callApiPython';

function CreateGroupModal({ onClose }) {
  const [groupName, setGroupName] = useState('');
  const [selectedMembers, setSelectedMembers] = useState([]);

  // Mock friends list
  const friends = [
    { id: 'user1', username: 'Nguyễn Hoàng', avatar: 'NH' },
    { id: 'user2', username: 'Phạm Thảo', avatar: 'PT' },
    { id: 'user3', username: 'Lê Minh', avatar: 'LM' }
  ];

  const toggleMember = (friendId) => {
    if (selectedMembers.includes(friendId)) {
      setSelectedMembers(selectedMembers.filter(id => id !== friendId));
    } else {
      setSelectedMembers([...selectedMembers, friendId]);
    }
  };

  const handleCreate = () => {
    if (!groupName.trim()) {
      alert('Vui lòng nhập tên nhóm');
      return;
    }
    if (selectedMembers.length === 0) {
      alert('Vui lòng chọn ít nhất một thành viên');
      return;
    }
    
    // Mock tạo nhóm
    alert(`Đã tạo nhóm "${groupName}" với ${selectedMembers.length} thành viên`);
    onClose();
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
        </div>

        <div className="modal-actions">
          <button className="btn-primary" onClick={handleCreate}>
            Tạo nhóm
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

