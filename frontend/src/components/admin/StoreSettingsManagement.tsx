import React, { useState, useEffect } from 'react';
import {
  Settings,
  Store,
  Phone,
  Truck,
  MapPin,
  Save,
  CheckCircle2,
  Bell,
  DollarSign,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { fetchAdminSettings, updateAdminSettings } from '../../services/api';

export const StoreSettingsManagement: React.FC = () => {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    fetchAdminSettings()
      .then(data => setSettings(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await updateAdminSettings(settings);
      if (res.success) {
        setSettings(res.data);
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 3000);
      }
    } catch (err) {
      console.error(err);
      alert('Không thể lưu cấu hình, vui lòng thử lại.');
    }
  };

  if (loading || !settings) {
    return <div className="p-12 text-center text-xs text-slate-400">Đang tải cấu hình hệ thống...</div>;
  }

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-slate-100 tracking-tight flex items-center space-x-2">
            <Settings className="w-5 h-5 text-emerald-600" />
            <span>Cấu Hình Cửa Hàng & Mạng Lưới Showroom</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Cập nhật Hotline, biểu ngữ thông báo chạy chữ Marquee, địa chỉ các Showroom và chính sách vận chuyển
          </p>
        </div>

        {savedSuccess && (
          <div className="px-3.5 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-bold flex items-center space-x-1.5 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Đã lưu cấu hình thành công!</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Brand & Hotline Settings Card */}
        <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-2xs space-y-4">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-2">
            <Store className="w-4 h-4 text-emerald-600" />
            <span>Thông Tin Thương Hiệu & Tổng Đài Hỗ Trợ</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Tên Chuỗi Cửa Hàng</label>
              <input
                type="text"
                value={settings.storeName}
                onChange={e => setSettings({ ...settings, storeName: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-bold"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Khẩu Hiệu / Slogan Định Vị</label>
              <input
                type="text"
                value={settings.slogan}
                onChange={e => setSettings({ ...settings, slogan: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Hotline Bán Hàng & Tư Vấn Build PC</label>
              <input
                type="text"
                value={settings.hotlineSales}
                onChange={e => setSettings({ ...settings, hotlineSales: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Hotline Bảo Hành & Khiếu Nại</label>
              <input
                type="text"
                value={settings.hotlineWarranty}
                onChange={e => setSettings({ ...settings, hotlineWarranty: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
              />
            </div>
          </div>
        </div>

        {/* Marquee & Shipping Card */}
        <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-2xs space-y-4">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-2">
            <Bell className="w-4 h-4 text-amber-500" />
            <span>Thông Báo Đầu Trang & Chính Sách Miễn Phí Vận Chuyển</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Nội Dung Thông Báo Marquee (Chạy trên thanh Header)</label>
              <input
                type="text"
                value={settings.marqueeText}
                onChange={e => setSettings({ ...settings, marqueeText: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Hạn Mức Miễn Phí Vận Chuyển (VNĐ)</label>
                <input
                  type="number"
                  value={settings.freeShippingThreshold}
                  onChange={e => setSettings({ ...settings, freeShippingThreshold: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Thuế VAT Tự Động (%)</label>
                <input
                  type="number"
                  value={settings.vatPercent}
                  onChange={e => setSettings({ ...settings, vatPercent: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Showrooms Addresses Card */}
        <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-2xs space-y-4">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-blue-600" />
            <span>Địa Chỉ & Hotline Các Chi Nhánh Showroom</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {settings.showrooms?.map((sr: any, idx: number) => (
              <div key={idx} className="p-3 bg-gray-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
                <input
                  type="text"
                  value={sr.name}
                  onChange={e => {
                    const next = [...settings.showrooms];
                    next[idx].name = e.target.value;
                    setSettings({ ...settings, showrooms: next });
                  }}
                  className="w-full font-bold text-slate-900 dark:text-slate-100 bg-transparent outline-none border-b border-dashed border-slate-300 dark:border-slate-600 pb-1"
                />
                <input
                  type="text"
                  value={sr.address}
                  onChange={e => {
                    const next = [...settings.showrooms];
                    next[idx].address = e.target.value;
                    setSettings({ ...settings, showrooms: next });
                  }}
                  className="w-full text-slate-600 dark:text-slate-300 bg-transparent outline-none text-[11px]"
                />
                <input
                  type="text"
                  value={sr.phone}
                  onChange={e => {
                    const next = [...settings.showrooms];
                    next[idx].phone = e.target.value;
                    setSettings({ ...settings, showrooms: next });
                  }}
                  className="w-full text-emerald-600 dark:text-emerald-400 font-mono font-bold bg-transparent outline-none text-[11px]"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2.5 bg-[#059669] hover:bg-[#047857] text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm transition active:scale-95 cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>Lưu Toàn Bộ Cấu Hình</span>
          </button>
        </div>
      </form>
    </div>
  );
};
