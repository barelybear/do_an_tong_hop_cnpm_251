# Các Field của Nhóm (Group Fields)

## Tài liệu về cấu trúc dữ liệu nhóm trong hệ thống

### 1. Class Group (helper.py)
```python
class Group:
    - group_name: str          # Tên nhóm
    - members: List[str]       # Danh sách username của các thành viên
    - admins: List[str]        # Danh sách username của các admin
```

### 2. Firestore Document Structure (collection: 'groups')
Khi tạo nhóm, document có các field sau:

#### Field bắt buộc:
- **`group_name`** (string): Tên nhóm (duy nhất)
- **`members`** (array): Danh sách username của các thành viên
  - Ví dụ: `["user1", "user2", "user3"]`
- **`admins`** (array): Danh sách username của các admin
  - Ví dụ: `["user1"]` (admin đầu tiên là người tạo nhóm)
- **`messages`** (array): Danh sách tin nhắn (ban đầu rỗng `[]`)
  - Cấu trúc message:
    ```python
    {
        'sender': str,           # Username người gửi
        'content': str,          # Nội dung tin nhắn
        'is_media': bool,        # Có phải media không
        'media_type': str/None,   # Loại media (image/video/file)
        'timestamp': datetime     # Thời gian gửi
    }
    ```

#### Field tùy chọn:
- **`created_date`** (string, ISO format): Ngày tạo nhóm
  - Format: ISO 8601 (ví dụ: `"2024-01-15T10:30:00"`)
  - Tự động set khi tạo nhóm
- **`description`** (string): Mô tả nhóm
  - Mặc định: `""` (chuỗi rỗng)
  - Có thể cập nhật sau

### 3. API Response Structure (get_group_info)
Khi gọi `get_group_info`, response trả về:
```python
{
    'group_name': str,
    'members': List[str],
    'admins': List[str],
    'created_date': str/None,    # ISO format hoặc None
    'description': str            # Mô tả nhóm hoặc ""
}
```

### 4. Các thao tác với field

#### Tạo nhóm mới:
- Tất cả field bắt buộc được set
- `created_date` tự động set
- `description` mặc định là chuỗi rỗng

#### Cập nhật nhóm:
- Có thể thêm/xóa thành viên (field `members`)
- Có thể thêm/xóa admin (field `admins`)
- Có thể cập nhật `description` (chưa có API riêng, cần thêm)

#### Xóa nhóm:
- Khi giải tán nhóm, document bị xóa hoàn toàn
- Tất cả thành viên được cập nhật (xóa nhóm khỏi `groups` của user)

### 5. Lưu ý
- `group_name` phải là duy nhất trong collection `groups`
- `admins` luôn là subset của `members` (admin phải là thành viên)
- Khi tạo nhóm, người tạo tự động là admin đầu tiên
- `messages` field trong document gốc có thể không được sử dụng (tin nhắn được lưu trong subcollection `conversation`)

