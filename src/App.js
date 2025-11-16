import React, { useState } from 'react';
import LoginPage from './pages/LoginPage';
import MainPage from './pages/MainPage';
import callPython from './callApiPython';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const handleLogin = (user) => {
    setCurrentUser(user);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsLoggedIn(false);
    callPython("logout", currentUser)
  };

  return (
    <div className="app">
      {!isLoggedIn ? (
        <LoginPage onLogin={handleLogin} />
      ) : (
        <MainPage currentUser={currentUser} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;

