import React, { useState } from 'react';
import '../styles/RequestList.css';
import callPython from '../callApiPython';

function RequestList() {
  const [requests, setRequests] = useState([
    {
      id: 'req1',
      username: 'Trần Anh',
      avatar: 'TA',
      timestamp: '2 giờ trước'
    },
    {
      id: 'req2',
      username: 'Võ Hương',
      avatar: 'VH',
      timestamp: '1 ngày trước'
    }
  ]);

  const handleAccept = (requestId) => {
    // Xử lý chấp nhận lời mời
    setRequests(requests.filter(req => req.id !== requestId));
    alert('Đã chấp nhận lời mời kết bạn!');
  };

  const handleReject = (requestId) => {
    // Xử lý từ chối lời mời
    setRequests(requests.filter(req => req.id !== requestId));
    alert('Đã từ chối lời mời kết bạn!');
  };

  return (
    <div className="request-list">
      {requests.map((request) => (
        <div key={request.id} className="request-item">
          <div className="request-avatar">
            <div className="avatar">{request.avatar}</div>
          </div>
          <div className="request-info">
            <h3 className="request-name">{request.username}</h3>
            <p className="request-time">{request.timestamp}</p>
          </div>
          <div className="request-actions">
            <button
              className="btn-accept"
              onClick={() => handleAccept(request.id)}
            >
              Chấp nhận
            </button>
            <button
              className="btn-reject"
              onClick={() => handleReject(request.id)}
            >
              Từ chối
            </button>
          </div>
        </div>
      ))}
      {requests.length === 0 && (
        <div className="empty-state">Không có lời mời kết bạn mới</div>
      )}
    </div>
  );
}

export default RequestList;

