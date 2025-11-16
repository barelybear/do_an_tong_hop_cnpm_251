import React, { useState, useEffect } from 'react';
import '../styles/ChatList.css';
import callPython from '../callApiPython';

function ChatList({ selectedChat, onSelectChat, searchQuery }) {
  const [chats, setChats] = useState([]);        // start empty
  const [filteredChats, setFilteredChats] = useState([]);

  useEffect(() => {
    // Function to fetch the chat list from the API
    async function fetchChats() {
      try {
        const res = await callPython({
          function_name: "load_chat_list",
          args: []
        });

        if (res && Array.isArray(res.output)) {
          setChats(res.output);
          // The filtering logic will be handled by the second useEffect
        } else {
          console.warn("⚠️ No chat list returned or the format is incorrect:", res);
        }
      } catch (error) {
        console.error("Failed to fetch chats:", error);
      }
    }

    // Fetch the chat list immediately when the component mounts
    fetchChats();

    // Set up an interval to fetch the chat list every 10 seconds
    const intervalId = setInterval(fetchChats, 10000); // 10000ms = 10 seconds

    // Cleanup function: this will be called when the component unmounts
    // to prevent memory leaks and unnecessary API calls.
    return () => clearInterval(intervalId);
  }, []); // The empty dependency array means this effect runs only once on mount

  // This effect handles filtering the chats whenever the search query or the main chat list changes
  useEffect(() => {
    if (searchQuery) {
      setFilteredChats(
        chats.filter(chat =>
          chat.name.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredChats(chats);
    }
  }, [searchQuery, chats]);

  return (
    <div className="chat-list">
      {filteredChats.map(chat => (
        <div
          key={chat.id}
          className={`chat-item ${selectedChat?.id === chat.id ? 'selected' : ''}`}
          onClick={() => onSelectChat(chat)}
        >
          <div className="chat-avatar">
            <div className={`avatar ${chat.type === 'group' ? 'group' : ''}`}>
              {chat.avatar}
            </div>
            {chat.type === 'direct' && chat.status === 'online' && (
              <span className="status-indicator online"></span>
            )}
          </div>
          <div className="chat-info">
            <div className="chat-header">
              <h3 className="chat-name">{chat.name}</h3>
              {/* Note: The timestamp from Python's datetime might need formatting */}
              <span className="chat-time">{chat.timestamp}</span>
            </div>
            <div className="chat-preview">
              <p className="last-message">{chat.lastMessage}</p>
              {chat.unread > 0 && (
                <span className="unread-badge">{chat.unread}</span>
              )}
            </div>
          </div>
        </div>
      ))}
      {filteredChats.length === 0 && (
        <div className="empty-state">Không tìm thấy cuộc trò chuyện</div>
      )}
    </div>
  );
}

export default ChatList;