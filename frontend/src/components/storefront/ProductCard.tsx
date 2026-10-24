import { OptimizedImage } from '../common/OptimizedImage';
import React from 'react';
import { ShoppingCart, Eye, Sparkles, CheckCircle2, AlertTriangle, XCircle, CheckSquare, Square, Star, Award, Heart } from 'lucide-react';
import { Product } from '../../types';
import { useCart } from '../../context/CartContext';
import { useLanguage } from '../../context/LanguageContext';
import { useWishlist } from '../../context/WishlistContext';

interface ProductCardProps {
  product: Product;
  onSelect: (product: Product) => void;
  onAskBot?: (product: Product) => void;
  isComparing?: boolean;
  onToggleCompare?: (product: Product) => void;
  onAddToCartToast?: (productName: string) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onSelect,
  onAskBot,
  isComparing = false,
  onToggleCompare,
  onAddToCartToast
}) => {
  const { addToCart } = useCart();
  const { t, lang } = useLanguage();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const wishlisted = isWishlisted(product.id);
  const stock = product.stockStatus;
  const isOutOfStock = stock?.status === 'out_of_stock';
  const isLowStock = stock?.status === 'low_stock';

  const handleAddToCart = () => {
    addToCart(product);
    if (onAddToCartToast) {
      onAddToCartToast(product.name);
    }
  };

  return (
    <div className="group bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 hover:shadow-lg transition-all duration-200 flex flex-col justify-between overflow-hidden relative rounded-2xl text-slate-800 dark:text-slate-100 p-3 select-none">
      {/* 1. Status Badges at Top Left (z-30 to guarantee never covered by images) */}
      <div className="absolute top-2.5 left-2.5 z-30 flex flex-col gap-1 items-start pointer-events-none">
        {product.discountPercent && product.discountPercent > 0 && (
          <span className="bg-[#d70018] text-white text-[10px] font-black px-1.5 py-0.5 rounded shadow-sm">
            {lang === 'vi' ? 'Giảm' : 'Save'} {product.discountPercent}%
          </span>
        )}
        {product.hasInstallment0 && (
          <span className="bg-blue-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm">
            {t('installment0')}
          </span>
        )}
        {product.isHot && (
          <span className="bg-slate-900 text-amber-400 text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded shadow-sm border border-slate-700">
            HOT
          </span>
        )}
      </div>

      {/* Action Buttons in Top Right (z-30) */}
      <div className="absolute top-2.5 right-2.5 z-30 flex items-center space-x-1">
        {/* Wishlist Heart Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleWishlist(product.id);
          }}
          className={`p-1.5 rounded-lg border transition cursor-pointer ${
            wishlisted
              ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-800 text-rose-500 shadow-xs'
              : 'bg-white/90 dark:bg-slate-800/90 border-gray-200 dark:border-slate-700 text-slate-400 hover:text-rose-500 hover:border-rose-200'
          }`}
          title={wishlisted ? (lang === 'vi' ? 'Bỏ yêu thích' : 'Remove wishlist') : (lang === 'vi' ? 'Thêm vào yêu thích' : 'Add to wishlist')}
        >
          <Heart className={`w-3.5 h-3.5 transition-transform active:scale-125 ${wishlisted ? 'fill-rose-500 text-rose-500' : ''}`} />
        </button>

        {/* Compare Checkbox Icon */}
        {onToggleCompare && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleCompare(product);
            }}
            className={`p-1.5 rounded-lg border transition cursor-pointer ${
              isComparing
                ? 'bg-slate-900 border-slate-900 text-white shadow-xs'
                : 'bg-white/90 dark:bg-slate-800/90 border-gray-200 dark:border-slate-700 text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:border-gray-300'
            }`}
            title={isComparing ? (lang === 'vi' ? 'Bỏ chọn so sánh' : 'Remove compare') : (lang === 'vi' ? 'Chọn so sánh' : 'Compare')}
          >
            {isComparing ? (
              <CheckSquare className="w-3.5 h-3.5 text-white" />
            ) : (
              <Square className="w-3.5 h-3.5" />
            )}
          </button>
        )}
      </div>

      {/* 2. Product Image Chamber (Clean Pure White / Dark Slate) */}
      <div
        onClick={() => onSelect(product)}
        className="cursor-pointer relative aspect-square p-2 bg-white dark:bg-slate-900/60 rounded-xl flex items-center justify-center overflow-hidden z-0"
      >
        <OptimizedImage
          src={product.imageUrl}
          alt={product.name}
          aspectRatio="square"
          className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300 drop-shadow-xs mix-blend-multiply dark:mix-blend-normal"
        />

        {/* Quick view on hover */}
        <div className="absolute inset-0 bg-slate-900/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center z-20">
          <span className="bg-white/95 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-[11px] font-bold px-3 py-1 rounded-full shadow-md border border-gray-200 dark:border-slate-700 flex items-center space-x-1 hover:text-[#d70018] dark:hover:text-red-400 transition">
            <Eye className="w-3.5 h-3.5 text-[#d70018] dark:text-red-400" />
            <span>{lang === 'vi' ? 'Xem nhanh' : 'Quick View'}</span>
          </span>
        </div>
      </div>

      {/* 3. Product Info */}
      <div className="pt-2 flex-1 flex flex-col justify-between space-y-2.5">
        <div>
          {/* Brand & Category */}
          <div className="flex items-center justify-between text-[11px] mb-1">
            <span className="font-extrabold text-[#d70018] dark:text-red-400 uppercase tracking-wider">{product.brandName}</span>
            <span className="uppercase text-slate-400 dark:text-slate-500 font-semibold text-[10px]">{product.categorySlug}</span>
          </div>

          {/* Name */}
          <h3
            onClick={() => onSelect(product)}
            className="text-xs sm:text-sm font-bold text-slate-800 dark:text-slate-100 line-clamp-2 group-hover:text-[#d70018] dark:group-hover:text-red-400 cursor-pointer min-h-[38px] transition leading-snug"
            title={product.name}
          >
            {product.name}
          </h3>

          {/* Tech Spec Badges (Clean neutral professional look) */}
          <div className="mt-2 flex flex-wrap gap-1">
            {product.specs.panel && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                product.specs.panel === 'OLED'
                  ? 'bg-slate-900 text-amber-400 border border-slate-700'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
              }`}>
                {product.specs.panel} {product.specs.refresh_hz ? `${product.specs.refresh_hz}Hz` : ''}
              </span>
            )}
            {product.specs.cpu_model && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-medium">
                {product.specs.cpu_model}
              </span>
            )}
            {product.specs.socket && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-bold">
                {product.specs.socket}
              </span>
            )}
            {product.specs.vram_gb && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-bold">
                {product.specs.vram_gb}GB VRAM
              </span>
            )}
            {product.specs.storage_gb && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-medium">
                {product.specs.storage_gb >= 1000 ? `${product.specs.storage_gb / 1000}TB` : `${product.specs.storage_gb}GB`} SSD
              </span>
            )}
            {product.specs.cores && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-bold">
                {product.specs.cores} Cores
              </span>
            )}
            {product.specs.chipset && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-bold">
                {product.specs.chipset}
              </span>
            )}
            {product.specs.ram_gb && (
              <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded font-medium">
                {product.specs.ram_gb}GB {product.specs.ram_type || ''}
              </span>
            )}
          </div>
        </div>

        {/* 4. Price & T-Member Perk */}
        <div className="pt-2 border-t border-gray-100 dark:border-slate-800 space-y-1.5">
          {/* Price */}
          <div className="flex items-baseline space-x-2">
            <span className="text-base sm:text-lg font-black text-[#d70018] dark:text-red-400 font-mono">
              {new Intl.NumberFormat('vi-VN').format(product.price)}₫
            </span>
            {product.originalPrice && product.originalPrice > product.price && (
              <span className="text-xs text-slate-400 dark:text-slate-500 line-through font-mono">
                {new Intl.NumberFormat('vi-VN').format(product.originalPrice)}₫
              </span>
            )}
          </div>

          {/* Promotion Gift Note Box */}
          <div className="bg-red-50/70 dark:bg-red-950/30 border border-red-200/80 dark:border-red-900/40 rounded-lg px-2 py-1 text-[10px] text-red-800 dark:text-red-300 line-clamp-1">
            <strong className="text-[#d70018] dark:text-red-400">[KM]</strong> {lang === 'vi' ? 'Tặng Balo Gaming + Chuột không dây + Gói bảo dưỡng PC' : 'Free Gaming Backpack + Wireless Mouse + Free Maintenance'}
          </div>

          {/* Smember / T-Member Cashback Tag */}
          <div className="bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 flex items-center space-x-1.5 text-[10px] text-slate-700 dark:text-slate-300 font-semibold">
            <Award className="w-3.5 h-3.5 text-slate-600 dark:text-slate-400 flex-shrink-0" />
            <span className="truncate">{t('tMemberPerk')}</span>
          </div>

          {/* Star rating & Stock status */}
          <div className="flex items-center justify-between text-[11px] pt-1">
            <div className="flex items-center space-x-1 text-amber-500 font-bold">
              <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
              <span>4.9</span>
              <span className="text-slate-400 dark:text-slate-500 font-normal text-[10px]">(48)</span>
            </div>

            {isOutOfStock ? (
              <span className="text-slate-400 dark:text-slate-500 font-medium flex items-center space-x-1">
                <XCircle className="w-3.5 h-3.5" />
                <span>{t('outOfStock')}</span>
              </span>
            ) : isLowStock ? (
              <span className="text-amber-600 dark:text-amber-400 font-semibold flex items-center space-x-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>{lang === 'vi' ? `Còn ${stock?.availableQty} máy` : `${stock?.availableQty} left`}</span>
              </span>
            ) : (
              <span className="text-slate-700 dark:text-slate-300 font-semibold flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-slate-500" />
                <span>{lang === 'vi' ? 'Sẵn hàng tại HN & HCM' : t('inStock')}</span>
              </span>
            )}
          </div>

          {/* Buy Button */}
          <div className="pt-1 flex items-center space-x-1.5">
            {isOutOfStock ? (
              <button
                disabled
                className="w-full py-2 bg-gray-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 text-xs font-semibold rounded-xl cursor-not-allowed text-center border border-gray-200 dark:border-slate-700"
              >
                {t('outOfStock')}
              </button>
            ) : (
              <>
                <button
                  onClick={handleAddToCart}
                  className="flex-1 py-2 px-3 bg-[#d70018] hover:bg-[#b91c1c] text-white text-xs font-bold rounded-xl flex items-center justify-center space-x-1.5 transition shadow-xs active:scale-95 cursor-pointer"
                >
                  <ShoppingCart className="w-3.5 h-3.5" />
                  <span>{t('buyNow')}</span>
                </button>
                {onAskBot && (
                  <button
                    onClick={() => onAskBot(product)}
                    title={t('askAIConsult')}
                    className="p-2 border border-gray-200 dark:border-slate-700 hover:border-red-500 dark:hover:border-red-500 text-slate-500 dark:text-slate-400 hover:text-[#d70018] dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer"
                  >
                    <Sparkles className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
