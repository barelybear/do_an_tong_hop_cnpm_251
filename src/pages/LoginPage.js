import React, { useState } from 'react';
import '../styles/LoginPage.css';
import callPython from '../callApiPython';
import { ca } from 'google-translate-api/languages';

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

      const data = await callPython({function_name: "sign_up", args: [formData.username, formData.password, formData.gmail]});
      if (!data.output) {
        if (data.running) {
          alert('Loading... Vui lòng chờ.');
          return;
        }
        alert('Đăng ký thất bại tên đăng nhập hoặc gmail đã tồn tại. Vui lòng thử lại.');
        return;
      }
      
      alert('Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.');
      setIsRegister(false);
    } else {
      console.log("Submitting login for", formData.username);
      const data = await callPython({function_name: "login", args: [formData.username, formData.password]});
      if (!data.output) {
        if (data.running) {
          alert('Loading... Vui lòng chờ.');
          return;
        }
        alert('Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.');
        return;
      }
      alert('Đăng nhập thành công! Xin chào ' + formData.username);
      onLogin(formData.username);
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

