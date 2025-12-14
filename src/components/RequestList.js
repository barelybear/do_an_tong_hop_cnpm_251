import React, { useState, useEffect } from 'react';
import '../styles/RequestList.css'; 
import { apiCall } from '../utils/api'; // Giả định module API này tồn tại

// Hàm hỗ trợ: Chuyển đổi Firestore Timestamp thành văn bản thân thiện
const formatTimestamp = (ts) => {
    // ts có thể là: 1. Đối tượng Firestore Timestamp, 2. Đối tượng Date, 3. Chuỗi (nếu API serialize)
    let date;
    
    // Xử lý đối tượng Firestore Timestamp (phổ biến)
    if (ts && typeof ts.toDate === 'function') {
        date = ts.toDate();
    } 
    // Xử lý trường hợp đã là đối tượng Date (ít phổ biến, thường gặp ở client side)
    else if (ts instanceof Date) {
        date = ts;
    }
    // Xử lý chuỗi ISO (nếu API serializes thành chuỗi)
    else if (typeof ts === 'string' || typeof ts === 'number') {
        date = new Date(ts);
    } 
    
    if (!date || isNaN(date.getTime())) return "Không xác định";
    
    const diffMs = Date.now() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return "Vừa xong";
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return `${Math.floor(diffHours / 24)} ngày trước`;
};

function RequestList({ searchQuery = '', currentUser }) {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load requests from API
    const loadRequests = async () => {
    setLoading(true); // Đảm bảo bắt đầu Loading
    try {
      let data = await apiCall("load_requests", { currentUser });
      let responseObject;

      // Bước 1: Parse dữ liệu (Chỉ parse nếu nó là chuỗi)
      if (typeof data === 'string' && data.trim().startsWith('{')) {
          try {
              responseObject = JSON.parse(data);
          } catch (e) {
              console.error("Failed to parse JSON string:", e);
              responseObject = null;
          }
      } else {
          // Dữ liệu đã là Object/Array/null/undefined
          responseObject = data;
      }
      
      // Bước 2: Truy cập MẢNG DỮ LIỆU CỤ THỂ theo cấu trúc response của bạn
      let requestsArray = [];
      // Kiểm tra responseObject tồn tại, status là 'success' và output là một Array
      if (responseObject && responseObject.status === 'success' && Array.isArray(responseObject.output)) {
          requestsArray = responseObject.output;
      }

      // Bước 3: Map Mảng (requestsArray luôn là một Array - dù là rỗng)
      const converted = requestsArray.map((req) => {
        // ... (Logic mapping của bạn)
        const {
            request_id: id,             
            from_username: fromUser,
            type,
            timestamp, // Cần đảm bảo formatTimestamp() xử lý được format DatetimeWithNanoseconds
            group_name: groupName,      
            group_member_count: memberCount 
        } = req;

        // Group Invite
        if (type === "group") {
            return {
              id: id, type: "group", groupName: groupName || 'Group Name', inviterName: fromUser, 
              avatar: "👥", timestamp: formatTimestamp(timestamp), memberCount: memberCount ?? 0,
            };
        }

        // Friend Request
        return {
            id: id, type: "friend", username: fromUser, 
            avatar: fromUser ? fromUser.slice(0, 2).toUpperCase() : '?', 
            timestamp: formatTimestamp(timestamp),
        };
      });

      // Bước 4: Cập nhật State
      setRequests(converted);
      setFilteredRequests(converted);
      // **UI chắc chắn sẽ cập nhật sau 2 lần set state này**

    } catch (e) {
      console.error("Failed to load requests:", e);
      // Xảy ra lỗi nặng, reset state
      setRequests([]); 
      setFilteredRequests([]);
    } finally {
      // Kết thúc Loading
      setLoading(false); 
    }
  };

  useEffect(() => {
    // Load request ban đầu
    loadRequests();
    // Bạn có thể thêm logic pull-to-refresh/refresh định kỳ tại đây nếu cần
  }, [currentUser]); // Chỉ chạy khi currentUser thay đổi

  // SEARCH EFFECT
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

  // Logic xóa request khỏi state
  const removeRequestFromState = (requestId) => {
    setRequests((prev) => prev.filter((r) => r.id !== requestId));
    setFilteredRequests((prev) => prev.filter((r) => r.id !== requestId));
  };

  // Accept
  const handleAccept = async (request) => {
    try {
      if (request.type === "friend") {
        await apiCall("add_friend", {
          request_id: request.id, 
          from: request.username, // Metadata phụ trợ cho backend
          to: currentUser // Cần biết người đang accept là ai để xử lý subcollection
        });
      } else {
        await apiCall("accept_group_invite", {
          request_id: request.id,
          from: request.inviterName, 
          group_name: request.groupName,
          to: currentUser // Cần biết người đang accept là ai
        });
      }
      
      removeRequestFromState(request.id);
      
    } catch (e) {
      console.error("Failed to accept request:", e);
      // Hiển thị thông báo lỗi cho người dùng (nếu có UI/toast system)
    }
  };

  // Reject
  const handleReject = async (request) => {
    try {
      // Cả hai hành động Reject/Delete đều cần 'request_id' và 'to' (currentUser) để tìm
      // document subcollection và xóa nó.
      
      if (request.type === "friend") {
        await apiCall("reject_friend_request", {
          request_id: request.id,
          from: request.username,
          to: currentUser
        });
      } else {
        await apiCall("reject_group_invite", {
          request_id: request.id,
          from: request.inviterName,
          group_name: request.groupName,
          to: currentUser
        });
      }
      
      removeRequestFromState(request.id);
      
    } catch (e) {
      console.error("Failed to reject request:", e);
    }
  };

  if (loading) {
    return <div className="loading-state">Đang tải lời mời...</div>;
  }
  
  // UI Render
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
        <div className="empty-state">Không tìm thấy lời mời với tìm kiếm hiện tại</div>
      )}
      {requests.length === 0 && !loading && (
        <div className="empty-state">Không có lời mời mới</div>
      )}
    </div>
  );
}

export default RequestList;