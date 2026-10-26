import React, { useState } from 'react';
import {
  X,
  Trash2,
  ArrowRight,
  ShoppingBag,
  ShieldCheck,
  Tag,
  Sparkles,
  CheckCircle2,
  Truck,
  Plus
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { triggerConfetti } from '../../utils/confetti';
import { sound } from '../../utils/sound';
import { Product } from '../../types';

interface CartDrawerProps {
  onProceedToCheckout: () => void;
}

const FREESHIP_THRESHOLD = 500000; // 500,000 VND

const UPSELL_ACCESSORIES = [
  {
    id: 'upsell-pad',
    name: 'Lót chuột Gaming Speed Pad 80x30cm',
    price: 49000,
    originalPrice: 99000,
    imageUrl: 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=120&auto=format&fit=crop&q=80'
  },
  {
    id: 'upsell-paste',
    name: 'Keo tản nhiệt Arctic MX-4 (4g) chính hãng',
    price: 89000,
    originalPrice: 150000,
    imageUrl: 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80'
  },
  {
    id: 'upsell-hdmi',
    name: 'Cáp HDMI 2.1 8K 60Hz bọc dù chống đứt',
    price: 120000,
    originalPrice: 190000,
    imageUrl: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=120&auto=format&fit=crop&q=80'
  }
];

export const CartDrawer: React.FC<CartDrawerProps> = ({ onProceedToCheckout }) => {
  const { cart, isOpen, closeCart, removeFromCart, updateQty, totalAmount, totalItems, addToCart } = useCart();
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState<{ code: string; discount: number; label: string } | null>(null);
  const [couponError, setCouponError] = useState<string | null>(null);

  if (!isOpen) return null;

  const freeshipProgress = Math.min(100, Math.round((totalAmount / FREESHIP_THRESHOLD) * 100));
  const freeshipRemaining = Math.max(0, FREESHIP_THRESHOLD - totalAmount);

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

  const handleAddUpsell = (acc: typeof UPSELL_ACCESSORIES[0]) => {
    const dummyProduct: Product = {
      id: acc.id,
      name: acc.name,
      slug: acc.id,
      brandId: 'b-techstore',
      brandName: 'TechStore Gear',
      categoryId: 'cat-acc',
      categorySlug: 'accessories' as any,
      price: acc.price,
      originalPrice: acc.originalPrice,
      imageUrl: acc.imageUrl,
      images: [acc.imageUrl],
      description: acc.name,
      highlights: ['Chính hãng 100%', 'Bảo hành 12 tháng'],
      status: 'active',
      createdAt: new Date().toISOString(),
      stockStatus: { status: 'in_stock', availableQty: 99 },
      variants: [
        {
          id: `var-${acc.id}`,
          productId: acc.id,
          sku: `SKU-${acc.id.toUpperCase()}`,
          name: 'Tiêu chuẩn',
          price: acc.price,
          originalPrice: acc.originalPrice,
          costPrice: acc.price * 0.7,
          status: 'active'
        }
      ],
      specs: {}
    };

    addToCart(dummyProduct, dummyProduct.variants[0], 1);
    sound.playPop();
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
              <ShoppingBag className="w-5 h-5 text-[#d70018] dark:text-red-400" />
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

          {/* Freeship Progress Bar Callout */}
          {cart.length > 0 && (
            <div className="bg-red-50/60 dark:bg-slate-900/90 px-4 py-3 border-b border-red-100 dark:border-slate-800">
              <div className="flex items-center justify-between text-xs mb-1.5 font-medium">
                <span className="flex items-center space-x-1.5 text-slate-700 dark:text-slate-300">
                  <Truck className="w-4 h-4 text-[#d70018]" />
                  {freeshipRemaining > 0 ? (
                    <span>
                      Mua thêm <strong className="font-mono font-bold text-[#d70018]">{new Intl.NumberFormat('vi-VN').format(freeshipRemaining)}₫</strong> để được <strong>FREESHIP</strong>
                    </span>
                  ) : (
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Đủ điều kiện FREESHIP TOÀN QUỐC!</span>
                    </span>
                  )}
                </span>
                <span className="font-mono font-bold text-[11px] text-slate-500">{freeshipProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 rounded-full ${
                    freeshipProgress >= 100 ? 'bg-emerald-500' : 'bg-gradient-to-r from-red-500 to-[#d70018]'
                  }`}
                  style={{ width: `${freeshipProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
            {cart.length === 0 ? (
              <div className="text-center py-16 space-y-3">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto text-slate-400 dark:text-slate-500">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">Giỏ hàng của bạn đang trống</p>
                <p className="text-xs text-slate-400 dark:text-slate-500">Hãy dạo một vòng và chọn chiếc laptop hoặc linh kiện ưng ý nhé!</p>
                <button
                  onClick={closeCart}
                  className="mt-4 px-4 py-2 bg-[#d70018] hover:bg-[#b91c1c] text-white text-xs font-semibold rounded-lg transition cursor-pointer shadow-xs active:scale-95"
                >
                  Khám phá sản phẩm
                </button>
              </div>
            ) : (
              <>
                {cart.map(item => (
                  <div
                    key={item.variantId}
                    className="flex space-x-3 p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/60 hover:bg-slate-50 dark:hover:bg-slate-900/80 transition"
                  >
                    <img
                      src={item.imageUrl}
                      alt={item.productName}
                      className="w-16 h-16 object-contain rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-1 flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0 flex flex-col justify-between">
                      <div>
                        <div className="flex justify-between items-start">
                          <h3 className="text-xs font-bold text-slate-900 dark:text-slate-100 truncate pr-2" title={item.productName}>
                            {item.productName}
                          </h3>
                          <button
                            onClick={() => removeFromCart(item.variantId)}
                            className="text-slate-400 hover:text-red-500 transition cursor-pointer p-0.5"
                            title="Xóa khỏi giỏ"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                          {item.variantName}
                        </p>
                      </div>

                      <div className="flex justify-between items-center mt-2">
                        <div className="flex items-center space-x-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 px-2 py-0.5">
                          <button
                            onClick={() => updateQty(item.variantId, item.qty - 1)}
                            className="text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 font-bold px-1"
                          >
                            -
                          </button>
                          <span className="text-xs font-semibold w-4 text-center">{item.qty}</span>
                          <button
                            onClick={() => updateQty(item.variantId, item.qty + 1)}
                            className="text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 font-bold px-1"
                          >
                            +
                          </button>
                        </div>
                        <span className="text-xs font-black text-[#d70018] dark:text-red-400 font-mono">
                          {new Intl.NumberFormat('vi-VN').format(item.price * item.qty)}₫
                        </span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Quick Upsell Accessories section */}
                <div className="pt-3 border-t border-slate-200 dark:border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-extrabold uppercase text-[11px] text-slate-500 dark:text-slate-400 flex items-center space-x-1">
                      <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                      <span>Gợi ý mua kèm ưu đãi</span>
                    </span>
                    <span className="text-[10px] text-red-500 font-semibold">Freeship ngay</span>
                  </div>

                  <div className="space-y-2">
                    {UPSELL_ACCESSORIES.map(acc => (
                      <div
                        key={acc.id}
                        className="p-2 rounded-xl bg-gray-50 dark:bg-slate-900/40 border border-gray-150 dark:border-slate-800 flex items-center justify-between gap-3 text-xs"
                      >
                        <div className="flex items-center space-x-2.5 min-w-0">
                          <img
                            src={acc.imageUrl}
                            alt={acc.name}
                            className="w-10 h-10 object-cover rounded-lg border border-gray-200 dark:border-slate-700 flex-shrink-0"
                          />
                          <div className="min-w-0">
                            <p className="font-bold text-slate-800 dark:text-slate-200 truncate text-[11px]" title={acc.name}>
                              {acc.name}
                            </p>
                            <div className="flex items-baseline space-x-1.5">
                              <span className="font-mono font-black text-[#d70018] text-xs">
                                {new Intl.NumberFormat('vi-VN').format(acc.price)}₫
                              </span>
                              <span className="font-mono text-[10px] text-slate-400 line-through">
                                {new Intl.NumberFormat('vi-VN').format(acc.originalPrice)}₫
                              </span>
                            </div>
                          </div>
                        </div>

                        <button
                          onClick={() => handleAddUpsell(acc)}
                          className="px-2.5 py-1 bg-white dark:bg-slate-800 hover:bg-[#d70018] hover:text-white dark:hover:bg-[#d70018] text-[#d70018] border border-red-200 dark:border-slate-700 rounded-lg font-bold text-[11px] flex items-center space-x-1 transition cursor-pointer shadow-2xs flex-shrink-0 active:scale-95"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Thêm</span>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Footer & Checkout Callout */}
          {cart.length > 0 && (
            <div className="p-4 sm:p-5 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 space-y-3">
              {/* Voucher Input */}
              <div className="space-y-1.5">
                {!appliedCoupon ? (
                  <>
                    <div className="flex space-x-2">
                      <div className="relative flex-1">
                        <Tag className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                        <input
                          type="text"
                          value={couponCode}
                          onChange={e => setCouponCode(e.target.value)}
                          placeholder="Nhập mã ưu đãi..."
                          className="w-full pl-8 pr-3 py-1.5 border border-slate-200 dark:border-slate-700 rounded-lg text-xs bg-white dark:bg-slate-800 uppercase"
                        />
                      </div>
                      <button
                        onClick={() => handleApplyCoupon()}
                        className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition cursor-pointer"
                      >
                        Áp dụng
                      </button>
                    </div>

                    {/* Quick Voucher Suggestion Pills */}
                    <div className="flex flex-wrap gap-1 pt-1">
                      <button
                        onClick={() => handleApplyCoupon('TECH500')}
                        className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-200 cursor-pointer"
                      >
                        Mã TECH500 (-500k)
                      </button>
                      <button
                        onClick={() => handleApplyCoupon('GAMING2026')}
                        className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-200 cursor-pointer"
                      >
                        Mã GAMING2026 (-3%)
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="flex items-center justify-between text-xs bg-slate-100 dark:bg-slate-800/80 p-2 rounded-lg border border-slate-200 dark:border-slate-700">
                    <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#d70018]" />
                      <span>{appliedCoupon.code}: {appliedCoupon.label}</span>
                    </span>
                    <span className="font-mono font-bold text-[#d70018] dark:text-red-400">
                      -{new Intl.NumberFormat('vi-VN').format(appliedCoupon.discount)}₫
                    </span>
                  </div>
                )}

                {couponError && (
                  <p className="text-[11px] text-red-500 font-medium">{couponError}</p>
                )}
              </div>

              {/* Price Calculation */}
              <div className="space-y-1.5 pt-2 border-t border-slate-200 dark:border-slate-800 text-xs">
                <div className="flex justify-between text-slate-500 dark:text-slate-400">
                  <span>Tạm tính ({totalItems} món):</span>
                  <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                    {new Intl.NumberFormat('vi-VN').format(totalAmount)}₫
                  </span>
                </div>
                {appliedCoupon && (
                  <div className="flex justify-between text-[#d70018] dark:text-red-400">
                    <span>Ưu đãi voucher:</span>
                    <span className="font-mono font-bold">
                      -{new Intl.NumberFormat('vi-VN').format(appliedCoupon.discount)}₫
                    </span>
                  </div>
                )}
                <div className="flex justify-between text-slate-500 dark:text-slate-400">
                  <span>Phí vận chuyển:</span>
                  <span className="font-semibold text-emerald-600 dark:text-emerald-400 font-mono">
                    {freeshipRemaining === 0 ? 'MIỄN PHÍ' : 'Tính khi thanh toán'}
                  </span>
                </div>
                <div className="flex justify-between text-sm pt-1 border-t border-slate-200 dark:border-slate-800">
                  <span className="font-bold text-slate-900 dark:text-slate-100">Tổng thanh toán:</span>
                  <span className="font-black text-base font-mono text-[#d70018] dark:text-red-400">
                    {new Intl.NumberFormat('vi-VN').format(finalAmount)}₫
                  </span>
                </div>
              </div>

              {/* Checkout CTA */}
              <button
                onClick={() => {
                  closeCart();
                  onProceedToCheckout();
                }}
                className="w-full py-3 bg-[#d70018] hover:bg-[#b91c1c] text-white font-bold rounded-xl text-xs sm:text-sm flex items-center justify-center space-x-2 transition shadow-lg shadow-red-600/20 active:scale-95 cursor-pointer"
              >
                <span>Tiến hành đặt hàng ngay</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="flex items-center justify-center space-x-4 text-[10px] text-slate-400 dark:text-slate-500 pt-1">
                <span className="flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Bảo mật 100%</span>
                </span>
                <span>•</span>
                <span>Đổi mới 30 ngày</span>
                <span>•</span>
                <span>Hỗ trợ trả góp 0%</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
