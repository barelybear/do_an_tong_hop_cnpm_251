// API utility for making requests to the backend
const API_BASE_URL = 'http://127.0.0.1:5000';

// Simple cache for API responses
const apiCache = {};
const CACHE_TTL = 5000; // 5 seconds cache TTL

// Functions that should NOT be cached (mutations, real-time data)
const NO_CACHE_FUNCTIONS = [
  'send_message_user',
  'send_message_group',
  'send_file_user',
  'send_file_group',
  'add_friend',
  'remove_friend',
  'block_user',
  'unblock_user',
  'accept_friend_request',
  'reject_friend_request',
  'create_group',
  'leave_group',
  'add_member_to_group',
  'remove_member_from_group',
  'update_profile',
  'update_avatar',
  'set_user_status',
  'login',
  'log_out',
  'sign_up'
];

function getCacheKey(functionName, args) {
  return `${functionName}_${JSON.stringify(args)}`;
}

function isCacheValid(cacheEntry) {
  if (!cacheEntry) return false;
  const now = Date.now();
  return (now - cacheEntry.timestamp) < CACHE_TTL;
}

export const apiCall = async (functionName, args = []) => {
  // Check if this function should be cached
  const shouldCache = !NO_CACHE_FUNCTIONS.includes(functionName);
  
  if (shouldCache) {
    const cacheKey = getCacheKey(functionName, args);
    const cached = apiCache[cacheKey];
    
    if (isCacheValid(cached)) {
      console.log(`[Cache Hit] ${functionName}`);
      return cached.data;
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        function_name: functionName,
        args: args
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Cache successful responses
    if (shouldCache && data.status === 'success') {
      const cacheKey = getCacheKey(functionName, args);
      apiCache[cacheKey] = {
        data: data,
        timestamp: Date.now()
      };
    }
    
    return data;
  } catch (error) {
    console.error(`Error calling ${functionName}:`, error);
    throw error;
  }
};

// Function to clear cache (useful after mutations)
export const clearApiCache = (functionName = null) => {
  if (functionName) {
    // Clear cache for specific function
    Object.keys(apiCache).forEach(key => {
      if (key.startsWith(`${functionName}_`)) {
        delete apiCache[key];
      }
    });
  } else {
    // Clear all cache
    Object.keys(apiCache).forEach(key => delete apiCache[key]);
  }
};

// Helper function to format timestamp for display
export const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  
  try {
    // Handle ISO format string
    if (typeof timestamp === 'string') {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) return timestamp;
      
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);
      
      if (diffMins < 1) return 'Vừa xong';
      if (diffMins < 60) return `${diffMins} phút trước`;
      if (diffHours < 24) return `${diffHours} giờ trước`;
      if (diffDays === 1) return 'Hôm qua';
      if (diffDays < 7) return `${diffDays} ngày trước`;
      
      // Format as time if same day, otherwise as date
      const isToday = date.toDateString() === now.toDateString();
      if (isToday) {
        return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      }
      return date.toLocaleDateString('vi-VN');
    }
    
    return timestamp;
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return timestamp;
  }
};

