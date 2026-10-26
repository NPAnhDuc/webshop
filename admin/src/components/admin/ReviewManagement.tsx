import React, { useState, useEffect } from 'react';
import {
  Star,
  MessageSquare,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
  User,
  Package,
  Calendar,
  ThumbsUp,
  RefreshCw
} from 'lucide-react';
import { fetchAdminReviews, toggleAdminReviewStatus, replyAdminReview } from '../../services/api';

export const ReviewManagement: React.FC = () => {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    fetchAdminReviews()
      .then(data => setReviews(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleStatus = async (id: string) => {
    try {
      const res = await toggleAdminReviewStatus(id);
      if (res.success && res.data) {
        setReviews(prev => prev.map(r => r.id === id ? res.data : r));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReply = async (id: string, customerName: string) => {
    const replyText = window.prompt(`Nhập nội dung phản hồi từ TechStore đến khách hàng ${customerName}:`);
    if (!replyText || !replyText.trim()) return;

    try {
      const res = await replyAdminReview(id, replyText.trim());
      if (res.success && res.data) {
        setReviews(prev => prev.map(r => r.id === id ? res.data : r));
        alert(`Đã gửi phản hồi thành công đến ${customerName}!`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-slate-100 tracking-tight flex items-center space-x-2">
            <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
            <span>Kiểm Duyệt & Quản Lý Đánh Giá Khách Hàng</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Duyệt nhận xét 5 sao và phản hồi thắc mắc kỹ thuật từ người mua hàng thực tế
          </p>
        </div>

        <button
          onClick={loadData}
          className="p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-50 transition self-start sm:self-auto cursor-pointer"
          title="Tải lại dữ liệu"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Đang tải danh sách đánh giá...</div>
      ) : (
        <div className="space-y-3">
          {reviews.map(review => {
            const isApproved = review.status === 'approved';
            return (
              <div
                key={review.id}
                className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center font-bold text-xs">
                      {review.customerName.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <strong className="text-slate-900 dark:text-slate-100 text-xs">{review.customerName}</strong>
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.2 rounded font-semibold">
                          Đã mua hàng
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 flex items-center space-x-1 mt-0.5">
                        <Package className="w-3 h-3" />
                        <span>Sản phẩm: <strong>{review.productName}</strong></span>
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    {/* Star Rating */}
                    <div className="flex items-center space-x-0.5 text-amber-500">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3.5 h-3.5 ${i < review.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-300 dark:text-slate-700'}`}
                        />
                      ))}
                    </div>

                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      isApproved
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                        : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                    }`}>
                      {isApproved ? 'Hiển thị công khai' : 'Đang ẩn'}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-850 dark:bg-slate-900/60 p-3 rounded-xl border border-slate-150 dark:border-slate-800/80 leading-relaxed">
                  "{review.comment}"
                </p>

                {review.reply && (
                  <div className="text-xs bg-emerald-50 dark:bg-emerald-950/40 p-2.5 rounded-xl border-l-2 border-[#059669] text-emerald-800 dark:text-emerald-300">
                    <strong className="block text-[11px] font-bold">Phản hồi của Cửa hàng:</strong>
                    <span>{review.reply}</span>
                  </div>
                )}

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-800">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Ngày gửi: {new Date(review.createdAt).toLocaleDateString('vi-VN')}</span>
                  </span>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleStatus(review.id)}
                      className="px-3 py-1 rounded-lg text-xs font-bold transition flex items-center space-x-1 cursor-pointer bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300"
                    >
                      {isApproved ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      <span>{isApproved ? 'Ẩn đánh giá' : 'Duyệt hiển thị'}</span>
                    </button>

                    <button
                      onClick={() => handleReply(review.id, review.customerName)}
                      className="px-3 py-1 rounded-lg text-xs font-bold transition flex items-center space-x-1 cursor-pointer bg-[#059669] hover:bg-[#047857] text-white"
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      <span>Trả lời khách</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
