import React from 'react';
import { Home, LayoutGrid, SlidersHorizontal, Heart, ShoppingCart } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useWishlist } from '../../context/WishlistContext';
import { sound } from '../../utils/sound';

interface MobileBottomNavProps {
  currentView: string;
  onNavigateHome: () => void;
  onNavigatePCBuilder: () => void;
  onOpenCategories: () => void;
  onToggleWishlist: () => void;
  isWishlistActive?: boolean;
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  currentView,
  onNavigateHome,
  onNavigatePCBuilder,
  onOpenCategories,
  onToggleWishlist,
  isWishlistActive = false
}) => {
  const { openCart, totalItems } = useCart();
  const { count: wishlistCount } = useWishlist();

  // If on product detail page, hide the bottom navigation to give full screen focus to product buy actions
  if (currentView === 'product-detail') {
    return null;
  }

  const isHomeActive = currentView === 'storefront' && !isWishlistActive;
  const isPCBuilderActive = currentView === 'pc-builder';

  return (
    <nav
      aria-label="Điều hướng nhanh di động"
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-[#0f172a]/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 shadow-[0_-4px_20px_rgba(0,0,0,0.08)] px-2 py-1.5"
      style={{ paddingBottom: 'calc(0.375rem + env(safe-area-inset-bottom, 0px))' }}
    >
      <div className="grid grid-cols-5 items-center">
        {/* 1. Trang Chủ */}
        <button
          onClick={() => {
            sound.playPop();
            onNavigateHome();
          }}
          className={`flex flex-col items-center justify-center py-1 transition cursor-pointer ${
            isHomeActive
              ? 'text-[#d70018] dark:text-red-400 font-bold'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <Home className="w-5 h-5 mb-0.5" />
          <span className="text-[10px] leading-tight">Trang chủ</span>
        </button>

        {/* 2. Danh Mục */}
        <button
          onClick={() => {
            sound.playPop();
            onOpenCategories();
          }}
          className="flex flex-col items-center justify-center py-1 transition cursor-pointer text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
        >
          <LayoutGrid className="w-5 h-5 mb-0.5" />
          <span className="text-[10px] leading-tight">Danh mục</span>
        </button>

        {/* 3. Tự Ráp PC (Highlight center button) */}
        <button
          onClick={() => {
            sound.playPop();
            onNavigatePCBuilder();
          }}
          className={`flex flex-col items-center justify-center py-1 transition cursor-pointer ${
            isPCBuilderActive
              ? 'text-[#d70018] dark:text-red-400 font-bold'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <div className="relative">
            <SlidersHorizontal className="w-5 h-5 mb-0.5 text-amber-500" />
            <span className="absolute -top-1 -right-2 w-2 h-2 rounded-full bg-red-600 animate-ping" />
          </div>
          <span className="text-[10px] leading-tight">Tự Ráp PC</span>
        </button>

        {/* 4. Yêu Thích */}
        <button
          onClick={() => {
            sound.playPop();
            onToggleWishlist();
          }}
          className={`flex flex-col items-center justify-center py-1 transition cursor-pointer relative ${
            isWishlistActive
              ? 'text-rose-600 font-bold'
              : 'text-slate-500 dark:text-slate-400 hover:text-rose-500'
          }`}
        >
          <div className="relative">
            <Heart className={`w-5 h-5 mb-0.5 ${isWishlistActive || wishlistCount > 0 ? 'fill-rose-500 text-rose-500' : ''}`} />
            {wishlistCount > 0 && (
              <span className="absolute -top-1 -right-2 bg-rose-600 text-white font-mono font-black text-[9px] w-4 h-4 rounded-full flex items-center justify-center">
                {wishlistCount}
              </span>
            )}
          </div>
          <span className="text-[10px] leading-tight">Yêu thích</span>
        </button>

        {/* 5. Giỏ Hàng */}
        <button
          onClick={() => {
            sound.playPop();
            openCart();
          }}
          className="flex flex-col items-center justify-center py-1 transition cursor-pointer text-slate-500 dark:text-slate-400 hover:text-[#d70018] dark:hover:text-red-400 relative"
        >
          <div className="relative">
            <ShoppingCart className="w-5 h-5 mb-0.5" />
            {totalItems > 0 && (
              <span className="absolute -top-1 -right-2.5 bg-[#d70018] text-white font-mono font-black text-[9px] min-w-4 h-4 px-1 rounded-full flex items-center justify-center shadow-xs">
                {totalItems}
              </span>
            )}
          </div>
          <span className="text-[10px] leading-tight">Giỏ hàng</span>
        </button>
      </div>
    </nav>
  );
};
