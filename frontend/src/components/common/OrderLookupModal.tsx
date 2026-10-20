import React, { useState } from 'react';
import {
  X,
  Search,
  PackageCheck,
  CheckCircle2,
  Clock,
  Truck,
  AlertCircle
} from 'lucide-react';
import { lookupOrder } from '../../services/api';
import { Order } from '../../types';

interface OrderLookupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OrderLookupModal: React.FC<OrderLookupModalProps> = ({
  isOpen,
  onClose
}) => {
  const [phone, setPhone] = useState('');
  const [orderCode, setOrderCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone.trim() || !orderCode.trim()) {
      setError('Vui lòng nhập cả số điện thoại và mã đơn hàng');
      return;
    }

    setLoading(true);
    setError(null);
    setOrder(null);

    try {
      const res = await lookupOrder(phone, orderCode);
      if (res.success && res.data) {
        setOrder(res.data);
      } else {
        setError(res.message || 'Không tìm thấy đơn hàng. Vui lòng kiểm tra lại thông tin.');
      }
    } catch (err: any) {
      console.error(err);
      setError('Lỗi khi tra cứu đơn hàng, vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#151c2c] rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 relative text-slate-800 dark:text-slate-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2.5 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-[#059669] text-white flex items-center justify-center font-bold shadow-sm shadow-emerald-500/20">
            <PackageCheck className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Tra Cứu Tiến Độ Đơn Hàng</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Nhập số điện thoại và mã đơn hàng đã nhận</p>
          </div>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mt-4 space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Số điện thoại:</label>
              <input
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="Ví dụ: 0981234567"
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-[#059669] dark:focus:border-emerald-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Mã đơn hàng:</label>
              <input
                type="text"
                value={orderCode}
                onChange={e => setOrderCode(e.target.value)}
                placeholder="Ví dụ: ORD-2026-1005"
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-[#059669] dark:focus:border-emerald-500 focus:outline-none uppercase font-mono"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-[#059669] hover:bg-[#047857] disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white font-bold rounded-xl text-xs flex items-center justify-center space-x-1.5 transition shadow-xs active:scale-95"
          >
            <Search className="w-3.5 h-3.5" />
            <span>{loading ? 'Đang tra cứu dữ liệu...' : 'Tìm kiếm đơn hàng'}</span>
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 rounded-lg text-xs text-red-700 dark:text-red-300 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Order Details Result */}
        {order && (
          <div className="mt-5 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4 text-xs">
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm">{order.orderCode}</span>
                <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
                  Người nhận: <strong className="text-slate-800 dark:text-slate-200">{order.customerName}</strong> ({order.customerPhone})
                </p>
                <p className="text-slate-500 dark:text-slate-400 text-[11px] truncate">{order.customerAddress}, {order.customerCity}</p>
              </div>
              <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 capitalize border border-emerald-200 dark:border-emerald-800">
                {order.status === 'new' ? 'Mới tạo' : order.status === 'confirmed' ? 'Đã duyệt' : order.status === 'shipping' ? 'Đang giao' : 'Hoàn tất'}
              </span>
            </div>

            {/* Items */}
            <div className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-lg space-y-2 border border-slate-100 dark:border-slate-800">
              <span className="font-bold text-slate-700 dark:text-slate-300 block text-[11px]">Sản phẩm trong đơn:</span>
              {order.items.map((it, idx) => (
                <div key={idx} className="flex justify-between text-slate-800 dark:text-slate-200">
                  <span>{it.productName} <strong className="text-slate-400">x{it.qty}</strong></span>
                  <span className="font-bold">{new Intl.NumberFormat('vi-VN').format(it.price * it.qty)}₫</span>
                </div>
              ))}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-between font-bold text-slate-900 dark:text-slate-100 text-sm">
                <span>Tổng cộng:</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-black">{new Intl.NumberFormat('vi-VN').format(order.total)}₫</span>
              </div>
            </div>

            {/* Timeline */}
            <div className="space-y-2 pt-1">
              <span className="font-bold text-slate-700 dark:text-slate-300 block text-[11px]">Lịch sử tiến độ:</span>
              <div className="space-y-2 pl-3 border-l-2 border-emerald-300 dark:border-emerald-700 text-[11px]">
                {order.statusTimeline?.map((t, idx) => (
                  <div key={idx} className="relative pl-3">
                    <span className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-emerald-600 dark:bg-emerald-400 ring-2 ring-white dark:ring-slate-900" />
                    <p className="font-bold text-slate-800 dark:text-slate-200">{t.note || t.status}</p>
                    <p className="text-slate-400 text-[10px]">{new Date(t.timestamp).toLocaleString('vi-VN')}</p>
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
