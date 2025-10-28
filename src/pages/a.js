import React, { useState } from 'react';
import '../styles/LoginPage.css';

function LoginPage({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    gmail: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
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
      // Mock registration success
      alert('Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.');
      setIsRegister(false);
    } else {
      // Mock login
      if (formData.username && formData.password) {
        onLogin({
          id: 'user123',
          username: formData.username,
          gmail: 'user@gmail.com',
          avatar: 'https://via.placeholder.com/150',
          status: 'online'
        });
      } else {
        alert('Sai tên đăng nhập hoặc mật khẩu.');
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
                required
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
                  required
                />
              </div>
            )}

            {!isRegister && (
              <div className="forgot-password">
                <a href="#forgot">Quên mật khẩu?</a>
              </div>
            )}

            <button type="submit" className="btn-primary">
              {isRegister ? 'Đăng ký' : 'Đăng nhập'}
            </button>

            <button
              type="button"
              className="btn-secondary"
              onClick={() => setIsRegister(!isRegister)}
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

