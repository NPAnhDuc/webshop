import React, { useState } from 'react';
import { X, Trash2, ArrowRight, ShoppingBag, ShieldCheck, Tag, Sparkles, CheckCircle2 } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { triggerConfetti } from '../../utils/confetti';
import { sound } from '../../utils/sound';

interface CartDrawerProps {
  onProceedToCheckout: () => void;
}

export const CartDrawer: React.FC<CartDrawerProps> = ({ onProceedToCheckout }) => {
  const { cart, isOpen, closeCart, removeFromCart, updateQty, totalAmount, totalItems } = useCart();
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState<{ code: string; discount: number; label: string } | null>(null);
  const [couponError, setCouponError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleApplyCoupon = (codeToApply?: string) => {
    const code = (codeToApply || couponCode).trim().toUpperCase();
    setCouponError(null);

    if (code === 'TECH500') {
      if (totalAmount < 10000000) {
        setCouponError('Mã TECH500 áp dụng cho đơn hàng từ 10.000.000₫');
        return;
      }
      setAppliedCoupon({ code: 'TECH500', discount: 500000, label: 'Giảm ngay 500.000₫' });
      triggerConfetti();
      sound.playVoucherSuccess();
    } else if (code === 'GAMING2026') {
      const discount = Math.min(1000000, Math.round(totalAmount * 0.03));
      setAppliedCoupon({ code: 'GAMING2026', discount, label: 'Ưu đãi Gaming - Giảm 3%' });
      triggerConfetti();
      sound.playVoucherSuccess();
    } else if (code === 'FREESHIP') {
      setAppliedCoupon({ code: 'FREESHIP', discount: 0, label: 'Miễn phí vận chuyển hỏa tốc toàn quốc' });
      triggerConfetti();
      sound.playVoucherSuccess();
    } else {
      setCouponError('Mã giảm giá không hợp lệ hoặc đã hết lượt.');
    }
  };

  const finalAmount = appliedCoupon ? Math.max(0, totalAmount - appliedCoupon.discount) : totalAmount;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-in fade-in duration-200">
      {/* Backdrop */}
      <div
        onClick={closeCart}
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white dark:bg-[#151c2c] shadow-2xl flex flex-col justify-between border-l border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-100 transition-colors">
          {/* Header */}
          <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShoppingBag className="w-5 h-5 text-[#059669] dark:text-emerald-400" />
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Giỏ hàng của bạn ({totalItems})
              </h2>
            </div>
            <button
              onClick={closeCart}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
            {cart.length === 0 ? (
              <div className="text-center py-16 space-y-3">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto text-slate-400 dark:text-slate-500">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">Giỏ hàng của bạn đang trống</p>
                <p className="text-xs text-slate-400 dark:text-slate-500">Hãy dạo một vòng và chọn chiếc laptop ưng ý nhé!</p>
                <button
                  onClick={closeCart}
                  className="mt-4 px-4 py-2 bg-[#059669] hover:bg-[#047857] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition cursor-pointer"
                >
                  Khám phá sản phẩm
                </button>
              </div>
            ) : (
              cart.map(item => (
                <div
                  key={item.variantId}
                  className="flex space-x-3 p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/60 hover:bg-slate-50 dark:hover:bg-slate-900/80 transition"
                >
                  <img
                    src={item.imageUrl}
                    alt={item.productName}
                    className="w-16 h-16 object-contain rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-1 flex-shrink-0"
                  />
                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div>
                      <div className="flex justify-between items-start">
                        <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">
                          {item.productName}
                        </h4>
                        <button
                          onClick={() => removeFromCart(item.variantId)}
                          className="text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition ml-2 cursor-pointer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">{item.variantName}</p>
                    </div>

                    <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-200/60 dark:border-slate-800">
                      {/* Quantity selector */}
                      <div className="flex items-center border border-slate-300 dark:border-slate-700 rounded bg-white dark:bg-slate-800">
                        <button
                          onClick={() => updateQty(item.variantId, item.qty - 1)}
                          className="px-2 py-0.5 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 font-bold cursor-pointer"
                        >
                          -
                        </button>
                        <span className="px-2.5 py-0.5 text-xs font-semibold text-slate-900 dark:text-slate-100">
                          {item.qty}
                        </span>
                        <button
                          onClick={() => updateQty(item.variantId, item.qty + 1)}
                          className="px-2 py-0.5 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 font-bold cursor-pointer"
                        >
                          +
                        </button>
                      </div>

                      <div className="text-right">
                        <span className="text-xs font-bold text-[#059669] dark:text-emerald-400 font-mono">
                          {new Intl.NumberFormat('vi-VN').format(item.price * item.qty)}₫
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer & Checkout Action */}
          {cart.length > 0 && (
            <div className="p-4 sm:p-5 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80 space-y-3">
              {/* Voucher Section */}
              <div className="p-2.5 bg-white dark:bg-[#151c2c] rounded-xl border border-dashed border-emerald-300 dark:border-emerald-700/60 space-y-2">
                <div className="flex items-center justify-between text-xs font-bold text-slate-800 dark:text-slate-200">
                  <div className="flex items-center space-x-1.5 text-[#059669] dark:text-emerald-400">
                    <Tag className="w-3.5 h-3.5" />
                    <span>Mã ưu đãi TechStore</span>
                  </div>
                  {appliedCoupon && (
                    <button
                      onClick={() => setAppliedCoupon(null)}
                      className="text-[11px] text-red-500 hover:underline font-normal cursor-pointer"
                    >
                      Bỏ áp dụng
                    </button>
                  )}
                </div>

                {!appliedCoupon ? (
                  <>
                    <div className="flex space-x-1.5">
                      <input
                        type="text"
                        value={couponCode}
                        onChange={e => setCouponCode(e.target.value.toUpperCase())}
                        placeholder="Nhập mã (VD: TECH500)"
                        className="flex-1 px-2.5 py-1.5 border border-slate-200 dark:border-slate-700 rounded-lg text-xs bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 font-mono focus:outline-none focus:border-[#059669]"
                      />
                      <button
                        onClick={() => handleApplyCoupon()}
                        className="px-3 py-1.5 bg-[#059669] hover:bg-[#047857] text-white rounded-lg text-xs font-bold transition cursor-pointer"
                      >
                        Áp dụng
                      </button>
                    </div>

                    {/* Quick Voucher Suggestion Pills */}
                    <div className="flex flex-wrap gap-1 pt-1">
                      <button
                        onClick={() => handleApplyCoupon('TECH500')}
                        className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 cursor-pointer"
                      >
                        🔥 TECH500 (-500k)
                      </button>
                      <button
                        onClick={() => handleApplyCoupon('GAMING2026')}
                        className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 cursor-pointer"
                      >
                        🎮 GAMING2026 (-3%)
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="flex items-center justify-between text-xs bg-emerald-50 dark:bg-emerald-950/40 p-2 rounded-lg border border-emerald-200 dark:border-emerald-800">
                    <span className="font-bold text-emerald-700 dark:text-emerald-300 flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{appliedCoupon.code}: {appliedCoupon.label}</span>
                    </span>
                    <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      -{new Intl.NumberFormat('vi-VN').format(appliedCoupon.discount)}₫
                    </span>
                  </div>
                )}

                {couponError && (
                  <p className="text-[11px] text-red-500 font-medium">{couponError}</p>
                )}
              </div>

              <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
                <span>Tạm tính hàng hóa:</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">
                  {new Intl.NumberFormat('vi-VN').format(totalAmount)}₫
                </span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
                <span>Phí vận chuyển toàn quốc:</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Miễn phí 100%</span>
              </div>
              {appliedCoupon && appliedCoupon.discount > 0 && (
                <div className="flex items-center justify-between text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
                  <span>Giảm giá từ ưu đãi:</span>
                  <span className="font-mono">-{new Intl.NumberFormat('vi-VN').format(appliedCoupon.discount)}₫</span>
                </div>
              )}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex items-baseline justify-between">
                <span className="text-sm font-bold text-slate-900 dark:text-slate-100">Tổng thanh toán:</span>
                <span className="text-xl font-black text-[#059669] dark:text-emerald-400 font-mono">
                  {new Intl.NumberFormat('vi-VN').format(finalAmount)}₫
                </span>
              </div>

              <div className="pt-1">
                <button
                  onClick={() => {
                    closeCart();
                    onProceedToCheckout();
                  }}
                  className="w-full py-3 bg-[#059669] hover:bg-[#047857] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white font-bold rounded-xl text-sm flex items-center justify-center space-x-2 transition shadow-sm active:scale-95 cursor-pointer"
                >
                  <span>Tiến hành đặt hàng</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center justify-center space-x-1.5 text-[11px] text-slate-500 dark:text-slate-400 pt-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                <span>Kiểm tra & giữ hàng tức thì trong thời gian thực</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
