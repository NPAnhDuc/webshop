import React, { useState, useRef, useEffect } from 'react';
import {
  ShieldCheck,
  Lock,
  User,
  KeyRound,
  QrCode,
  AlertCircle,
  HelpCircle,
  Eye,
  EyeOff,
  Sparkles,
  CheckCircle2,
  Cpu
} from 'lucide-react';
import { adminLogin, fetchOtpSetup } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

interface AdminLoginGateProps {
  onSuccess: () => void;
}

export const AdminLoginGate: React.FC<AdminLoginGateProps> = ({ onSuccess }) => {
  const { login } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // 6-digit OTP code state
  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showOtpModal, setShowOtpModal] = useState(false);
  const [otpSetupInfo, setOtpSetupInfo] = useState<any>(null);

  useEffect(() => {
    fetchOtpSetup()
      .then(info => setOtpSetupInfo(info))
      .catch(() => {});
  }, []);

  const handleOtpChange = (index: number, value: string) => {
    // Only accept numeric characters
    const cleanVal = value.replace(/\D/g, '');
    if (!cleanVal) {
      const newDigits = [...otpDigits];
      newDigits[index] = '';
      setOtpDigits(newDigits);
      return;
    }

    // If user pasted a string of numbers
    if (cleanVal.length > 1) {
      const pasted = cleanVal.slice(0, 6).split('');
      const newDigits = [...otpDigits];
      pasted.forEach((char, i) => {
        if (i < 6) newDigits[i] = char;
      });
      setOtpDigits(newDigits);
      const nextIndex = Math.min(pasted.length, 5);
      inputRefs.current[nextIndex]?.focus();
      return;
    }

    const newDigits = [...otpDigits];
    newDigits[index] = cleanVal[0];
    setOtpDigits(newDigits);

    // Jump to next input
    if (index < 5 && cleanVal) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpDigits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleQuickFillCurrentDevOtp = () => {
    if (otpSetupInfo?.currentDevOtp) {
      setOtpDigits(otpSetupInfo.currentDevOtp.split(''));
      setErrorMessage('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    const fullOtp = otpDigits.join('');
    if (fullOtp.length !== 6) {
      setErrorMessage('Vui lòng nhập đủ 6 chữ số mã OTP xác thực.');
      return;
    }

    setLoading(true);
    try {
      const res = await adminLogin({
        username: username.trim(),
        password: password.trim(),
        otp: fullOtp
      });

      if (res.success && res.token && res.user) {
        login(res.token, res.user);
        onSuccess();
      } else {
        setErrorMessage(res.message || 'Xác thực không thành công.');
      }
    } catch (err: any) {
      setErrorMessage('Lỗi kết nối tới máy chủ API: ' + (err.message || 'Không thể xác thực'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b0f19] via-[#0f172a] to-[#1e1b4b] flex items-center justify-center p-4 selection:bg-blue-600 selection:text-white">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-red-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative w-full max-w-md bg-[#131b2e]/90 backdrop-blur-xl border border-slate-700/80 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 animate-in fade-in duration-300">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 text-white shadow-lg shadow-blue-500/25 mb-1">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <div className="flex items-center justify-center space-x-1.5">
            <Cpu className="w-4 h-4 text-blue-400" />
            <h1 className="text-xl font-black uppercase tracking-tight text-white font-sans">
              TechStore <span className="text-blue-500">Admin Portal</span>
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Hệ thống quản trị bán lẻ & vận hành shop (Xác thực 2 lớp OTP)
          </p>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-3 bg-red-950/60 border border-red-500/50 rounded-2xl flex items-start space-x-2.5 text-xs text-red-200 animate-in shake">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1 leading-relaxed">{errorMessage}</div>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Username */}
          <div className="space-y-1.5">
            <label className="block font-bold text-slate-300">Tên đăng nhập</label>
            <div className="relative flex items-center">
              <User className="w-4 h-4 text-slate-500 absolute left-3.5 pointer-events-none" />
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="admin hoặc kho"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-700 focus:border-blue-500 rounded-xl text-slate-100 placeholder:text-slate-500 text-xs outline-none transition"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="block font-bold text-slate-300">Mật khẩu</label>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-[11px] text-slate-400 hover:text-slate-200 transition cursor-pointer flex items-center space-x-1"
              >
                {showPassword ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                <span>{showPassword ? 'Ẩn' : 'Hiện'}</span>
              </button>
            </div>
            <div className="relative flex items-center">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 pointer-events-none" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu quản trị"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-700 focus:border-blue-500 rounded-xl text-slate-100 placeholder:text-slate-500 text-xs outline-none transition"
                required
              />
            </div>
          </div>

          {/* 2FA OTP 6-Digit Section */}
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <KeyRound className="w-3.5 h-3.5 text-amber-400" />
                <label className="font-bold text-slate-200">
                  Mã xác thực 2FA (OTP 6 số)
                </label>
              </div>
              <button
                type="button"
                onClick={() => setShowOtpModal(true)}
                className="text-[11px] text-blue-400 hover:text-blue-300 flex items-center space-x-1 cursor-pointer transition font-medium"
              >
                <QrCode className="w-3 h-3" />
                <span>Cài Authenticator</span>
              </button>
            </div>

            {/* 6 Digit Input Boxes */}
            <div className="grid grid-cols-6 gap-2 pt-1">
              {otpDigits.map((digit, idx) => (
                <input
                  key={idx}
                  ref={el => { inputRefs.current[idx] = el; }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={e => handleOtpChange(idx, e.target.value)}
                  onKeyDown={e => handleKeyDown(idx, e)}
                  className="w-full h-12 text-center text-lg font-mono font-black rounded-xl bg-slate-900/90 border border-slate-700 text-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition"
                />
              ))}
            </div>

            {/* Helper quick fills for testing */}
            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
              <span>Đổi mới mỗi 30 giây</span>
              {/* Only present when the backend runs with ADMIN_OTP_DEV_HELPER=true (local development) */}
              {otpSetupInfo?.currentDevOtp && (
                <button
                  type="button"
                  onClick={handleQuickFillCurrentDevOtp}
                  className="text-emerald-400 hover:underline cursor-pointer"
                  title="Lấy mã TOTP hiện tại (chỉ môi trường dev)"
                >
                  Điền mã Live (dev)
                </button>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl text-sm transition shadow-lg shadow-blue-600/25 active:scale-98 cursor-pointer flex items-center justify-center space-x-2 disabled:opacity-60"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Đang xác thực...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>Xác thực & Vào Trung Tâm Quản Trị</span>
                </>
              )}
            </button>
          </div>
        </form>

        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-2xl text-[11px] text-slate-400 space-y-1">
          <div className="font-bold text-slate-300 flex items-center space-x-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Lưu ý bảo mật:</span>
          </div>
          <p className="text-[10.5px]">
            Tài khoản, mật khẩu và khóa OTP được cấu hình trên máy chủ. Phiên đăng nhập tự hết hạn; khi đó bạn sẽ được đưa về màn hình này.
          </p>
        </div>
      </div>

      {/* Google Authenticator Setup Modal */}
      {showOtpModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-[#151c2c] border border-slate-700 max-w-md w-full rounded-3xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2 text-white font-bold text-sm">
                <QrCode className="w-4 h-4 text-blue-400" />
                <span>Cài Đặt Google Authenticator (TOTP)</span>
              </div>
              <button
                onClick={() => setShowOtpModal(false)}
                className="text-slate-400 hover:text-white cursor-pointer font-bold px-2 py-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <p>
                Trang Admin áp dụng chuẩn mã hóa <strong>RFC 6238</strong>. Bạn có thể dùng <strong>Google Authenticator</strong>, <strong>Microsoft Authenticator</strong>, hoặc <strong>Authy</strong> trên điện thoại.
              </p>

              <div className="p-3 bg-slate-900 rounded-2xl border border-slate-800 space-y-2">
                <p className="text-slate-400 text-[11px] font-semibold">Khóa bí mật (Base32 Secret Key):</p>
                <div className="p-2 bg-black/50 rounded-xl font-mono text-amber-400 text-sm font-bold text-center tracking-widest border border-slate-800">
                  {otpSetupInfo?.secret || 'Liên hệ chủ shop để nhận khóa (ADMIN_TOTP_SECRET)'}
                </div>
                <p className="text-[10px] text-slate-500">
                  Cách thêm: Trong app Google Authenticator bấm <strong>+</strong> → chọn <strong>Nhập khóa thiết lập</strong> → Nhập tên tài khoản & dán khóa trên.
                </p>
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={() => setShowOtpModal(false)}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition cursor-pointer"
              >
                Đã hiểu, quay lại đăng nhập
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
