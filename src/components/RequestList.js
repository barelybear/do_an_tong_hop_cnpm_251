import React, { useState, useEffect } from 'react';
import '../styles/RequestList.css';

function RequestList({ searchQuery = '' }) {
  const [requests, setRequests] = useState([
    {
      id: 'req1',
      type: 'friend',
      username: 'Trần Anh',
      avatar: 'TA',
      timestamp: '2 giờ trước'
    },
    {
      id: 'req2',
      type: 'friend',
      username: 'Võ Hương',
      avatar: 'VH',
      timestamp: '1 ngày trước'
    },
    {
      id: 'req3',
      type: 'group',
      groupName: 'Nhóm Học Tập',
      inviterName: 'Nguyễn Hoàng',
      avatar: '👥',
      timestamp: '3 giờ trước',
      memberCount: 12
    },
    {
      id: 'req4',
      type: 'group',
      groupName: 'Nhóm Dự Án Web',
      inviterName: 'Phạm Thảo',
      avatar: '👥',
      timestamp: '1 ngày trước',
      memberCount: 8
    }
  ]);

  const [filteredRequests, setFilteredRequests] = useState(requests);

  // Filter requests based on search query
  useEffect(() => {
    if (searchQuery) {
      const queryLower = searchQuery.toLowerCase();
      setFilteredRequests(
        requests.filter(request => {
          if (request.type === 'group') {
            // Search in group name or inviter name
            return (request.groupName && request.groupName.toLowerCase().includes(queryLower)) ||
                   (request.inviterName && request.inviterName.toLowerCase().includes(queryLower));
          } else {
            // Search in username
            return request.username && request.username.toLowerCase().includes(queryLower);
          }
        })
      );
    } else {
      setFilteredRequests(requests);
    }
  }, [searchQuery, requests]);

  const handleAccept = (requestId, type) => {
    // Xử lý chấp nhận lời mời
    setRequests(requests.filter(req => req.id !== requestId));
    if (type === 'group') {
      alert('Đã tham gia nhóm!');
    } else {
      alert('Đã chấp nhận lời mời kết bạn!');
    }
  };

  const handleReject = (requestId, type) => {
    // Xử lý từ chối lời mời
    setRequests(requests.filter(req => req.id !== requestId));
    if (type === 'group') {
      alert('Đã từ chối lời mời tham gia nhóm!');
    } else {
      alert('Đã từ chối lời mời kết bạn!');
    }
  };

  return (
    <div className="request-list">
      {filteredRequests.map((request) => (
        <div key={request.id} className={`request-item ${request.type === 'group' ? 'group-request' : ''}`}>
          <div className="request-avatar">
            <div className={`avatar ${request.type === 'group' ? 'group' : ''}`}>
              {request.avatar}
            </div>
          </div>
          <div className="request-info">
            {request.type === 'group' ? (
              <>
                <h3 className="request-name">
                  <span className="request-type-label">👥 Nhóm:</span> {request.groupName}
                </h3>
                <p className="request-description">
                  {request.inviterName} mời bạn tham gia
                  {request.memberCount && ` • ${request.memberCount} thành viên`}
                </p>
                <p className="request-time">{request.timestamp}</p>
              </>
            ) : (
              <>
                <h3 className="request-name">{request.username}</h3>
                <p className="request-description">Muốn kết bạn với bạn</p>
                <p className="request-time">{request.timestamp}</p>
              </>
            )}
          </div>
          <div className="request-actions">
            <button
              className="btn-accept"
              onClick={() => handleAccept(request.id, request.type)}
            >
              {request.type === 'group' ? 'Tham gia' : 'Chấp nhận'}
            </button>
            <button
              className="btn-reject"
              onClick={() => handleReject(request.id, request.type)}
            >
              Từ chối
            </button>
          </div>
        </div>
      ))}
      {filteredRequests.length === 0 && requests.length > 0 && (
        <div className="empty-state">Không tìm thấy lời mời</div>
      )}
      {requests.length === 0 && (
        <div className="empty-state">Không có lời mời mới</div>
      )}
    </div>
  );
}

export default RequestList;


