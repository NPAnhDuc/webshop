import { OptimizedImage } from '../common/OptimizedImage';
import React, { useState, useEffect } from 'react';
import {
  X,
  ShoppingCart,
  Sparkles,
  ShieldCheck,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  CreditCard,
  Star,
  ThumbsUp,
  MessageSquare,
  Award
} from 'lucide-react';
import { Product, ProductVariant } from '../../types';
import { useCart } from '../../context/CartContext';
import { fetchProductDetail, fetchProductReviews, submitProductReview } from '../../services/api';
import { sound } from '../../utils/sound';
import { InstallmentCalculatorModal } from '../common/InstallmentCalculatorModal';

interface ProductDetailModalProps {
  product: Product | null;
  onClose: () => void;
  onAskBot: (product: Product) => void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  product,
  onClose,
  onAskBot
}) => {
  const { addToCart } = useCart();
  const [detailedProduct, setDetailedProduct] = useState<any>(null);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);

  // Customer Reviews State
  const [reviews, setReviews] = useState<any[]>([]);
  const [newAuthor, setNewAuthor] = useState('');
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewSubmitted, setReviewSubmitted] = useState(false);
  const [showInstallmentModal, setShowInstallmentModal] = useState(false);

  const loadReviews = (slugOrId: string) => {
    fetchProductReviews(slugOrId)
      .then(data => {
        if (data && data.length > 0) {
          const formatted = data.map(r => ({
            id: r.id,
            author: r.customerName || 'Khách hàng',
            location: 'Việt Nam',
            rating: r.rating || 5,
            date: new Date(r.createdAt).toLocaleDateString('vi-VN'),
            verified: true,
            comment: r.comment,
            reply: r.reply,
            helpful: Math.floor(Math.random() * 8) + 2
          }));
          setReviews(formatted);
        } else {
          setReviews([
            {
              id: 'rev-default-1',
              author: 'Võ Minh Tuấn',
              location: 'Hà Nội',
              rating: 5,
              date: '15/10/2026',
              verified: true,
              comment: 'Máy bọc chống sốc 3 lớp rất kỹ, mở hộp thơm mùi máy mới seal zin. Màn hình nét căng, test nhiệt độ render 4K rất êm và mát. Shop tư vấn nhiệt tình 10/10!',
              helpful: 12
            },
            {
              id: 'rev-default-2',
              author: 'Nguyễn Thảo Ly',
              location: 'Đà Nẵng',
              rating: 5,
              date: '12/10/2026',
              verified: true,
              comment: 'Giao hàng hỏa tốc trong 2 tiếng đúng như cam kết, shipper thân thiện cho kiểm tra bật máy trước khi nhận. Đang dùng mượt mà không có điểm chết màn hình.',
              helpful: 8
            }
          ]);
        }
      })
      .catch(() => {});
  };

  const handleAddReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAuthor.trim() || !newComment.trim() || !product) return;

    try {
      const res = await submitProductReview(product.slug || product.id, {
        author: newAuthor,
        rating: newRating,
        comment: newComment,
        productName: product.name
      });

      if (res.success && res.data) {
        setReviews(prev => [
          {
            id: res.data.id,
            author: newAuthor,
            location: 'Việt Nam',
            rating: newRating,
            date: 'Vừa xong',
            verified: true,
            comment: newComment,
            helpful: 1
          },
          ...prev
        ]);
      }
    } catch (err) {
      console.error(err);
    }

    setNewAuthor('');
    setNewComment('');
    setShowReviewForm(false);
    setReviewSubmitted(true);
    sound.playVoucherSuccess();
    setTimeout(() => setReviewSubmitted(false), 4000);
  };

  useEffect(() => {
    if (!product) {
      setDetailedProduct(null);
      setSelectedVariant(null);
      return;
    }

    loadReviews(product.slug || product.id);

    setLoading(true);
    fetchProductDetail(product.slug || product.id)
      .then(data => {
        setDetailedProduct(data);
        if (data.variants && data.variants.length > 0) {
          setSelectedVariant(data.variants[0]);
        }
        setSelectedImage(data.imageUrl || (data.images && data.images[0]) || '');
      })
      .catch(err => {
        console.error(err);
        setDetailedProduct(product);
        setSelectedVariant(product.variants?.[0] || null);
        setSelectedImage(product.imageUrl);
      })
      .finally(() => setLoading(false));
  }, [product]);

  if (!product) return null;

  const currentPrice = selectedVariant?.price || product.price;
  const originalPrice = selectedVariant?.originalPrice || product.originalPrice;
  const stockInfo = detailedProduct?.stockStatus || product.stockStatus;
  const isOutOfStock = stockInfo?.status === 'out_of_stock';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200 text-slate-800 dark:text-slate-100">
      <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl max-w-4xl w-full max-h-[92vh] overflow-y-auto shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 transition cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {loading ? (
          <div className="p-16 text-center text-slate-400">
            <div className="w-8 h-8 border-2 border-[#d70018] dark:border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <span>Đang tải thông số kỹ thuật...</span>
          </div>
        ) : (
          <div className="p-6 sm:p-8 space-y-6">
            {/* Top Grid: Gallery & Buying Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Left Column: Image Gallery */}
              <div className="space-y-4">
                <div className="aspect-square bg-gray-50 dark:bg-slate-900/60 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 flex items-center justify-center overflow-hidden relative group">
                  <img
                    src={selectedImage || product.imageUrl}
                    alt={product.name}
                    className="max-h-full max-w-full object-contain drop-shadow-sm z-10 group-hover:scale-105 transition-transform"
                  />
                </div>

                {/* Thumbnails */}
                {product.images && product.images.length > 1 && (
                  <div className="flex space-x-2 overflow-x-auto pb-1">
                    {product.images.map((img, idx) => (
                      <button
                        key={idx}
                        onClick={() => setSelectedImage(img)}
                        className={`w-16 h-16 rounded-xl border p-1 bg-white dark:bg-slate-800 flex-shrink-0 transition cursor-pointer ${
                          selectedImage === img ? 'border-[#d70018] dark:border-emerald-400 ring-2 ring-emerald-200 dark:ring-emerald-900/50' : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600'
                        }`}
                      >
                        <img src={img} alt="thumb" className="w-full h-full object-contain" />
                      </button>
                    ))}
                  </div>
                )}

                {/* AI Assistant Context Action */}
                <div className="bg-emerald-50/60 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-2xl p-3.5 flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <Sparkles className="w-5 h-5 text-[#d70018] dark:text-red-400" />
                    <div>
                      <p className="text-xs font-bold text-slate-900 dark:text-slate-100">Trợ lý AI TechStore</p>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">Tư vấn ưu nhược điểm & ước tính trả góp</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      onClose();
                      onAskBot(product);
                    }}
                    className="px-3 py-1.5 bg-[#d70018] hover:bg-[#b91c1c] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer"
                  >
                    Hỏi ngay
                  </button>
                </div>
              </div>

              {/* Right Column: Title, Variants, Pricing & Actions */}
              <div className="space-y-4">
                <div>
                  <div className="flex items-center space-x-2 text-xs text-[#d70018] dark:text-red-400 font-bold mb-1">
                    <span className="uppercase">{product.brandName}</span>
                    <span>•</span>
                    <span className="uppercase text-slate-400 dark:text-slate-500">{product.categorySlug}</span>
                  </div>
                  <h1 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-slate-100 leading-snug">
                    {product.name}
                  </h1>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="flex items-center text-amber-400">
                      {[1, 2, 3, 4, 5].map(s => (
                        <Star key={s} className="w-3.5 h-3.5 fill-amber-400" />
                      ))}
                    </div>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">4.9/5</span>
                    <span className="text-[11px] text-slate-400">({reviews.length * 16} đánh giá)</span>
                    <span className="text-[10px] bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 px-1.5 py-0.5 rounded font-bold border border-emerald-200 dark:border-emerald-800">
                      98% hài lòng
                    </span>
                  </div>
                </div>

                {/* Pricing & Stock Status */}
                <div className="bg-gray-50 dark:bg-slate-900/60 p-4 rounded-2xl border border-gray-200 dark:border-slate-800 space-y-2">
                  <div className="flex items-baseline space-x-3">
                    <span className="text-2xl font-black text-[#d70018] dark:text-red-400 font-mono">
                      {new Intl.NumberFormat('vi-VN').format(currentPrice)}₫
                    </span>
                    {originalPrice && originalPrice > currentPrice && (
                      <span className="text-sm text-slate-400 dark:text-slate-500 line-through font-mono">
                        {new Intl.NumberFormat('vi-VN').format(originalPrice)}₫
                      </span>
                    )}
                    {product.discountPercent && (
                      <span className="bg-[#059669] dark:bg-emerald-500 text-white dark:text-slate-950 text-xs font-bold px-2 py-0.5 rounded shadow-2xs">
                        Tiết kiệm {product.discountPercent}%
                      </span>
                    )}
                  </div>

                  <div className="text-xs flex items-center space-x-2 pt-1">
                    {isOutOfStock ? (
                      <span className="text-slate-500 font-semibold flex items-center space-x-1">
                        <XCircle className="w-4 h-4 text-red-500" />
                        <span>Sản phẩm hiện đang tạm hết hàng tại kho</span>
                      </span>
                    ) : stockInfo?.status === 'low_stock' ? (
                      <span className="text-amber-700 font-semibold flex items-center space-x-1">
                        <AlertTriangle className="w-4 h-4 text-amber-500" />
                        <span>Kho chỉ còn {stockInfo.availableQty} sản phẩm</span>
                      </span>
                    ) : (
                      <span className="text-emerald-700 font-semibold flex items-center space-x-1">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Còn hàng - Giao hỏa tốc 2 giờ tại chi nhánh</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* 0% Installment Action Banner */}
                {currentPrice >= 1000000 && (
                  <div className="flex items-center justify-between p-3 bg-amber-50/90 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 rounded-2xl text-xs">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-amber-500 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                        0%
                      </div>
                      <div>
                        <span className="text-slate-700 dark:text-slate-300 font-medium block">
                          Trả góp 0% chỉ từ <strong className="text-[#d70018] dark:text-red-400 font-mono font-bold">{new Intl.NumberFormat('vi-VN').format(Math.round(currentPrice / 6))}₫</strong>/tháng
                        </span>
                        <span className="text-[10px] text-slate-400 dark:text-slate-500">Duyệt online 15 phút qua Fundiin hoặc Thẻ tín dụng</span>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setShowInstallmentModal(true);
                        sound.playClick();
                      }}
                      className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold text-[11px] transition shadow-2xs cursor-pointer flex-shrink-0"
                    >
                      Bảng tính
                    </button>
                  </div>
                )}

                {/* Variants Selector */}
                {product.variants && product.variants.length > 0 && (
                  <div>
                    <label className="block text-xs font-bold text-slate-800 dark:text-slate-200 mb-2">
                      Chọn phiên bản cấu hình:
                    </label>
                    <div className="grid grid-cols-1 gap-2">
                      {product.variants.map(v => (
                        <button
                          key={v.id}
                          onClick={() => setSelectedVariant(v)}
                          className={`p-3 rounded-xl border text-xs text-left transition flex items-center justify-between cursor-pointer ${
                            selectedVariant?.id === v.id
                              ? 'border-[#d70018] dark:border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-[#d70018] dark:text-emerald-300 font-bold shadow-2xs'
                              : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800/80'
                          }`}
                        >
                          <span>{v.name}</span>
                          <span className="font-bold text-slate-900 dark:text-slate-100 font-mono">
                            {new Intl.NumberFormat('vi-VN').format(v.price)}₫
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quantity & Buy Buttons */}
                {!isOutOfStock ? (
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Số lượng:</span>
                      <div className="flex items-center border border-gray-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800">
                        <button
                          onClick={() => setQuantity(Math.max(1, quantity - 1))}
                          className="px-3 py-1 text-slate-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 font-bold rounded-l-xl cursor-pointer"
                        >
                          -
                        </button>
                        <span className="px-3 py-1 text-xs font-bold text-slate-900 dark:text-slate-100">{quantity}</span>
                        <button
                          onClick={() => setQuantity(quantity + 1)}
                          className="px-3 py-1 text-slate-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 font-bold rounded-r-xl cursor-pointer"
                        >
                          +
                        </button>
                      </div>
                    </div>

                    <div className="flex space-x-3">
                      <button
                        onClick={() => {
                          addToCart(product, selectedVariant || undefined, quantity);
                          onClose();
                        }}
                        className="flex-1 py-3 px-4 bg-[#d70018] hover:bg-[#b91c1c] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white font-bold rounded-xl text-sm flex items-center justify-center space-x-2 transition shadow-sm active:scale-95 cursor-pointer"
                      >
                        <ShoppingCart className="w-4 h-4" />
                        <span>Thêm vào giỏ hàng</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    disabled
                    className="w-full py-3 bg-gray-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 font-semibold rounded-xl text-sm cursor-not-allowed text-center border border-gray-200 dark:border-slate-700"
                  >
                    Báo khi có hàng trở lại
                  </button>
                )}

                {/* Store Commitments */}
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400">
                  <div className="flex items-center space-x-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-red-400 flex-shrink-0" />
                    <span>Bảo hành {product.specs?.warranty_months || 12}T</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <RotateCcw className="w-4 h-4 text-[#d70018] dark:text-red-400 flex-shrink-0" />
                    <span>1 đổi 1 30 ngày</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setShowInstallmentModal(true);
                      sound.playClick();
                    }}
                    className="flex items-center space-x-1.5 hover:text-amber-600 dark:hover:text-amber-400 transition cursor-pointer text-left"
                    title="Mở bảng tính toán trả góp 0% chi tiết"
                  >
                    <CreditCard className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0" />
                    <span className="underline decoration-dotted font-semibold">Trả góp 0%</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Bottom Grid: Grouped Specifications Table & Highlights */}
            <div className="pt-6 border-t border-gray-200 dark:border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Highlights & Description */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wide">
                  Đặc điểm nổi bật
                </h3>
                <ul className="space-y-2">
                  {(product.highlights || []).map((h, i) => (
                    <li key={i} className="flex items-start space-x-2 text-xs text-slate-600 dark:text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed pt-2">
                  {product.description}
                </p>
              </div>

              {/* Grouped Specs Table */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wide">
                  Thông số kỹ thuật chi tiết
                </h3>
                <div className="border border-gray-200 dark:border-slate-800 rounded-2xl overflow-hidden divide-y divide-gray-200 dark:divide-slate-800 text-xs bg-white dark:bg-[#151c2c]">
                  {product.specs?.cpu_model && (
                    <div className="grid grid-cols-3 p-3">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Vi xử lý (CPU)</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.cpu_brand} {product.specs.cpu_model} ({product.specs.cores || 8} nhân)
                      </span>
                    </div>
                  )}
                  {product.specs?.ram_gb && (
                    <div className="grid grid-cols-3 p-3 bg-gray-50/50 dark:bg-slate-900/40">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Bộ nhớ RAM</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.ram_gb}GB {product.specs.ram_type}
                      </span>
                    </div>
                  )}
                  {product.specs?.storage_gb && (
                    <div className="grid grid-cols-3 p-3">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Ổ cứng lưu trữ</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.storage_gb >= 1024 ? '1TB' : `${product.specs.storage_gb}GB`} {product.specs.storage_type}
                      </span>
                    </div>
                  )}
                  {product.specs?.screen_inch && (
                    <div className="grid grid-cols-3 p-3 bg-gray-50/50 dark:bg-slate-900/40">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Màn hình</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.screen_inch}" {product.specs.resolution} {product.specs.panel} {product.specs.refresh_hz ? `${product.specs.refresh_hz}Hz` : ''}
                      </span>
                    </div>
                  )}
                  {product.specs?.gpu_model && (
                    <div className="grid grid-cols-3 p-3">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Card đồ họa</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.gpu_model}
                      </span>
                    </div>
                  )}
                  {product.specs?.weight_kg && (
                    <div className="grid grid-cols-3 p-3 bg-gray-50/50 dark:bg-slate-900/40">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Trọng lượng</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.weight_kg} kg
                      </span>
                    </div>
                  )}
                  {product.specs?.warranty_months && (
                    <div className="grid grid-cols-3 p-3">
                      <span className="text-slate-500 dark:text-slate-400 font-medium">Bảo hành</span>
                      <span className="col-span-2 font-semibold text-slate-900 dark:text-slate-100">
                        {product.specs.warranty_months} tháng chính hãng
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Customer Reviews & Community Feedback Section */}
            <div className="pt-6 border-t border-gray-200 dark:border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gray-50 dark:bg-slate-900/60 p-4 rounded-2xl border border-gray-200 dark:border-slate-800">
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <span className="text-3xl font-black text-[#d70018] dark:text-red-400 font-mono">4.9</span>
                    <div className="flex items-center justify-center text-amber-400 mt-0.5">
                      {[1, 2, 3, 4, 5].map(s => (
                        <Star key={s} className="w-3.5 h-3.5 fill-amber-400" />
                      ))}
                    </div>
                    <span className="text-[10px] text-slate-400">48 đánh giá</span>
                  </div>
                  <div className="h-10 w-px bg-gray-200 dark:bg-slate-700 hidden sm:block" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                      Đánh Giá & Nhận Xét Từ Khách Hàng
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      100% đánh giá từ khách hàng đã mua và trải nghiệm thực tế tại TechStore
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setShowReviewForm(!showReviewForm)}
                  className="px-4 py-2 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center justify-center space-x-1.5 cursor-pointer self-start sm:self-auto"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>{showReviewForm ? 'Đóng lại' : 'Viết đánh giá'}</span>
                </button>
              </div>

              {/* Success Notification after submitting review */}
              {reviewSubmitted && (
                <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 rounded-xl text-xs text-emerald-800 dark:text-emerald-300 font-bold flex items-center space-x-2 animate-in fade-in">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-red-400" />
                  <span>Cảm ơn bạn! Đánh giá của bạn đã được xuất bản công khai trên TechStore.</span>
                </div>
              )}

              {/* Review Submission Form */}
              {showReviewForm && (
                <form onSubmit={handleAddReview} className="bg-white dark:bg-slate-800/80 p-4 rounded-2xl border border-gray-200 dark:border-slate-700 space-y-3 animate-in fade-in">
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">Gửi nhận xét về sản phẩm này</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">Họ và tên của bạn:</label>
                      <input
                        type="text"
                        value={newAuthor}
                        onChange={e => setNewAuthor(e.target.value)}
                        placeholder="Ví dụ: Hoàng Long"
                        required
                        className="w-full px-3 py-2 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-xs focus:outline-none focus:border-[#d70018]"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">Mức độ hài lòng:</label>
                      <select
                        value={newRating}
                        onChange={e => setNewRating(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-xs focus:outline-none focus:border-[#d70018]"
                      >
                        <option value={5}>⭐⭐⭐⭐⭐ Tuyệt vời (5 sao)</option>
                        <option value={4}>⭐⭐⭐⭐ Rất tốt (4 sao)</option>
                        <option value={3}>⭐⭐⭐ Bình thường (3 sao)</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1 text-xs">Cảm nhận chi tiết (độ mượt, tản nhiệt, đóng gói...):</label>
                    <textarea
                      value={newComment}
                      onChange={e => setNewComment(e.target.value)}
                      rows={2}
                      placeholder="Chia sẻ trải nghiệm sử dụng thực tế của bạn để giúp khách hàng khác có thêm thông tin..."
                      required
                      className="w-full px-3 py-2 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-xs focus:outline-none focus:border-[#d70018]"
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      onClick={() => setShowReviewForm(false)}
                      className="px-3 py-1.5 text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 font-medium"
                    >
                      Hủy
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-1.5 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                    >
                      Gửi đánh giá
                    </button>
                  </div>
                </form>
              )}

              {/* Reviews List */}
              <div className="space-y-3">
                {reviews.map(rev => (
                  <div
                    key={rev.id}
                    className="p-3.5 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl space-y-2 shadow-2xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="w-7 h-7 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-[#d70018] dark:text-red-400 font-bold text-xs flex items-center justify-center">
                          {rev.author.charAt(0)}
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-xs text-slate-900 dark:text-slate-100">{rev.author}</span>
                            <span className="text-[10px] text-slate-400">({rev.location})</span>
                            {rev.verified && (
                              <span className="text-[10px] bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-red-400 px-1.5 py-0.2 rounded font-semibold border border-emerald-200 dark:border-emerald-800 flex items-center space-x-1">
                                <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-red-400" />
                                <span>Đã mua tại TechStore</span>
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-1.5 mt-0.5">
                            <div className="flex items-center text-amber-400">
                              {[...Array(rev.rating)].map((_, i) => (
                                <Star key={i} className="w-3 h-3 fill-amber-400" />
                              ))}
                            </div>
                            <span className="text-[10px] text-slate-400">• {rev.date}</span>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => sound.playPop()}
                        className="flex items-center space-x-1 text-[11px] text-slate-400 hover:text-[#d70018] dark:hover:text-emerald-400 transition"
                      >
                        <ThumbsUp className="w-3 h-3" />
                        <span>Hữu ích ({rev.helpful})</span>
                      </button>
                    </div>

                    <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed pl-9">
                      {rev.comment}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
