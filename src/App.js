import React, { useState } from 'react';
import LoginPage from './pages/LoginPage';
import MainPage from './pages/MainPage';
import { apiCall } from './utils/api';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const handleLogin = (user) => {
    setCurrentUser(user);
    setIsLoggedIn(true);
  };

  const handleLogout = async () => {
    try {
      // Call logout API to update backend state
      const response = await apiCall('log_out', []);
      console.log('Logout response:', response);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear frontend state
      setCurrentUser(null);
      setIsLoggedIn(false);
    }
  };

  return (
    <div className="app">
      {!isLoggedIn ? (
        <LoginPage key="login-page" onLogin={handleLogin} />
      ) : (
        <MainPage currentUser={currentUser} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;


