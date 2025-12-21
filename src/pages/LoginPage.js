import React, { useState, useEffect } from 'react';
import '../styles/LoginPage.css';
import { apiCall } from '../utils/api';

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register' | 'forgot'
  const [step, setStep] = useState('input'); // 'input' | 'verify' | 'new_password'
  const [loading, setLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [userCode, setUserCode] = useState('');

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    gmail: ''
  });

  useEffect(() => {
    resetForm();
  }, []);

  const resetForm = () => {
    setFormData({ username: '', password: '', confirmPassword: '', gmail: '' });
    setMode('login');
    setStep('input');
    setGeneratedCode(null);
    setUserCode('');
    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // --- HÀM XÁC THỰC EMAIL ---
  const handleRequestVerify = async () => {
    if (!formData.gmail) {
      alert('Vui lòng nhập Email.');
      return;
    }

    try {
      setLoading(true);
      // Mode register => true, forgot password => false
      const isSignUp = (mode === 'register');
      const response = await apiCall('verify_email', [formData.gmail, isSignUp]);
      
      const out = parseInt(response.output);

      if (out === -1) {
        alert('Email không tồn tại hoặc định dạng không hợp lệ.');
      } else if (out === -2) {
        if (isSignUp) {
          alert('Email này đã được sử dụng cho một tài khoản khác.');
        } else {
          alert('Email này không tồn tại trong hệ thống của chúng tôi.');
        }
      } else if (response.status === 'success') {
        setGeneratedCode(out.toString()); // Lưu mã OTP để đối chiếu
        setStep('verify');
        alert('Mã xác thực đã được gửi xử lý. Vui lòng nhập mã để tiếp tục.');
      } else {
        alert('Có lỗi xảy ra: ' + response.message);
      }
    } catch (error) {
      console.error(error);
      alert('Lỗi kết nối server khi xác thực.');
    } finally {
      setLoading(false);
    }
  };

  // --- HÀM XỬ LÝ SUBMIT CHÍNH ---
  const handleSubmit = async (e) => {
    e.preventDefault();

    // 1. Chế độ Đăng nhập bình thường
    if (mode === 'login') {
      try {
        setLoading(true);
        const response = await apiCall('login', [formData.username, formData.password]);
        if (response.status === 'success' && response.is_user) {
          onLogin({
            id: response.username,
            username: response.username,
            gmail: response.gmail,
            avatar: 'https://via.placeholder.com/150'
          });
        } else {
          alert('Sai tên đăng nhập hoặc mật khẩu.');
        }
      } catch (err) {
        alert('Lỗi kết nối server.');
      } finally {
        setLoading(false);
      }
    } 

    // 2. Chế độ Nhập mã xác thực (Verify Step)
    else if (step === 'verify') {
      if (userCode === generatedCode) {
        if (mode === 'register') {
          finalSignUp(); // Khớp mã thì đăng ký luôn
        } else if (mode === 'forgot') {
          setStep('new_password'); // Khớp mã thì đi tới màn hình đặt pass mới
        }
      } else {
        alert('Mã xác nhận không chính xác.');
      }
    }

    // 3. Chế độ Quên mật khẩu: Đặt mật khẩu mới
    else if (step === 'new_password') {
      if (formData.password !== formData.confirmPassword) {
        alert('Mật khẩu không khớp.');
        return;
      }
      try {
        setLoading(true);
        const response = await apiCall('forget_password', [formData.password, formData.gmail]);
        if (response.status === 'success') {
          alert('Đặt lại mật khẩu thành công! Hãy đăng nhập lại.');
          resetForm();
        } else {
          alert('Lỗi: ' + response.message);
        }
      } catch (err) {
        alert('Lỗi kết nối server.');
      } finally {
        setLoading(false);
      }
    }
  };

  const finalSignUp = async () => {
    try {
      setLoading(true);
      const response = await apiCall('sign_up', [formData.username, formData.password, formData.gmail]);
      if (response.status === 'success') {
        alert('Đăng ký thành công! Hãy đăng nhập.');
        resetForm();
      } else {
        alert('Đăng ký thất bại: ' + response.message);
      }
    } catch (err) {
      alert('Lỗi kết nối server.');
    } finally {
      setLoading(false);
    }
  };

  // Render các thành phần Form tùy theo Mode và Step
  const renderFormFields = () => {
    if (step === 'verify') {
      return (
        <div className="form-group">
          <label>Mã xác thực</label>
          <input 
            type="text" 
            placeholder="Nhập mã OTP" 
            value={userCode} 
            onChange={(e) => setUserCode(e.target.value)} 
            required 
          />
          <button type="submit" className="btn-primary" style={{marginTop: '20px'}}>Xác thực mã</button>
        </div>
      );
    }

    if (step === 'new_password') {
      return (
        <>
          <div className="form-group">
            <label>Mật khẩu mới</label>
            <input type="password" name="password" onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Xác nhận mật khẩu</label>
            <input type="password" name="confirmPassword" onChange={handleChange} required />
          </div>
          <button type="submit" className="btn-primary">Đặt lại mật khẩu</button>
        </>
      );
    }

    // Các trường mặc định khi ở step "input"
    return (
      <>
        {mode !== 'forgot' && (
          <div className="form-group">
            <label>Username</label>
            <input type="text" name="username" value={formData.username} onChange={handleChange} required />
          </div>
        )}
        
        {(mode === 'register' || mode === 'forgot') && (
          <div className="form-group">
            <label>Gmail</label>
            <input type="email" name="gmail" value={formData.gmail} onChange={handleChange} required />
          </div>
        )}

        {mode !== 'forgot' && (
          <div className="form-group">
            <label>Mật khẩu</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required />
          </div>
        )}

        {mode === 'register' && (
          <div className="form-group">
            <label>Xác nhận mật khẩu</label>
            <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} required />
          </div>
        )}

        {mode === 'login' ? (
          <>
            <div className="forgot-password">
              <a href="#forgot" onClick={() => { setMode('forgot'); setStep('input'); }}>Quên mật khẩu?</a>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>Đăng nhập</button>
          </>
        ) : (
          <button type="button" className="btn-primary" onClick={handleRequestVerify} disabled={loading}>
            Gửi mã xác thực
          </button>
        )}
      </>
    );
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <h1 className="login-title">
            {mode === 'login' ? 'Đăng nhập' : mode === 'register' ? 'Đăng ký' : 'Khôi phục tài khoản'}
          </h1>
          
          <form onSubmit={handleSubmit}>
            {renderFormFields()}

            <button
              type="button"
              className="btn-secondary"
              style={{ marginTop: '10px' }}
              onClick={() => {
                if (mode === 'login') setMode('register');
                else resetForm();
              }}
              disabled={loading}
            >
              {mode === 'login' ? 'Tạo tài khoản mới' : 'Quay lại đăng nhập'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;