import React, { useState, useEffect } from 'react';
import {
  SlidersHorizontal,
  CheckCircle2,
  FileText,
  Printer,
  Search,
  Zap,
  Cpu,
  Clock,
  Download,
  AlertTriangle,
  ArrowRight,
  Phone,
  User,
  ShoppingBag,
  RefreshCw
} from 'lucide-react';
import { fetchAdminQuotations, updateAdminQuotationStatus } from '../../services/api';

export const QuotationManagement: React.FC = () => {
  const [quotations, setQuotations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuote, setSelectedQuote] = useState<any | null>(null);

  const loadData = () => {
    setLoading(true);
    fetchAdminQuotations()
      .then(data => {
        setQuotations(data);
        if (data.length > 0 && !selectedQuote) {
          setSelectedQuote(data[0]);
        }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApproveQuote = async (id: string) => {
    try {
      const res = await updateAdminQuotationStatus(id, 'approved');
      if (res.success && res.data) {
        setQuotations(prev => prev.map(q => q.id === id ? res.data : q));
        setSelectedQuote(res.data);
        alert(`Đã duyệt cấu hình ${res.data.id} thành công! Kỹ thuật viên có thể tiến hành ráp máy.`);
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
            <SlidersHorizontal className="w-5 h-5 text-emerald-600" />
            <span>Quản Lý Cấu Hình & Báo Giá Ráp PC Khách Hàng</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Duyệt cấu hình phần cứng do khách hàng tự build từ công cụ PC Builder trực tuyến
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
        <div className="p-12 text-center text-xs text-slate-400">Đang đồng bộ báo giá ráp máy...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Quotes List Column (lg:col-span-5) */}
          <div className="lg:col-span-5 space-y-3">
            <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Danh Sách Báo Giá Gần Đây ({quotations.length})
            </h3>

            <div className="space-y-2.5">
              {quotations.map(quote => {
                const isSelected = selectedQuote?.id === quote.id;
                return (
                  <div
                    key={quote.id}
                    onClick={() => setSelectedQuote(quote)}
                    className={`p-4 rounded-2xl border transition cursor-pointer ${
                      isSelected
                        ? 'bg-emerald-50/70 dark:bg-emerald-950/40 border-emerald-500 shadow-xs'
                        : 'bg-white dark:bg-[#151c2c] border-slate-200 dark:border-slate-800 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-black text-xs text-[#059669] dark:text-emerald-400">
                        {quote.id}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        quote.status === 'approved'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                          : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                      }`}>
                        {quote.status === 'approved' ? 'Đã thẩm định' : 'Chờ duyệt'}
                      </span>
                    </div>

                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs mt-1.5 line-clamp-1">
                      {quote.title}
                    </h4>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                      <span>KH: <strong>{quote.customerName}</strong> ({quote.phone})</span>
                      <span className="font-mono font-black text-red-600 dark:text-rose-400">
                        {new Intl.NumberFormat('vi-VN').format(quote.totalPrice)}₫
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quote Details Column (lg:col-span-7) */}
          <div className="lg:col-span-7">
            {selectedQuote ? (
              <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-150 dark:border-slate-800 pb-3">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono tracking-wider">Phiếu Thẩm Định Phần Cứng</span>
                    <h3 className="text-base font-black text-slate-900 dark:text-slate-100">
                      {selectedQuote.title}
                    </h3>
                  </div>

                  <button
                    onClick={() => window.print()}
                    className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center space-x-1.5 transition cursor-pointer"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>In Phiếu Kỹ Thuật</span>
                  </button>
                </div>

                {/* Specs Summary Row */}
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60">
                    <span className="text-[10px] text-slate-400 block">Công Suất Nguồn</span>
                    <strong className="text-[#059669] dark:text-emerald-400 text-sm font-mono">{selectedQuote.totalWatts}W</strong>
                  </div>
                  <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60">
                    <span className="text-[10px] text-slate-400 block">Nguồn Đề Xuất</span>
                    <strong className="text-blue-600 dark:text-blue-400 text-sm font-mono">{selectedQuote.recommendedPsu}</strong>
                  </div>
                  <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60">
                    <span className="text-[10px] text-slate-400 block">Tương Thích Socket</span>
                    <strong className="text-emerald-600 dark:text-emerald-400 text-sm font-mono">{selectedQuote.compatibilityScore}% Chuẩn</strong>
                  </div>
                </div>

                {/* Parts Table */}
                <div className="space-y-1.5">
                  <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    Linh Kiện Trong Cấu Hình ({selectedQuote.parts?.length || 0})
                  </h4>
                  <div className="divide-y divide-slate-100 dark:divide-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden text-xs">
                    {selectedQuote.parts?.map((part: any, idx: number) => (
                      <div key={idx} className="p-2.5 flex items-center justify-between bg-white dark:bg-[#151c2c]">
                        <div className="flex items-center space-x-2">
                          <span className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded font-bold text-[10px] min-w-16 text-center">
                            {part.type}
                          </span>
                          <span className="font-semibold text-slate-800 dark:text-slate-200">{part.name}</span>
                        </div>
                        <span className="font-mono font-bold text-red-600 dark:text-rose-400">
                          {new Intl.NumberFormat('vi-VN').format(part.price)}₫
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Total and Actions */}
                <div className="pt-3 border-t border-slate-150 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-500 dark:text-slate-400 block">Tổng Chi Phí Dự Tính</span>
                    <span className="text-lg font-black text-red-600 dark:text-rose-400 font-mono">
                      {new Intl.NumberFormat('vi-VN').format(selectedQuote.totalPrice)}₫
                    </span>
                  </div>

                  <button
                    onClick={() => handleApproveQuote(selectedQuote.id)}
                    disabled={selectedQuote.status === 'approved'}
                    className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm transition active:scale-95 cursor-pointer ${
                      selectedQuote.status === 'approved'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 cursor-default'
                        : 'bg-[#059669] hover:bg-[#047857] text-white'
                    }`}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{selectedQuote.status === 'approved' ? 'Đã Duyệt & Xuất Kho' : 'Duyệt Cấu Hình & Giữ Linh Kiện'}</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-xs text-slate-400">Chọn một báo giá bên trái để xem chi tiết linh kiện.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
