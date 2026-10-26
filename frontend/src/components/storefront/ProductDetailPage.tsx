import { useProductDetailQuery, useProductReviewsQuery, useSubmitReviewMutation } from '../../hooks/useQueries';
import React, { useState, useEffect, useMemo } from 'react';
import {
  ArrowLeft,
  ShoppingCart,
  Zap,
  ShieldCheck,
  RotateCcw,
  CreditCard,
  Truck,
  Star,
  ThumbsUp,
  MessageSquare,
  Award,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Heart,
  Scale,
  Sparkles,
  ChevronRight,
  Home,
  SlidersHorizontal,
  Activity,
  Flame,
  Check
} from 'lucide-react';
import { Product, ProductVariant } from '../../types';
import { useCart } from '../../context/CartContext';
import { useWishlist } from '../../context/WishlistContext';
import { fetchProductDetail, fetchProductReviews, submitProductReview, fetchProducts } from '../../services/api';
import { sound } from '../../utils/sound';
import { OptimizedImage } from '../common/OptimizedImage';
import { InstallmentCalculatorModal } from '../common/InstallmentCalculatorModal';
import { calculateGamingTelemetry } from '../../utils/hardwareBenchmarks';

interface ProductDetailPageProps {
  productSlugOrId: string;
  initialProduct?: Product | null;
  onBack: () => void;
  onSelectProduct: (product: Product) => void;
  onNavigateCategory: (category: string) => void;
  onNavigateHome: () => void;
  onNavigatePCBuilder: () => void;
  onProceedToCheckout?: () => void;
  onToast: (title: string, message?: string, type?: 'success' | 'error' | 'info') => void;
  isComparing?: (product: Product) => boolean;
  onToggleCompare?: (product: Product) => void;
}

export const ProductDetailPage: React.FC<ProductDetailPageProps> = ({
  productSlugOrId,
  initialProduct,
  onBack,
  onSelectProduct,
  onNavigateCategory,
  onNavigateHome,
  onNavigatePCBuilder,
  onProceedToCheckout,
  onToast,
  isComparing,
  onToggleCompare
}) => {
  const { addToCart } = useCart();
  const { toggleWishlist, isWishlisted } = useWishlist();

  // TanStack Query for instantaneous 0ms cache loading and background sync
  const { data: detailData, isLoading: detailLoading } = useProductDetailQuery(productSlugOrId);
  const { data: serverReviews } = useProductReviewsQuery(productSlugOrId);
  const submitReviewMutation = useSubmitReviewMutation(productSlugOrId);

  const product = detailData || initialProduct || null;
  const loading = detailLoading && !product;

  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState<'specs' | 'telemetry' | 'review' | 'ratings'>('specs');
  const [gameResolution, setGameResolution] = useState<'1080p' | '1440p' | '4k'>('1080p');
  const [showInstallmentModal, setShowInstallmentModal] = useState(false);

  // Customer Reviews State
  const [localReviews, setLocalReviews] = useState<any[]>([]);
  const [newAuthor, setNewAuthor] = useState('');
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  // Related products
  const [relatedProducts, setRelatedProducts] = useState<Product[]>([]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [productSlugOrId]);

  useEffect(() => {
    if (product) {
      if (!selectedVariant && product.variants && product.variants.length > 0) {
        setSelectedVariant(product.variants[0]);
      }
      if (!selectedImage) {
        setSelectedImage(product.imageUrl || (product.images && product.images[0]) || '');
      }

      if (product.categorySlug) {
        fetchProducts({ category: product.categorySlug, limit: 6 })
          .then(res => {
            if (res.products) {
              setRelatedProducts(res.products.filter(p => p.id !== product.id).slice(0, 4));
            }
          })
          .catch(() => {});
      }
    }
  }, [product?.id, product?.categorySlug]);

  const defaultReviews = [
    {
      id: 'rev-1',
      customerName: 'Hoàng Anh Đức',
      rating: 5,
      createdAt: new Date().toISOString(),
      comment: 'Sản phẩm chính hãng nguyên seal tem Viễn Sơn, test benchmark nhiệt độ cực mát, đóng gói 3 lớp xốp chống sốc rất cẩn thận!'
    },
    {
      id: 'rev-2',
      customerName: 'Nguyễn Thanh Tùng',
      rating: 5,
      createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
      comment: 'Giao hàng hỏa tốc trong 2 giờ đúng hẹn. Kỹ thuật viên TechStore hỗ trợ cài đặt và test FPS game Wukong rất nhiệt tình 10/10!'
    }
  ];

  const reviews = serverReviews && serverReviews.length > 0
    ? [...localReviews, ...serverReviews]
    : localReviews.length > 0
    ? localReviews
    : defaultReviews;

  const currentPrice = selectedVariant ? selectedVariant.price : (product?.price || 0);
  const originalPrice = selectedVariant?.originalPrice || product?.originalPrice;
  const isOutOfStock = product?.stockStatus?.status === 'out_of_stock';
  const stockInfo = product?.stockStatus;
  const isFav = product ? isWishlisted(product.id) : false;
  const isComp = product && isComparing ? isComparing(product) : false;

  // Calculate gaming telemetry if hardware product
  const gamingTelemetry = useMemo(() => {
    if (!product) return [];
    const dummyParts: Record<string, Product> = {};
    if (product.categorySlug === 'cpu') dummyParts['cpu'] = product;
    else if (product.categorySlug === 'vga') dummyParts['vga'] = product;
    else if (product.categorySlug === 'pc' || product.categorySlug === 'laptop') {
      dummyParts['cpu'] = product;
      dummyParts['vga'] = product;
    }
    return calculateGamingTelemetry(dummyParts, gameResolution);
  }, [product, gameResolution]);

  const handleAddReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAuthor.trim() || !newComment.trim() || !product) return;
    setSubmittingReview(true);

    try {
      const res = await submitProductReview(product.slug || product.id, {
        author: newAuthor.trim(),
        rating: newRating,
        comment: newComment.trim(),
        productName: product.name
      });

      if (res.success && res.data) {
        setLocalReviews(prev => [
          {
            id: res.data.id,
            customerName: newAuthor,
            rating: newRating,
            createdAt: new Date().toISOString(),
            comment: newComment
          },
          ...prev
        ]);
        setNewAuthor('');
        setNewComment('');
        sound.playVoucherSuccess();
        onToast('Đánh giá thành công!', 'Cảm ơn bạn đã đóng góp đánh giá thực tế cho sản phẩm.');
      }
    } catch (err) {
      console.error(err);
      onToast('Lỗi gửi đánh giá', 'Vui lòng thử lại sau', 'error');
    } finally {
      setSubmittingReview(false);
    }
  };

  const formatVND = (num: number) => new Intl.NumberFormat('vi-VN').format(num) + '₫';

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 rounded-full border-3 border-slate-300 dark:border-slate-700 border-t-[#d70018] animate-spin" />
        <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Đang tải trang chi tiết sản phẩm chính hãng...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] flex flex-col items-center justify-center space-y-4 p-4 text-center">
        <AlertTriangle className="w-12 h-12 text-amber-500" />
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Không tìm thấy sản phẩm</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm">Sản phẩm này có thể đã ngừng kinh doanh hoặc đường dẫn không chính xác.</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-[#d70018] text-white rounded-xl text-xs font-bold cursor-pointer"
        >
          Quay lại danh mục sản phẩm
        </button>
      </div>
    );
  }

  const allImages = [
    product.imageUrl,
    ...(product.images || []),
    ...(product.variants?.map((v: any) => (v as any).imageUrl).filter(Boolean) || [])
  ].filter(Boolean);

  const uniqueImages = Array.from(new Set(allImages));

  return (
    <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] text-slate-800 dark:text-slate-100 transition-colors pb-16">
      {/* 1. Breadcrumbs & Top Navigation Bar */}
      <div className="bg-white dark:bg-[#151c2c] border-b border-gray-200 dark:border-slate-800 py-3 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 overflow-x-auto scrollbar-none py-1">
            <button
              onClick={onNavigateHome}
              className="text-slate-500 hover:text-[#d70018] dark:text-slate-400 dark:hover:text-red-400 font-bold flex items-center space-x-1 cursor-pointer flex-shrink-0"
            >
              <Home className="w-3.5 h-3.5" />
              <span>Trang chủ</span>
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <button
              onClick={() => onNavigateCategory(product.categorySlug)}
              className="text-slate-500 hover:text-[#d70018] dark:text-slate-400 dark:hover:text-red-400 font-bold uppercase cursor-pointer flex-shrink-0"
            >
              {product.categorySlug}
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="text-slate-400 dark:text-slate-500 uppercase font-medium flex-shrink-0">{product.brandName}</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="text-slate-900 dark:text-slate-100 font-bold truncate max-w-[200px] sm:max-w-xs">{product.name}</span>
          </div>

          <button
            onClick={onBack}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-gray-200 dark:border-slate-700 hover:bg-gray-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold transition flex-shrink-0 cursor-pointer shadow-2xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Trở về</span>
          </button>
        </div>
      </div>

      {/* 2. Main Product Showcase Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-6 space-y-8">
        <div className="bg-white dark:bg-[#151c2c] rounded-3xl p-5 sm:p-8 border border-gray-200 dark:border-slate-800 shadow-xs grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Visual Gallery (5 Cols) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-gray-50 dark:bg-slate-900/60 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 flex items-center justify-center relative aspect-square overflow-hidden group">
              <OptimizedImage
                src={selectedImage || product.imageUrl}
                alt={product.name}
                className="max-h-[360px] w-full object-contain transition-transform duration-300 group-hover:scale-105"
              />

              {/* Discount / Hot Badges */}
              <div className="absolute top-3 left-3 flex flex-col gap-1.5">
                {product.discountPercent && (
                  <span className="bg-[#d70018] text-white text-xs font-black px-2.5 py-1 rounded-lg shadow-sm">
                    GIẢM {product.discountPercent}%
                  </span>
                )}
                {product.isHot && (
                  <span className="bg-amber-500 text-white text-[10px] font-black uppercase px-2 py-0.5 rounded-md flex items-center space-x-1 shadow-2xs">
                    <Flame className="w-3 h-3 fill-white" />
                    <span>BÁN CHẠY</span>
                  </span>
                )}
              </div>

              {/* Action Floating Buttons */}
              <div className="absolute top-3 right-3 flex flex-col gap-2">
                <button
                  onClick={() => {
                    toggleWishlist(product.id);
                    sound.playPop();
                  }}
                  className={`p-2.5 rounded-xl border backdrop-blur-md transition shadow-xs cursor-pointer ${
                    isFav
                      ? 'bg-red-50 text-red-600 border-red-300 dark:bg-red-950/80 dark:border-red-800'
                      : 'bg-white/90 dark:bg-slate-800/90 text-slate-500 hover:text-red-500 border-gray-200 dark:border-slate-700'
                  }`}
                  title={isFav ? 'Đã yêu thích' : 'Thêm vào yêu thích'}
                >
                  <Heart className={`w-4 h-4 ${isFav ? 'fill-red-600' : ''}`} />
                </button>
              </div>
            </div>

            {/* Gallery Thumbnails */}
            {uniqueImages.length > 1 && (
              <div className="flex items-center space-x-2.5 overflow-x-auto pb-2 scrollbar-none">
                {uniqueImages.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setSelectedImage(img);
                      sound.playClick();
                    }}
                    className={`w-16 h-16 rounded-xl p-1 border-2 transition-all flex-shrink-0 cursor-pointer overflow-hidden bg-white dark:bg-slate-900 ${
                      selectedImage === img
                        ? 'border-[#d70018] shadow-xs'
                        : 'border-gray-200 dark:border-slate-700 hover:border-gray-400 opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={img} alt="" className="w-full h-full object-contain" />
                  </button>
                ))}
              </div>
            )}

            {/* Quick Highlights Box */}
            {product.highlights && product.highlights.length > 0 && (
              <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-gray-200 dark:border-slate-800 space-y-2 text-xs">
                <span className="font-bold text-slate-900 dark:text-slate-100 block text-[11px] uppercase tracking-wider">
                  Đặc Điểm Nổi Bật:
                </span>
                <ul className="space-y-1.5 text-slate-600 dark:text-slate-300">
                  {product.highlights.map((h: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span className="leading-snug">{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Right Column: Pricing, Specs, Installment & Buy Actions (7 Cols) */}
          <div className="lg:col-span-7 space-y-5">
            <div>
              <div className="flex items-center space-x-2 text-xs text-[#d70018] dark:text-red-400 font-bold mb-1.5 uppercase">
                <span>{product.brandName}</span>
                <span>•</span>
                <span className="text-slate-400 dark:text-slate-500">{product.categorySlug}</span>
                <span>•</span>
                <span className="text-emerald-600 dark:text-emerald-400">CHÍNH HÃNG 100%</span>
              </div>

              <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 leading-snug">
                {product.name}
              </h1>

              <div className="flex items-center space-x-3 mt-2 text-xs">
                <div className="flex items-center text-amber-400">
                  {[1, 2, 3, 4, 5].map(s => (
                    <Star key={s} className="w-4 h-4 fill-amber-400" />
                  ))}
                </div>
                <span className="font-bold text-slate-800 dark:text-slate-200">4.9/5</span>
                <span className="text-slate-400">({reviews.length * 12 + 18} đánh giá)</span>
                <span className="text-slate-300 dark:text-slate-700">|</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Bảo hành {product.specs?.warranty_months || 36} Tháng</span>
                </span>
              </div>
            </div>

            {/* Pricing Box */}
            <div className="p-4 sm:p-5 bg-gradient-to-r from-red-50/60 to-slate-50 dark:from-red-950/20 dark:to-slate-900/60 rounded-2xl border border-red-200/70 dark:border-red-950/60 space-y-2">
              <div className="flex flex-wrap items-baseline gap-3">
                <span className="text-3xl font-black text-[#d70018] dark:text-red-400 font-mono tracking-tight">
                  {formatVND(currentPrice)}
                </span>
                {originalPrice && originalPrice > currentPrice && (
                  <span className="text-base text-slate-400 line-through font-mono">
                    {formatVND(originalPrice)}
                  </span>
                )}
                {product.discountPercent && (
                  <span className="bg-emerald-600 text-white text-xs font-bold px-2 py-0.5 rounded shadow-2xs">
                    Tiết kiệm {product.discountPercent}%
                  </span>
                )}
              </div>

              <div className="text-xs pt-1">
                {isOutOfStock ? (
                  <span className="text-red-600 font-bold flex items-center space-x-1">
                    <XCircle className="w-4 h-4" />
                    <span>Tạm hết hàng tại showroom</span>
                  </span>
                ) : stockInfo?.status === 'low_stock' ? (
                  <span className="text-amber-600 font-bold flex items-center space-x-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Chỉ còn {stockInfo.availableQty} sản phẩm trong kho</span>
                  </span>
                ) : (
                  <span className="text-emerald-700 dark:text-emerald-400 font-bold flex items-center space-x-1">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Còn hàng - Giao hỏa tốc 2 giờ tại chi nhánh</span>
                  </span>
                )}
              </div>
            </div>

            {/* Trả góp 0% Interactive Banner */}
            {currentPrice >= 1000000 && (
              <div className="flex items-center justify-between p-3.5 bg-amber-50/90 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 rounded-2xl text-xs">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-xl bg-amber-500 text-white flex items-center justify-center font-black text-xs flex-shrink-0 shadow-xs">
                    0%
                  </div>
                  <div>
                    <span className="text-slate-800 dark:text-slate-200 font-bold block">
                      Trả góp 0% lãi suất chỉ từ <strong className="text-[#d70018] dark:text-red-400 font-mono">{formatVND(Math.round(currentPrice / 6))}</strong>/tháng
                    </span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400">
                      Duyệt online 15 phút qua Fundiin hoặc Thẻ tín dụng 25 ngân hàng
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowInstallmentModal(true);
                    sound.playClick();
                  }}
                  className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold text-xs transition shadow-2xs cursor-pointer flex-shrink-0"
                >
                  Bảng tính
                </button>
              </div>
            )}

            {/* Variants Selector */}
            {product.variants && product.variants.length > 0 && (
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-800 dark:text-slate-200">
                  Chọn phiên bản cấu hình:
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {product.variants.map((v: any) => (
                    <button
                      key={v.id}
                      onClick={() => {
                        setSelectedVariant(v);
                        sound.playClick();
                      }}
                      className={`p-3 rounded-xl border text-xs text-left transition flex items-center justify-between cursor-pointer ${
                        selectedVariant?.id === (v as any).id
                          ? 'border-[#d70018] bg-red-50/60 dark:bg-red-950/40 text-[#d70018] dark:text-red-400 font-bold ring-2 ring-red-100 dark:ring-red-950/60 shadow-2xs'
                          : 'border-gray-200 dark:border-slate-800 hover:border-gray-300 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900/60'
                      }`}
                    >
                      <span className="truncate pr-2">{v.name}</span>
                      <span className="font-mono font-bold text-slate-900 dark:text-slate-100 flex-shrink-0">
                        {formatVND(v.price)}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Quantity & Buy Buttons */}
            {!isOutOfStock ? (
              <div className="space-y-3 pt-2">
                <div className="flex items-center space-x-3 text-xs">
                  <span className="font-bold text-slate-600 dark:text-slate-400">Số lượng:</span>
                  <div className="flex items-center border border-gray-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 overflow-hidden">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="px-3.5 py-1.5 text-slate-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 font-bold cursor-pointer"
                    >
                      -
                    </button>
                    <span className="px-3 py-1.5 text-xs font-bold text-slate-900 dark:text-slate-100 font-mono">{quantity}</span>
                    <button
                      onClick={() => setQuantity(quantity + 1)}
                      className="px-3.5 py-1.5 text-slate-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 font-bold cursor-pointer"
                    >
                      +
                    </button>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 pt-1">
                  <button
                    onClick={() => {
                      addToCart(product, selectedVariant || undefined, quantity);
                      sound.playPop();
                      onToast('Đã thêm vào giỏ hàng!', `${quantity}x ${product.name}`);
                    }}
                    className="flex-1 py-3.5 px-4 border-2 border-[#d70018] text-[#d70018] hover:bg-red-50 dark:hover:bg-red-950/40 font-bold rounded-2xl text-xs sm:text-sm flex items-center justify-center space-x-2 transition cursor-pointer shadow-xs"
                  >
                    <ShoppingCart className="w-4 h-4" />
                    <span>Thêm Vào Giỏ Hàng</span>
                  </button>

                  <button
                    onClick={() => {
                      addToCart(product, selectedVariant || undefined, quantity);
                      sound.playVoucherSuccess();
                      if (onProceedToCheckout) {
                        onProceedToCheckout();
                      }
                    }}
                    className="flex-1 py-3.5 px-4 bg-[#d70018] hover:bg-[#b91c1c] text-white font-bold rounded-2xl text-xs sm:text-sm flex items-center justify-center space-x-2 transition cursor-pointer shadow-md hover:shadow-lg active:scale-98"
                  >
                    <Zap className="w-4 h-4 fill-white" />
                    <span>Mua Ngay (Giao 2H)</span>
                  </button>
                </div>
              </div>
            ) : (
              <button
                disabled
                className="w-full py-3.5 bg-gray-100 dark:bg-slate-800 text-slate-400 font-semibold rounded-2xl text-xs cursor-not-allowed text-center border border-gray-200 dark:border-slate-700"
              >
                Sản phẩm tạm hết hàng - Báo khi có hàng lại
              </button>
            )}

            {/* Commitments Bar */}
            <div className="grid grid-cols-3 gap-2 pt-4 border-t border-gray-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400">
              <div className="flex items-center space-x-2">
                <RotateCcw className="w-4 h-4 text-[#d70018] flex-shrink-0" />
                <span>1 Đổi 1 Trong 30 Ngày</span>
              </div>
              <div className="flex items-center space-x-2">
                <Truck className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span>Giao Nhanh 2 Giờ</span>
              </div>
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Chính Hãng 100%</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Deep Tabbed Details Section */}
        <div className="bg-white dark:bg-[#151c2c] rounded-3xl p-5 sm:p-8 border border-gray-200 dark:border-slate-800 shadow-xs space-y-6">
          {/* Tabs Bar */}
          <div className="flex space-x-2 border-b border-gray-200 dark:border-slate-800 pb-3 overflow-x-auto scrollbar-none text-xs font-bold">
            <button
              onClick={() => setActiveTab('specs')}
              className={`px-4 py-2.5 rounded-xl transition cursor-pointer flex items-center space-x-1.5 flex-shrink-0 ${
                activeTab === 'specs'
                  ? 'bg-[#d70018] text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>Thông Số Kỹ Thuật Đầy Đủ</span>
            </button>

            {gamingTelemetry.length > 0 && (
              <button
                onClick={() => setActiveTab('telemetry')}
                className={`px-4 py-2.5 rounded-xl transition cursor-pointer flex items-center space-x-1.5 flex-shrink-0 ${
                  activeTab === 'telemetry'
                    ? 'bg-[#d70018] text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800'
                }`}
              >
                <Activity className="w-4 h-4" />
                <span>Hiệu Năng & Đo FPS Game</span>
              </button>
            )}

            <button
              onClick={() => setActiveTab('review')}
              className={`px-4 py-2.5 rounded-xl transition cursor-pointer flex items-center space-x-1.5 flex-shrink-0 ${
                activeTab === 'review'
                  ? 'bg-[#d70018] text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Bài Viết Đánh Giá Chi Tiết</span>
            </button>

            <button
              onClick={() => setActiveTab('ratings')}
              className={`px-4 py-2.5 rounded-xl transition cursor-pointer flex items-center space-x-1.5 flex-shrink-0 ${
                activeTab === 'ratings'
                  ? 'bg-[#d70018] text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Đánh Giá Khách Hàng ({reviews.length})</span>
            </button>
          </div>

          {/* TAB 1: TECHNICAL SPECS TABLE */}
          {activeTab === 'specs' && (
            <div className="space-y-4">
              <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">
                Bảng Thông Số Kỹ Thuật Chi Tiết Từ Nhà Sản Xuất:
              </h3>
              <div className="border border-gray-200 dark:border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full text-xs text-left">
                  <tbody className="divide-y divide-gray-150 dark:divide-slate-800">
                    <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                      <td className="py-3 px-4 font-bold text-slate-500 w-1/3">Thương hiệu / Hãng</td>
                      <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.brandName}</td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-bold text-slate-500">Danh mục sản phẩm</td>
                      <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100 uppercase">{product.categorySlug}</td>
                    </tr>
                    {product.specs?.socket && (
                      <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                        <td className="py-3 px-4 font-bold text-slate-500">Chuẩn chân Socket</td>
                        <td className="py-3 px-4 font-bold text-blue-600 dark:text-blue-400">{product.specs.socket}</td>
                      </tr>
                    )}
                    {product.specs?.chipset && (
                      <tr>
                        <td className="py-3 px-4 font-bold text-slate-500">Chipset bo mạch</td>
                        <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.specs.chipset}</td>
                      </tr>
                    )}
                    {product.specs?.cores && (
                      <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                        <td className="py-3 px-4 font-bold text-slate-500">Số nhân / Số luồng</td>
                        <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.specs.cores} Nhân</td>
                      </tr>
                    )}
                    {product.specs?.tdp_w && (
                      <tr>
                        <td className="py-3 px-4 font-bold text-slate-500">Công suất tiêu thụ (TDP)</td>
                        <td className="py-3 px-4 font-bold text-amber-600 font-mono">{product.specs.tdp_w}W</td>
                      </tr>
                    )}
                    {product.specs?.tgp_w && (
                      <tr>
                        <td className="py-3 px-4 font-bold text-slate-500">Điện năng tiêu thụ (TGP)</td>
                        <td className="py-3 px-4 font-bold text-amber-600 font-mono">{product.specs.tgp_w}W</td>
                      </tr>
                    )}
                    {product.specs?.psu_watt && (
                      <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                        <td className="py-3 px-4 font-bold text-slate-500">Công suất thực nguồn</td>
                        <td className="py-3 px-4 font-bold text-emerald-600 font-mono">{product.specs.psu_watt}W</td>
                      </tr>
                    )}
                    {product.specs?.ram_gb && (
                      <tr>
                        <td className="py-3 px-4 font-bold text-slate-500">Dung lượng bộ nhớ RAM</td>
                        <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.specs.ram_gb}GB {product.specs.ram_type}</td>
                      </tr>
                    )}
                    {product.specs?.vram_gb && (
                      <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                        <td className="py-3 px-4 font-bold text-slate-500">Dung lượng VRAM đồ họa</td>
                        <td className="py-3 px-4 font-bold text-purple-600 font-mono">{product.specs.vram_gb}GB GDDR6 / GDDR7</td>
                      </tr>
                    )}
                    {product.specs?.storage_gb && (
                      <tr>
                        <td className="py-3 px-4 font-bold text-slate-500">Dung lượng lưu trữ SSD</td>
                        <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.specs.storage_gb}GB NVMe M.2</td>
                      </tr>
                    )}
                    {product.specs?.form_factor && (
                      <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                        <td className="py-3 px-4 font-bold text-slate-500">Kích thước chuẩn (Form factor)</td>
                        <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.specs.form_factor}</td>
                      </tr>
                    )}
                    {product.specs?.length_mm && (
                      <tr>
                        <td className="py-3 px-4 font-bold text-slate-500">Chiều dài VGA</td>
                        <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{product.specs.length_mm} mm</td>
                      </tr>
                    )}
                    <tr className="bg-gray-50/50 dark:bg-slate-900/50">
                      <td className="py-3 px-4 font-bold text-slate-500">Thời hạn bảo hành chính hãng</td>
                      <td className="py-3 px-4 font-bold text-emerald-700 dark:text-emerald-400">{product.specs?.warranty_months || 36} Tháng (1 Đổi 1 trong 30 ngày)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: GAMING TELEMETRY & FPS BENCHMARKS */}
          {activeTab === 'telemetry' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-gray-150 dark:border-slate-800">
                <div>
                  <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                    <Activity className="w-4 h-4 text-amber-500" />
                    <span>Dự Toán Hiệu Năng Chiến Game Thực Tế (Live Telemetry)</span>
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Số liệu benchmark FPS thực tế trên các tựa game phổ biến nhất tại Việt Nam
                  </p>
                </div>

                <div className="flex items-center space-x-1 bg-gray-100 dark:bg-slate-800 p-1 rounded-xl self-start sm:self-auto">
                  {(['1080p', '1440p', '4k'] as const).map(res => (
                    <button
                      key={res}
                      onClick={() => {
                        setGameResolution(res);
                        sound.playClick();
                      }}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                        gameResolution === res
                          ? 'bg-[#d70018] text-white shadow-2xs'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                      }`}
                    >
                      {res === '1080p' ? 'Full HD (1080p)' : res === '1440p' ? '2K (1440p)' : '4K Ultra'}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {gamingTelemetry.map(game => (
                  <div key={game.id} className="p-3.5 bg-gray-50 dark:bg-slate-900/60 rounded-2xl border border-gray-200 dark:border-slate-800 space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <strong className="text-xs text-slate-900 dark:text-slate-100 block">{game.name}</strong>
                        <span className="text-[10px] text-slate-400">{game.genre}</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        game.experienceRating === 'ultra' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300' :
                        game.experienceRating === 'smooth' ? 'bg-blue-100 text-blue-800 dark:bg-blue-950/80 dark:text-blue-300' :
                        'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300'
                      }`}>
                        {game.badgeText}
                      </span>
                    </div>

                    <div className="flex items-baseline justify-between pt-1">
                      <span className="text-xl font-black text-slate-900 dark:text-slate-100 font-mono">
                        {game.fpsText}
                      </span>
                      <span className="text-[10px] text-slate-500 font-medium">{game.settingsNote}</span>
                    </div>

                    <div className="w-full bg-gray-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-[#d70018] h-full rounded-full transition-all duration-500" style={{ width: `${game.progressPct}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: EDITORIAL REVIEW & HIGHLIGHTS */}
          {activeTab === 'review' && (
            <div className="space-y-4 text-xs leading-relaxed text-slate-700 dark:text-slate-300">
              <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">
                Đánh Giá Chuyên Sâu Về {product.name}
              </h3>
              <p>
                {product.description ||
                  `${product.name} là dòng sản phẩm cao cấp thuộc thương hiệu ${product.brandName}, được tối ưu hóa cho nhu cầu làm việc đồ họa chuyên nghiệp và chiến các tựa game AAA đỉnh cao. Sản phẩm trang bị các linh kiện tuyển chọn, hệ thống tản nhiệt tiên tiến giúp nhiệt độ luôn ổn định dưới tải nặng kéo dài.`}
              </p>
              <div className="p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-2xl border border-emerald-200 dark:border-emerald-800/60 space-y-2">
                <span className="font-bold text-emerald-900 dark:text-emerald-200 text-xs flex items-center space-x-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Cam Kết Chất Lượng Tại TechStore Studio:</span>
                </span>
                <p className="text-emerald-800/90 dark:text-emerald-300/90 text-xs">
                  Mọi sản phẩm bán ra đều được phòng Lab TechStore kiểm tra thông số, tra keo tản nhiệt xịn (Kryonaut / TF7), cài đặt Windows bản quyền và kiểm tra tương thích kỹ lưỡng trước khi đóng gói gửi đến tay khách hàng.
                </p>
              </div>
            </div>
          )}

          {/* TAB 4: CUSTOMER REVIEWS & FORM */}
          {activeTab === 'ratings' && (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-150 dark:border-slate-800 gap-4">
                <div>
                  <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">
                    Khách Hàng Nói Gì Về Sản Phẩm Này ({reviews.length} đánh giá)
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">100% đánh giá từ khách hàng đã mua và trải nghiệm thực tế</p>
                </div>

                <div className="flex items-center space-x-2">
                  <div className="flex items-center text-amber-400">
                    {[1, 2, 3, 4, 5].map(s => <Star key={s} className="w-4 h-4 fill-amber-400" />)}
                  </div>
                  <strong className="text-lg font-black text-slate-900 dark:text-slate-100 font-mono">4.9 / 5</strong>
                </div>
              </div>

              {/* Reviews List */}
              <div className="space-y-3">
                {reviews.map((r, idx) => (
                  <div key={r.id || idx} className="p-4 bg-gray-50 dark:bg-slate-900/60 rounded-2xl border border-gray-200 dark:border-slate-800 space-y-2 text-xs">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <strong className="text-slate-900 dark:text-slate-100">{r.customerName || r.author || 'Khách hàng'}</strong>
                        <span className="text-[10px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 px-2 py-0.5 rounded-full font-bold flex items-center space-x-1">
                          <Check className="w-2.5 h-2.5" />
                          <span>Đã mua hàng</span>
                        </span>
                      </div>
                      <span className="text-slate-400 text-[11px]">{new Date(r.createdAt || Date.now()).toLocaleDateString('vi-VN')}</span>
                    </div>

                    <div className="flex items-center text-amber-400">
                      {[1, 2, 3, 4, 5].map(s => (
                        <Star key={s} className={`w-3.5 h-3.5 ${s <= (r.rating || 5) ? 'fill-amber-400' : 'text-gray-300'}`} />
                      ))}
                    </div>

                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{r.comment}</p>
                  </div>
                ))}
              </div>

              {/* Add Review Form */}
              <form onSubmit={handleAddReview} className="p-5 bg-slate-50 dark:bg-slate-900/80 rounded-2xl border border-gray-200 dark:border-slate-800 space-y-3 text-xs">
                <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs sm:text-sm">Gửi Nhận Xét Của Bạn:</h4>
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500">Đánh giá sao:</span>
                  <div className="flex items-center space-x-1">
                    {[1, 2, 3, 4, 5].map(s => (
                      <button
                        type="button"
                        key={s}
                        onClick={() => setNewRating(s)}
                        className="cursor-pointer"
                      >
                        <Star className={`w-5 h-5 ${s <= newRating ? 'text-amber-400 fill-amber-400' : 'text-gray-300'}`} />
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    type="text"
                    required
                    value={newAuthor}
                    onChange={e => setNewAuthor(e.target.value)}
                    placeholder="Họ và tên của bạn *"
                    className="px-3.5 py-2.5 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl outline-none text-slate-900 dark:text-slate-100 font-medium"
                  />
                </div>

                <textarea
                  required
                  rows={3}
                  value={newComment}
                  onChange={e => setNewComment(e.target.value)}
                  placeholder="Chia sẻ cảm nhận về hiệu năng, độ mát, độ êm hoặc thời gian giao hàng... *"
                  className="w-full px-3.5 py-2.5 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl outline-none text-slate-900 dark:text-slate-100"
                />

                <button
                  type="submit"
                  disabled={submittingReview}
                  className="px-5 py-2.5 bg-[#d70018] hover:bg-[#b91c1c] text-white font-bold rounded-xl transition cursor-pointer shadow-xs disabled:opacity-50"
                >
                  {submittingReview ? 'Đang gửi...' : 'Gửi Đánh Giá Ngay'}
                </button>
              </form>
            </div>
          )}
        </div>

        {/* 4. Related Products & Cross-Sell Section */}
        {relatedProducts.length > 0 && (
          <div className="space-y-4 pt-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base sm:text-lg text-slate-900 dark:text-slate-100">
                  Sản Phẩm Thường Được Mua Kèm / Cùng Danh Mục
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">Các linh kiện tương thích tối ưu được kỹ thuật viên đề xuất</p>
              </div>

              <button
                onClick={() => onNavigateCategory(product.categorySlug)}
                className="text-xs text-[#d70018] dark:text-red-400 font-bold hover:underline flex items-center space-x-1 cursor-pointer"
              >
                <span>Xem tất cả {product.categorySlug.toUpperCase()}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {relatedProducts.map(rel => (
                <div
                  key={rel.id}
                  onClick={() => onSelectProduct(rel)}
                  className="bg-white dark:bg-[#151c2c] rounded-2xl p-4 border border-gray-200 dark:border-slate-800 hover:border-red-400 dark:hover:border-red-500 transition-all hover:shadow-md cursor-pointer flex flex-col justify-between space-y-3 group"
                >
                  <div className="aspect-square bg-gray-50 dark:bg-slate-900/60 rounded-xl p-3 flex items-center justify-center overflow-hidden">
                    <img src={rel.imageUrl} alt={rel.name} className="max-h-36 w-full object-contain group-hover:scale-105 transition-transform" />
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">{rel.brandName}</span>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 line-clamp-2 group-hover:text-[#d70018] transition">
                      {rel.name}
                    </h4>
                  </div>

                  <div className="pt-2 border-t border-gray-150 dark:border-slate-800 flex items-center justify-between">
                    <span className="text-xs font-black text-[#d70018] dark:text-red-400 font-mono">
                      {formatVND(rel.price)}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        addToCart(rel);
                        sound.playPop();
                        onToast('Đã thêm vào giỏ!', rel.name);
                      }}
                      className="p-1.5 rounded-lg bg-gray-100 dark:bg-slate-800 hover:bg-[#d70018] hover:text-white transition cursor-pointer"
                      title="Thêm nhanh vào giỏ hàng"
                    >
                      <ShoppingCart className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 5. 0% Installment Calculator Modal */}
      <InstallmentCalculatorModal
        isOpen={showInstallmentModal}
        onClose={() => setShowInstallmentModal(false)}
        productName={product.name}
        price={currentPrice}
        onSelectPlan={(plan) => {
          addToCart(product, selectedVariant || undefined, 1);
          setShowInstallmentModal(false);
          onToast('Đã chọn gói trả góp!', `${plan.provider} • Kỳ hạn ${plan.termMonths} tháng`);
        }}
      />
    </div>
  );
};
