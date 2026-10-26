import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Award,
  Crown,
  Phone,
  Mail,
  MapPin,
  ShoppingBag,
  DollarSign,
  Calendar,
  Filter,
  Download,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { fetchAdminCustomers } from '../../services/api';

export const CustomerManagement: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [tierFilter, setTierFilter] = useState('all');

  const loadData = () => {
    setLoading(true);
    fetchAdminCustomers()
      .then(data => setCustomers(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const exportCustomersCSV = () => {
    const headers = ['Mã KH', 'Tên Khách Hàng', 'Số Điện Thoại', 'Khu Vực', 'Tổng Đơn', 'Tổng Chi Tiêu', 'Hạng Thành Viên', 'Đơn Cuối'];
    const rows = filteredCustomers.map(c => [
      c.id,
      `"${c.name}"`,
      `"${c.phone}"`,
      `"${c.city || 'Chưa cập nhật'}"`,
      c.totalOrders,
      c.totalSpent,
      c.tier,
      c.lastOrderDate ? new Date(c.lastOrderDate).toLocaleDateString('vi-VN') : ''
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `techstore_customers_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredCustomers = customers.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) || c.phone.includes(search);
    const matchesTier = tierFilter === 'all' || c.tier === tierFilter;
    return matchesSearch && matchesTier;
  });

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-slate-100 tracking-tight flex items-center space-x-2">
            <Users className="w-5 h-5 text-emerald-600" />
            <span>Quản Lý Khách Hàng & Hạng Thành Viên T-Member</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Dữ liệu tích lũy điểm thưởng và phân hạng: T-Standard, T-VIP (&gt;30 triệu), T-Diamond (&gt;80 triệu)
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={exportCustomersCSV}
            className="px-3.5 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-slate-300 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center space-x-1.5 shadow-2xs transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Xuất Danh Sách CSV</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Tìm theo tên khách hàng hoặc số điện thoại..."
            className="w-full pl-9 pr-3 py-1.5 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-slate-100 outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
          {[
            { id: 'all', label: 'Tất cả hạng' },
            { id: 'T-Diamond', label: '💎 Kim Cương (>80Tr)' },
            { id: 'T-VIP', label: '⭐ VIP (>30Tr)' },
            { id: 'T-Standard', label: 'Tiêu chuẩn' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTierFilter(t.id)}
              className={`px-3 py-1 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer border ${
                tierFilter === t.id
                  ? 'bg-[#059669] text-white border-[#059669] shadow-xs'
                  : 'bg-white dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-emerald-500'
              }`}
            >
              {t.label}
            </button>
          ))}
          <button
            onClick={loadData}
            title="Tải lại"
            className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Customers Table */}
      <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-2xs">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Đang đồng bộ hồ sơ khách hàng...</div>
        ) : filteredCustomers.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">Không tìm thấy khách hàng nào.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50/80 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Khách Hàng</th>
                  <th className="py-3 px-3">Liên Hệ</th>
                  <th className="py-3 px-3">Hạng Thành Viên</th>
                  <th className="py-3 px-3">Số Đơn Hàng</th>
                  <th className="py-3 px-3">Tổng Chi Tiêu</th>
                  <th className="py-3 px-4 text-right">Lần Mua Cuối</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-800 dark:text-slate-200">
                {filteredCustomers.map(cust => (
                  <tr key={cust.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 flex items-center space-x-3">
                      <div className="w-9 h-9 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 flex items-center justify-center font-black text-xs flex-shrink-0">
                        {cust.name.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-bold text-slate-900 dark:text-slate-100">{cust.name}</p>
                        <p className="text-[10px] text-slate-400">{cust.city || 'Toàn quốc'}</p>
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <p className="font-mono font-bold text-slate-800 dark:text-slate-200">{cust.phone}</p>
                    </td>

                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[10px] font-black uppercase ${
                        cust.tier === 'T-Diamond'
                          ? 'bg-purple-100 text-purple-900 dark:bg-purple-950/80 dark:text-purple-300 border border-purple-300 dark:border-purple-800'
                          : cust.tier === 'T-VIP'
                          ? 'bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-300 dark:border-amber-800'
                          : 'bg-gray-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-gray-200 dark:border-slate-700'
                      }`}>
                        {cust.tier === 'T-Diamond' ? <Crown className="w-3 h-3 text-purple-600" /> : <Award className="w-3 h-3 text-amber-600" />}
                        <span>{cust.tier}</span>
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      <span className="font-bold text-slate-800 dark:text-slate-200">{cust.totalOrders} đơn</span>
                    </td>

                    <td className="py-3 px-3">
                      <span className="font-mono font-black text-red-600 dark:text-rose-400 text-xs">
                        {new Intl.NumberFormat('vi-VN').format(cust.totalSpent)}₫
                      </span>
                    </td>

                    <td className="py-3 px-4 text-right text-slate-400 font-mono text-[11px]">
                      {cust.lastOrderDate ? new Date(cust.lastOrderDate).toLocaleDateString('vi-VN') : 'Mới tạo'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
