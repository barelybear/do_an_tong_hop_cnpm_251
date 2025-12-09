import React, { useState, useEffect } from 'react';
import '../styles/RequestList.css';
import { apiCall } from '../utils/api';

function RequestList({ searchQuery = '', currentUser }) {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);

  // Convert Firestore timestamp → text
  const formatTimestamp = (ts) => {
    if (!ts) return "";
    const date = ts.toDate();
    const diffMs = Date.now() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHours < 1) return "Vừa xong";
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return `${Math.floor(diffHours / 24)} ngày trước`;
  };

  // Load requests from API
  const loadRequests = async () => {
    try {
      const data = await apiCall("load_requests", {currentUser}); // ← bạn chỉnh theo cách gọi API của bạn

      const converted = data.map((req) => {
        const [
          fromUser,
          _same,
          type,
          avatar,
          timestamp,
          groupName,
          memberCount
        ] = req;

        if (type === "group") {
          return {
            id: `${fromUser}-${groupName}`,
            type: "group",
            groupName,
            inviterName: fromUser,
            avatar: "👥",
            timestamp: formatTimestamp(timestamp),
            memberCount: memberCount ?? 0,
          };
        }

        return {
          id: `${fromUser}-friend`,
          type: "friend",
          username: fromUser,
          avatar,
          timestamp: formatTimestamp(timestamp),
        };
      });

      setRequests(converted);
      setFilteredRequests(converted);
    } catch (e) {
      console.error("Failed to load requests:", e);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  // SEARCH
  useEffect(() => {
    if (!searchQuery) {
      setFilteredRequests(requests);
      return;
    }

    const q = searchQuery.toLowerCase();
    setFilteredRequests(
      requests.filter((req) => {
        if (req.type === "group") {
          return (
            req.groupName.toLowerCase().includes(q) ||
            req.inviterName.toLowerCase().includes(q)
          );
        } else {
          return req.username.toLowerCase().includes(q);
        }
      })
    );
  }, [searchQuery, requests]);

  // Accept
  const handleAccept = async (request) => {
    try {
      if (request.type === "friend") {
        await apiCall("accept_friend_request", {
          from: request.username,
        });
      } else {
        await apiCall("accept_group_invite", {
          from: request.inviterName,
          group_name: request.groupName,
        });
      }

      setRequests((prev) => prev.filter((r) => r.id !== request.id));
      setFilteredRequests((prev) => prev.filter((r) => r.id !== request.id));
    } catch (e) {
      console.error(e);
    }
  };

  // Reject
  const handleReject = async (request) => {
    try {
      if (request.type === "friend") {
        await apiCall("reject_friend_request", {
          from: request.username,
        });
      } else {
        await apiCall("reject_group_invite", {
          from: request.inviterName,
          group_name: request.groupName,
        });
      }

      setRequests((prev) => prev.filter((r) => r.id !== request.id));
      setFilteredRequests((prev) => prev.filter((r) => r.id !== request.id));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="request-list">
      {filteredRequests.map((req) => (
        <div key={req.id} className={`request-item ${req.type === "group" ? "group-request" : ""}`}>
          <div className="request-avatar">
            <div className={`avatar ${req.type === "group" ? "group" : ""}`}>
              {req.avatar}
            </div>
          </div>

          <div className="request-info">
            {req.type === "group" ? (
              <>
                <h3 className="request-name">
                  <span className="request-type-label">👥 Nhóm:</span> {req.groupName}
                </h3>
                <p className="request-description">
                  {req.inviterName} mời bạn tham gia • {req.memberCount} thành viên
                </p>
                <p className="request-time">{req.timestamp}</p>
              </>
            ) : (
              <>
                <h3 className="request-name">{req.username}</h3>
                <p className="request-description">Muốn kết bạn với bạn</p>
                <p className="request-time">{req.timestamp}</p>
              </>
            )}
          </div>

          <div className="request-actions">
            <button className="btn-accept" onClick={() => handleAccept(req)}>
              {req.type === "group" ? "Tham gia" : "Chấp nhận"}
            </button>

            <button className="btn-reject" onClick={() => handleReject(req)}>
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
