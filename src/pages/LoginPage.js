import React, { useState, useEffect } from 'react';
import '../styles/LoginPage.css';
import { apiCall } from '../utils/api';

function LoginPage({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    gmail: ''
  });

  // Reset form when component mounts (e.g., after logout)
  useEffect(() => {
    setFormData({
      username: '',
      password: '',
      confirmPassword: '',
      gmail: ''
    });
    setIsRegister(false);
    setLoading(false);
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isRegister) {
      // Validate registration
      if (formData.password !== formData.confirmPassword) {
        alert('Mật khẩu không khớp.');
        return;
      }
      if (!formData.gmail || !formData.username) {
        alert('Vui lòng điền đầy đủ thông tin.');
        return;
      }
      
      // Call sign up API
      try {
        setLoading(true);
        const response = await apiCall('sign_up', [formData.username, formData.password, formData.gmail]);
        if (response.status === 'success' && response.output) {
          alert('Đăng ký thành công! Vui lòng đăng nhập.');
          setIsRegister(false);
          // Keep username and gmail, only clear passwords
          setFormData({ 
            username: formData.username,
            gmail: formData.gmail,
            password: '', 
            confirmPassword: '' 
          });
          setLoading(false);
        } else {
          alert(response.message || 'Đăng ký thất bại. Vui lòng thử lại.');
          setLoading(false);
        }
      } catch (error) {
        console.error('Registration error:', error);
        alert('Lỗi kết nối đến server. Vui lòng thử lại.');
      } finally {
        setLoading(false);
      }
    } else {
      // Call login API
      if (formData.username && formData.password) {
        try {
          setLoading(true);
          const response = await apiCall('login', [formData.username, formData.password]);
          if (response.status === 'success' && response.output && response.is_user) {
            onLogin({
              id: response.username,
              username: response.username,
              gmail: response.gmail,
              avatar: 'https://via.placeholder.com/150',
              status: 'online'
            });
          } else {
            alert('Sai tên đăng nhập hoặc mật khẩu.');
          }
        } catch (error) {
          console.error('Login error:', error);
          alert('Lỗi kết nối đến server. Vui lòng thử lại.');
        } finally {
          setLoading(false);
        }
      } else {
        alert('Vui lòng điền đầy đủ thông tin.');
      }
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <h1 className="login-title">Đăng nhập</h1>
          <p className="login-subtitle">Chào mừng bạn trở lại!</p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                name="username"
                placeholder="Nhập username"
                value={formData.username}
                onChange={handleChange}
                disabled={loading}
                required
                autoFocus
              />
            </div>

            {isRegister && (
              <div className="form-group">
                <label>Gmail</label>
                <input
                  type="email"
                  name="gmail"
                  placeholder="Nhập gmail"
                  value={formData.gmail}
                  onChange={handleChange}
                  disabled={loading}
                  required
                />
              </div>
            )}

            <div className="form-group">
              <label>Mật khẩu</label>
              <input
                type="password"
                name="password"
                placeholder="Nhập mật khẩu"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            {isRegister && (
              <div className="form-group">
                <label>Xác nhận mật khẩu</label>
                <input
                  type="password"
                  name="confirmPassword"
                  placeholder="Nhập lại mật khẩu"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  disabled={loading}
                  required
                />
              </div>
            )}

            {!isRegister && (
              <div className="forgot-password">
                <a href="#forgot">Quên mật khẩu?</a>
              </div>
            )}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Đang xử lý...' : (isRegister ? 'Đăng ký' : 'Đăng nhập')}
            </button>

            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setIsRegister(!isRegister);
                // Clear form when switching between login/register
                setFormData({
                  username: '',
                  password: '',
                  confirmPassword: '',
                  gmail: ''
                });
              }}
              disabled={loading}
            >
              {isRegister ? 'Đã có tài khoản? Đăng nhập' : 'Tạo tài khoản mới'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;


