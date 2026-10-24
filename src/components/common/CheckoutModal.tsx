import React, { useState } from 'react';
import {
  X,
  ShieldCheck,
  CheckCircle2,
  Truck,
  CreditCard,
  Banknote,
  ArrowRight,
  Tag
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { createOrder, validateCoupon } from '../../services/api';
import { triggerConfetti } from '../../utils/confetti';
import { sound } from '../../utils/sound';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOrderSuccess: (orderCode: string) => void;
}

export const CheckoutModal: React.FC<CheckoutModalProps> = ({
  isOpen,
  onClose,
  onOrderSuccess
}) => {
  const { cart, totalAmount, clearCart } = useCart();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('Hà Nội');
  const [notes, setNotes] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'cod' | 'bank_transfer'>('cod');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voucherCode, setVoucherCode] = useState('');
  const [discountAmount, setDiscountAmount] = useState(0);
  const [appliedVoucherLabel, setAppliedVoucherLabel] = useState<string | null>(null);

  const [validatingVoucher, setValidatingVoucher] = useState(false);

  if (!isOpen) return null;

  const handleApplyVoucher = async (codeToApply?: string) => {
    const code = (codeToApply || voucherCode).trim().toUpperCase();
    if (!code) return;
    setError(null);
    setValidatingVoucher(true);

    try {
      const res = await validateCoupon(code, totalAmount);
      if (res.success && res.valid) {
        setDiscountAmount(res.discountAmount || 0);
        setAppliedVoucherLabel(res.label || `${code} (-${new Intl.NumberFormat('vi-VN').format(res.discountAmount)}₫)`);
        setVoucherCode(code);
        triggerConfetti();
        sound.playVoucherSuccess();
      } else {
        setError(res.message || 'Mã giảm giá không hợp lệ hoặc đã hết lượt.');
      }
    } catch (err: any) {
      console.error(err);
      setError('Lỗi khi xác thực mã giảm giá.');
    } finally {
      setValidatingVoucher(false);
    }
  };

  const finalCheckoutAmount = Math.max(0, totalAmount - discountAmount);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !phone.trim() || !address.trim()) {
      setError('Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ giao hàng.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const itemsPayload = cart.map(item => ({
        variantId: item.variantId,
        qty: item.qty
      }));

      const res = await createOrder({
        customerName: name,
        customerPhone: phone,
        customerAddress: address,
        customerCity: city,
        notes,
        items: itemsPayload,
        paymentMethod
      });

      if (res.success && res.order) {
        clearCart();
        onClose();
        onOrderSuccess(res.order.orderCode);
      } else {
        setError(res.message || 'Không thể tạo đơn hàng, vui lòng thử lại.');
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Lỗi kết nối máy chủ.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#151c2c] rounded-2xl max-w-xl w-full p-6 sm:p-8 shadow-2xl border border-slate-200 dark:border-slate-800 relative text-slate-800 dark:text-slate-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2.5 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-[#d70018] text-white flex items-center justify-center font-bold shadow-sm shadow-emerald-500/20">
            <Truck className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Thông Tin Đặt Hàng & Giao Hàng</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Đặt hàng nhanh không cần tạo tài khoản rườm rà</p>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 rounded-lg text-xs text-red-700 dark:text-red-300 font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-5 space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Họ và tên người nhận *</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Nguyễn Văn A"
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-[#d70018] dark:focus:border-emerald-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Số điện thoại *</label>
              <input
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="0912 345 678"
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-[#d70018] dark:focus:border-emerald-500 focus:outline-none"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Địa chỉ giao hàng (Số nhà, đường) *</label>
              <input
                type="text"
                value={address}
                onChange={e => setAddress(e.target.value)}
                placeholder="Số 45, Đường Xuân Thủy, Cầu Giấy"
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-[#d70018] dark:focus:border-emerald-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Tỉnh / Thành phố</label>
              <select
                value={city}
                onChange={e => setCity(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 focus:border-[#d70018] dark:focus:border-emerald-500 focus:outline-none"
              >
                <option value="Hà Nội">Hà Nội</option>
                <option value="TP. Hồ Chí Minh">TP. Hồ Chí Minh</option>
                <option value="Đà Nẵng">Đà Nẵng</option>
                <option value="Hải Phòng">Hải Phòng</option>
                <option value="Cần Thơ">Cần Thơ</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Ghi chú cho shipper (tùy chọn)</label>
            <input
              type="text"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Giao trong giờ hành chính / Gọi trước khi đến"
              className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-[#d70018] dark:focus:border-emerald-500 focus:outline-none"
            />
          </div>

          {/* Payment Method */}
          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-2">Hình thức thanh toán</label>
            <div className="grid grid-cols-2 gap-3">
              <label
                onClick={() => setPaymentMethod('cod')}
                className={`p-3 rounded-xl border flex items-center space-x-2.5 cursor-pointer transition select-none ${
                  paymentMethod === 'cod'
                    ? 'border-[#d70018] bg-emerald-50 dark:bg-emerald-950/40 text-[#d70018] dark:text-red-400 font-bold'
                    : 'border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                }`}
              >
                <Banknote className="w-4 h-4 text-emerald-600 dark:text-red-400" />
                <span>Thanh toán COD khi nhận</span>
              </label>
              <label
                onClick={() => setPaymentMethod('bank_transfer')}
                className={`p-3 rounded-xl border flex items-center space-x-2.5 cursor-pointer transition select-none ${
                  paymentMethod === 'bank_transfer'
                    ? 'border-[#d70018] bg-emerald-50 dark:bg-emerald-950/40 text-[#d70018] dark:text-red-400 font-bold'
                    : 'border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                }`}
              >
                <CreditCard className="w-4 h-4 text-[#d70018] dark:text-red-400" />
                <span>Chuyển khoản QR ngân hàng</span>
              </label>
            </div>
          </div>

          {/* Voucher Input */}
          <div className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center space-x-1 text-[#d70018] dark:text-red-400">
                <Tag className="w-3.5 h-3.5" />
                <span>Mã giảm giá / Voucher</span>
              </span>
              {appliedVoucherLabel && (
                <button
                  type="button"
                  onClick={() => {
                    setDiscountAmount(0);
                    setAppliedVoucherLabel(null);
                  }}
                  className="text-[10px] text-red-500 hover:underline"
                >
                  Xóa mã
                </button>
              )}
            </div>
            {!appliedVoucherLabel ? (
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={voucherCode}
                  onChange={e => setVoucherCode(e.target.value.toUpperCase())}
                  placeholder="Nhập mã (VD: TECH500)"
                  className="flex-1 px-3 py-1.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 text-xs font-mono focus:border-[#d70018] focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => handleApplyVoucher()}
                  className="px-3.5 py-1.5 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-lg text-xs font-bold transition cursor-pointer"
                >
                  Áp dụng
                </button>
              </div>
            ) : (
              <div className="flex items-center justify-between text-xs font-bold text-emerald-600 dark:text-red-400">
                <span>✓ Đã áp dụng: {appliedVoucherLabel}</span>
                <span className="font-mono">-{new Intl.NumberFormat('vi-VN').format(discountAmount)}₫</span>
              </div>
            )}
          </div>

          {/* Price Summary */}
          <div className="p-3.5 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-800 space-y-1.5 pt-3">
            <div className="flex justify-between text-slate-600 dark:text-slate-400">
              <span>Tổng tiền hàng ({cart.length} món):</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{new Intl.NumberFormat('vi-VN').format(totalAmount)}₫</span>
            </div>
            <div className="flex justify-between text-slate-600 dark:text-slate-400">
              <span>Phí giao hàng:</span>
              <span className="text-emerald-600 dark:text-red-400 font-semibold">Miễn phí toàn quốc</span>
            </div>
            {discountAmount > 0 && (
              <div className="flex justify-between text-emerald-600 dark:text-red-400 text-xs font-semibold">
                <span>Ưu đãi giảm giá:</span>
                <span className="font-mono font-bold">-{new Intl.NumberFormat('vi-VN').format(discountAmount)}₫</span>
              </div>
            )}
            <div className="flex justify-between items-baseline pt-2 border-t border-slate-200 dark:border-slate-700 text-sm font-bold text-slate-900 dark:text-slate-100">
              <span>Tổng thanh toán:</span>
              <span className="text-lg text-[#d70018] dark:text-red-400 font-black font-mono">
                {new Intl.NumberFormat('vi-VN').format(finalCheckoutAmount)}₫
              </span>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-[#d70018] hover:bg-[#b91c1c] disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white font-bold rounded-xl text-sm flex items-center justify-center space-x-2 transition shadow-sm active:scale-95"
            >
              <span>{loading ? 'Đang xác thực và giữ hàng...' : 'Xác nhận đặt hàng ngay'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center justify-center space-x-1.5 text-[11px] text-slate-500 dark:text-slate-400 pt-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-red-400" />
            <span>Hệ thống tự động khóa và giữ hàng trong kho ngay khi bấm đặt</span>
          </div>
        </form>
      </div>
    </div>
  );
};
