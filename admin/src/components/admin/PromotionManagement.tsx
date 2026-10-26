import React, { useState, useEffect } from 'react';
import {
  Tag,
  Plus,
  Percent,
  DollarSign,
  Calendar,
  ToggleLeft,
  ToggleRight,
  Trash2,
  CheckCircle2,
  Clock,
  Sparkles,
  Zap,
  Gift,
  RefreshCw
} from 'lucide-react';
import { fetchAdminPromotions, createAdminPromotion, toggleAdminPromotion, deleteAdminPromotion } from '../../services/api';

export const PromotionManagement: React.FC = () => {
  const [promotions, setPromotions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  const [formData, setFormData] = useState({
    name: 'TECH500',
    type: 'fixed_amount',
    value: 500000,
    description: 'Giảm ngay 500k cho đơn hàng từ 15 triệu',
    startsAt: new Date().toISOString().slice(0, 10),
    endsAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    isFlashSale: false
  });

  const loadData = () => {
    setLoading(true);
    fetchAdminPromotions()
      .then(data => setPromotions(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreatePromo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.value) return;
    try {
      await createAdminPromotion({
        ...formData,
        startsAt: new Date(formData.startsAt).toISOString(),
        endsAt: new Date(formData.endsAt).toISOString()
      });
      setShowAddModal(false);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggle = async (id: string) => {
    try {
      await toggleAdminPromotion(id);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (window.confirm(`Xác nhận xóa mã khuyến mãi "${name}"?`)) {
      try {
        await deleteAdminPromotion(id);
        loadData();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-slate-100 tracking-tight flex items-center space-x-2">
            <Tag className="w-5 h-5 text-emerald-600" />
            <span>Quản Lý Mã Giảm Giá & Chiến Dịch Khuyến Mãi</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Quản trị mã coupon áp dụng tại giỏ hàng và thanh toán (`TECH500`, `GAMING2026`, `FREESHIP`)
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-[#059669] hover:bg-[#047857] text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm transition active:scale-95 cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Tạo Mã Coupon Mới</span>
        </button>
      </div>

      {/* Promotions Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Đang tải danh sách khuyến mãi...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {promotions.map(promo => {
            const isActive = new Date(promo.endsAt) > new Date();
            return (
              <div
                key={promo.id}
                className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs space-y-3 relative overflow-hidden"
              >
                {/* Active indicator bar */}
                <div className={`absolute top-0 left-0 right-0 h-1 ${isActive ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-700'}`} />

                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 rounded-xl font-black text-sm">
                      {promo.name}
                    </div>
                    {promo.isFlashSale && (
                      <span className="px-1.5 py-0.5 bg-red-600 text-white font-black text-[9px] rounded">FLASH SALE</span>
                    )}
                  </div>

                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    isActive
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                      : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                  }`}>
                    {isActive ? 'Đang hiệu lực' : 'Đã hết hạn'}
                  </span>
                </div>

                <div>
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs">
                    Giảm: {promo.type === 'percentage' ? `${promo.value}%` : `${new Intl.NumberFormat('vi-VN').format(promo.value)}₫`}
                  </h4>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                    {promo.description || 'Ưu đãi đặc biệt dành cho khách hàng TechStore'}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Hạn: {new Date(promo.endsAt).toLocaleDateString('vi-VN')}</span>
                  </div>

                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleToggle(promo.id)}
                      className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-600 dark:text-slate-300 transition"
                      title={isActive ? 'Tạm ngưng mã' : 'Kích hoạt lại'}
                    >
                      {isActive ? <ToggleRight className="w-5 h-5 text-emerald-600" /> : <ToggleLeft className="w-5 h-5 text-slate-400" />}
                    </button>
                    <button
                      onClick={() => handleDelete(promo.id, promo.name)}
                      className="p-1 hover:bg-rose-50 dark:hover:bg-rose-950/60 rounded text-rose-600 dark:text-rose-400 transition"
                      title="Xóa mã"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Coupon Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#151c2c] rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-150 dark:border-slate-800 pb-3">
              <h3 className="text-base font-black text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                <Tag className="w-4 h-4 text-emerald-600" />
                <span>Tạo Mã Coupon Khuyến Mãi Mới</span>
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreatePromo} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Mã Coupon (Viết liền hoa) *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value.toUpperCase() })}
                  placeholder="VD: GAMING2026, TECH1000..."
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 font-mono font-bold text-slate-900 dark:text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Loại Giảm</label>
                  <select
                    value={formData.type}
                    onChange={e => setFormData({ ...formData, type: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  >
                    <option value="fixed_amount">Số tiền cố định (VNĐ)</option>
                    <option value="percentage">Phần trăm (%)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Giá Trị Giảm *</label>
                  <input
                    type="number"
                    required
                    value={formData.value}
                    onChange={e => setFormData({ ...formData, value: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Mô Tả Điều Kiện Áp Dụng</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  placeholder="VD: Giảm 500k cho đơn từ 15 triệu..."
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Ngày Bắt Đầu</label>
                  <input
                    type="date"
                    value={formData.startsAt}
                    onChange={e => setFormData({ ...formData, startsAt: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Ngày Kết Thúc</label>
                  <input
                    type="date"
                    value={formData.endsAt}
                    onChange={e => setFormData({ ...formData, endsAt: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-150 dark:border-slate-800 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 rounded-xl font-bold text-slate-700 dark:text-slate-300 transition"
                >
                  Hủy Bỏ
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#059669] hover:bg-[#047857] text-white rounded-xl font-bold transition shadow-sm"
                >
                  Kích Hoạt Mã
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
