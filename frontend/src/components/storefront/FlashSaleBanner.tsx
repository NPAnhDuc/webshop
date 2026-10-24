import { OptimizedImage } from '../common/OptimizedImage';
import React, { useState, useEffect } from 'react';
import { Flame, Timer, Sparkles, ArrowRight, ShieldCheck, Zap, RotateCcw, Award, ShoppingCart, ChevronRight } from 'lucide-react';
import { Product } from '../../types';
import { useLanguage } from '../../context/LanguageContext';
import { useCart } from '../../context/CartContext';
import { sound } from '../../utils/sound';

interface FlashSaleBannerProps {
  products?: Product[];
  onSelectProduct?: (product: Product) => void;
  onAskBot?: (product?: Product) => void;
  onExploreDeals?: () => void;
}

export const FlashSaleBanner: React.FC<FlashSaleBannerProps> = ({
  products = [],
  onSelectProduct,
  onAskBot,
  onExploreDeals
}) => {
  const { lang, t } = useLanguage();
  const { addToCart } = useCart();
  const [activeTab, setActiveTab] = useState<'all' | 'laptop' | 'component'>('all');

  // Live countdown timer state (hours, minutes, seconds)
  const [timeLeft, setTimeLeft] = useState({
    hours: 2,
    minutes: 45,
    seconds: 18
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 };
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: 59, seconds: 59 };
        } else if (prev.hours > 0) {
          return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        }
        return prev;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Filter 4-5 real hot flash sale products
  const flashProducts = products.filter(p => {
    if (activeTab === 'laptop') return p.categorySlug === 'laptop';
    if (activeTab === 'component') return p.categorySlug !== 'laptop';
    return (p.discountPercent && p.discountPercent > 0) || p.isHot;
  }).slice(0, 5);

  return (
    <div id="section-flash-sale" className="relative scroll-mt-24 overflow-hidden bg-gradient-to-r from-red-600 via-rose-600 to-amber-600 dark:from-[#1a0808] dark:via-[#260e0e] dark:to-[#18110b] rounded-3xl p-4 sm:p-6 text-white shadow-xl mb-8 border border-red-500/30 dark:border-rose-900/50 select-none">
      {/* Background Subtle Flame Aura */}
      <div className="absolute -top-20 -left-20 w-72 h-72 bg-red-400/20 dark:bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-amber-400/20 dark:bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header: Title, Live Countdown & Filter Tabs */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-white/20 dark:border-white/10 gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-white text-red-600 px-3 py-1 rounded-full font-black text-xs uppercase tracking-wider shadow-sm animate-pulse">
            <Flame className="w-4 h-4 fill-red-600" />
            <span>FLASH SALE GIỜ VÀNG</span>
          </div>

          {/* Countdown Clock */}
          <div className="flex items-center space-x-1.5 text-xs font-bold text-white/90">
            <Timer className="w-4 h-4 text-yellow-300" />
            <span className="hidden sm:inline">KẾT THÚC SAU:</span>
            <div className="flex items-center space-x-1 font-mono font-black text-sm">
              <span className="bg-black/50 backdrop-blur-md px-2 py-0.5 rounded text-yellow-300 border border-white/10">
                {String(timeLeft.hours).padStart(2, '0')}
              </span>
              <span>:</span>
              <span className="bg-black/50 backdrop-blur-md px-2 py-0.5 rounded text-yellow-300 border border-white/10">
                {String(timeLeft.minutes).padStart(2, '0')}
              </span>
              <span>:</span>
              <span className="bg-black/50 backdrop-blur-md px-2 py-0.5 rounded text-yellow-300 border border-white/10">
                {String(timeLeft.seconds).padStart(2, '0')}
              </span>
            </div>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex items-center space-x-1 self-start md:self-auto">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1 rounded-xl text-xs font-bold transition cursor-pointer ${
              activeTab === 'all'
                ? 'bg-white text-red-600 shadow-sm'
                : 'bg-black/20 hover:bg-black/30 text-white/90'
            }`}
          >
            Tất cả deal sốc
          </button>
          <button
            onClick={() => setActiveTab('laptop')}
            className={`px-3 py-1 rounded-xl text-xs font-bold transition cursor-pointer ${
              activeTab === 'laptop'
                ? 'bg-white text-red-600 shadow-sm'
                : 'bg-black/20 hover:bg-black/30 text-white/90'
            }`}
          >
            Laptop Gaming
          </button>
          <button
            onClick={() => setActiveTab('component')}
            className={`px-3 py-1 rounded-xl text-xs font-bold transition cursor-pointer ${
              activeTab === 'component'
                ? 'bg-white text-red-600 shadow-sm'
                : 'bg-black/20 hover:bg-black/30 text-white/90'
            }`}
          >
            Linh kiện PC
          </button>
        </div>
      </div>

      {/* Real Flash Sale Product Grid */}
      <div className="relative z-10 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-4">
        {flashProducts.map((p, idx) => {
          const discountPct = p.discountPercent || 15;
          const soldCount = 12 + (idx * 3) % 12;
          const totalSlot = 20;
          const soldPct = Math.min(95, Math.round((soldCount / totalSlot) * 100));

          return (
            <div
              key={p.id}
              onClick={() => onSelectProduct && onSelectProduct(p)}
              className="bg-white dark:bg-[#151c2c] rounded-2xl p-2.5 sm:p-3 text-slate-800 dark:text-slate-100 flex flex-col justify-between hover:shadow-2xl transition-all duration-300 group cursor-pointer border border-transparent dark:border-slate-800/80 relative"
            >
              {/* Discount Ribbon Badge */}
              <div className="absolute top-2 left-2 z-20 flex flex-col gap-1 items-start">
                <span className="bg-red-600 text-white text-[10px] font-black px-1.5 py-0.5 rounded shadow-sm">
                  -{discountPct}%
                </span>
                {p.hasInstallment0 && (
                  <span className="bg-blue-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow-xs hidden sm:inline-block">
                    0%
                  </span>
                )}
              </div>

              {/* Product Image */}
              <div className="aspect-square bg-slate-50 dark:bg-slate-900/60 rounded-xl p-2 flex items-center justify-center overflow-hidden mb-2">
                <img
                  src={p.imageUrl}
                  alt={p.name}
                  className="max-h-full max-w-full object-contain group-hover:scale-110 transition-transform duration-300"
                  loading="lazy"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80';
                  }}
                />
              </div>

              {/* Product Details */}
              <div className="space-y-1.5 flex-1 flex flex-col justify-between">
                <div>
                  <h4 className="text-xs font-bold line-clamp-2 leading-snug group-hover:text-red-600 dark:group-hover:text-red-400 transition" title={p.name}>
                    {p.name}
                  </h4>
                  <div className="mt-1 flex items-baseline space-x-1.5">
                    <span className="text-xs sm:text-sm font-black text-red-600 dark:text-rose-400 font-mono">
                      {new Intl.NumberFormat('vi-VN').format(p.price)}₫
                    </span>
                    {p.originalPrice && (
                      <span className="text-[10px] text-slate-400 line-through font-mono hidden sm:inline">
                        {new Intl.NumberFormat('vi-VN').format(p.originalPrice)}₫
                      </span>
                    )}
                  </div>
                </div>

                {/* Progress Bar: Đã bán X / Y suất */}
                <div className="space-y-1 pt-1">
                  <div className="w-full bg-gray-150 dark:bg-slate-800 h-3 rounded-full overflow-hidden relative">
                    <div
                      className="bg-gradient-to-r from-red-600 to-amber-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${soldPct}%` }}
                    />
                    <span className="absolute inset-0 flex items-center justify-center text-[9px] font-black text-white drop-shadow-xs uppercase">
                      Đã bán {soldCount}/{totalSlot}
                    </span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      addToCart(p);
                      sound.playCartAdd();
                    }}
                    className="w-full py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-[11px] font-bold flex items-center justify-center space-x-1 transition shadow-xs active:scale-95 cursor-pointer mt-1"
                  >
                    <ShoppingCart className="w-3 h-3" />
                    <span>Mua Ngay</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
