import React, { useState, useEffect } from 'react';
import {
  Package,
  Plus,
  Search,
  Edit2,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  SlidersHorizontal,
  Flame,
  Award,
  Download,
  Filter,
  DollarSign,
  Zap,
  Tag,
  RefreshCw
} from 'lucide-react';
import { fetchAdminProducts, createAdminProduct, updateAdminProduct, deleteAdminProduct, formatProductImageUrl, DEFAULT_PRODUCT_FALLBACK_IMAGE } from '../../services/api';
import { Product } from '../../types';

export const ProductManagement: React.FC = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<any | null>(null);

  // New Product Form State
  const [formData, setFormData] = useState({
    name: '',
    categorySlug: 'laptop',
    brandName: 'ASUS',
    price: 15000000,
    originalPrice: 18000000,
    discountPercent: 15,
    imageUrl: 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80',
    description: '',
    isHot: true,
    hasInstallment0: true,
    initialQty: 15,
    specs: {
      cpu_model: 'Intel Core i5',
      ram_gb: 16,
      ram_type: 'DDR5',
      storage_gb: 512,
      gpu_model: 'RTX 4060',
      vram_gb: 8,
      panel: 'IPS',
      refresh_hz: 144,
      socket: 'LGA1700',
      chipset: 'B760',
      tdp_w: 65
    }
  });

  const loadData = () => {
    setLoading(true);
    fetchAdminProducts()
      .then(data => setProducts(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.price) return;
    try {
      await createAdminProduct(formData);
      setShowAddModal(false);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProduct) return;
    try {
      await updateAdminProduct(editingProduct.id, editingProduct);
      setEditingProduct(null);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteProduct = async (id: string, name: string) => {
    if (window.confirm(`Bạn có chắc chắn muốn xóa sản phẩm "${name}" khỏi hệ thống?`)) {
      try {
        await deleteAdminProduct(id);
        loadData();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const exportToCSV = () => {
    const headers = ['Mã ID', 'Tên Sản Phẩm', 'Danh Mục', 'Hãng', 'Giá Bán', 'Giá Gốc', 'Tồn Kho', 'Trạng Thái'];
    const rows = filteredProducts.map(p => [
      p.id,
      `"${p.name.replace(/"/g, '""')}"`,
      p.categorySlug,
      p.brandName,
      p.price,
      p.originalPrice || p.price,
      p.availableQty || 0,
      p.stockStatus || 'in_stock'
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `techstore_products_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) || p.brandName.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || p.categorySlug === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-black text-slate-900 dark:text-slate-100 tracking-tight flex items-center space-x-2">
            <Package className="w-5 h-5 text-emerald-600" />
            <span>Quản Lý Toàn Bộ Danh Mục Sản Phẩm</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Tổng cộng: <strong>{products.length}</strong> sản phẩm phần cứng & laptop trong cơ sở dữ liệu
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={exportToCSV}
            className="px-3.5 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-slate-300 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center space-x-1.5 shadow-2xs transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Xuất CSV</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-[#059669] hover:bg-[#047857] text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm transition active:scale-95 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Thêm Sản Phẩm Mới</span>
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
            placeholder="Tìm theo tên máy, hãng, mã sản phẩm..."
            className="w-full pl-9 pr-3 py-1.5 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-slate-100 outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center space-x-2 overflow-x-auto scrollbar-none">
          <Filter className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
          {[
            { id: 'all', label: 'Tất cả ngành' },
            { id: 'laptop', label: 'Laptop' },
            { id: 'pc', label: 'PC Gaming' },
            { id: 'cpu', label: 'CPU' },
            { id: 'vga', label: 'VGA' },
            { id: 'mainboard', label: 'Mainboard' },
            { id: 'ram', label: 'RAM' },
            { id: 'ssd', label: 'SSD' },
            { id: 'monitor', label: 'Màn hình' }
          ].map(c => (
            <button
              key={c.id}
              onClick={() => setCategoryFilter(c.id)}
              className={`px-3 py-1 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer border ${
                categoryFilter === c.id
                  ? 'bg-[#059669] text-white border-[#059669] shadow-xs'
                  : 'bg-white dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-emerald-500'
              }`}
            >
              {c.label}
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

      {/* Product Table */}
      <div className="bg-white dark:bg-[#151c2c] border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-2xs">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Đang đồng bộ danh mục sản phẩm...</div>
        ) : filteredProducts.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">Không tìm thấy sản phẩm phù hợp.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50/80 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Sản Phẩm</th>
                  <th className="py-3 px-3">Ngành & Hãng</th>
                  <th className="py-3 px-3">Giá Bán</th>
                  <th className="py-3 px-3">Tồn Kho</th>
                  <th className="py-3 px-3">Đặc Quyền</th>
                  <th className="py-3 px-4 text-right">Thao Tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-800 dark:text-slate-200">
                {filteredProducts.map(p => (
                  <tr key={p.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 flex items-center space-x-3">
                      <img
                        src={formatProductImageUrl(p.imageUrl)}
                        alt={p.name}
                        onError={(e) => {
                          e.currentTarget.onerror = null;
                          e.currentTarget.src = DEFAULT_PRODUCT_FALLBACK_IMAGE;
                        }}
                        className="w-11 h-11 object-contain rounded-lg border border-slate-200 dark:border-slate-700 bg-white p-1 flex-shrink-0"
                        loading="lazy"
                      />
                      <div className="min-w-0 max-w-sm">
                        <p className="font-bold text-slate-900 dark:text-slate-100 truncate" title={p.name}>
                          {p.name}
                        </p>
                        <div className="flex items-center space-x-1 mt-0.5 text-[10px] text-slate-400">
                          {p.specs.cpu_model && <span>{p.specs.cpu_model}</span>}
                          {p.specs.socket && <span>• {p.specs.socket}</span>}
                          {p.specs.vram_gb && <span>• {p.specs.vram_gb}GB VRAM</span>}
                          {p.specs.panel && <span>• {p.specs.panel}</span>}
                        </div>
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <span className="inline-block px-2 py-0.5 bg-emerald-50 dark:bg-emerald-950/60 text-[#059669] dark:text-emerald-400 rounded-md font-bold uppercase text-[10px] border border-emerald-200 dark:border-emerald-800/60">
                        {p.categorySlug}
                      </span>
                      <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 mt-0.5">{p.brandName}</p>
                    </td>

                    <td className="py-3 px-3">
                      <p className="font-mono font-black text-red-600 dark:text-rose-400 text-xs">
                        {new Intl.NumberFormat('vi-VN').format(p.price)}₫
                      </p>
                      {p.originalPrice && p.originalPrice > p.price && (
                        <p className="font-mono text-[10px] text-slate-400 line-through">
                          {new Intl.NumberFormat('vi-VN').format(p.originalPrice)}₫
                        </p>
                      )}
                    </td>

                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        (p.availableQty || 0) <= 2
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                          : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                      }`}>
                        <span>{p.availableQty || 15} máy</span>
                      </span>
                    </td>

                    <td className="py-3 px-3 space-x-1">
                      {p.isHot && (
                        <span className="px-1.5 py-0.5 bg-yellow-400 text-slate-950 font-black text-[9px] rounded">HOT</span>
                      )}
                      {p.hasInstallment0 && (
                        <span className="px-1.5 py-0.5 bg-blue-600 text-white font-bold text-[9px] rounded">0%</span>
                      )}
                    </td>

                    <td className="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
                      <button
                        onClick={() => setEditingProduct({ ...p })}
                        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-300 transition"
                        title="Chỉnh sửa sản phẩm"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteProduct(p.id, p.name)}
                        className="p-1.5 hover:bg-rose-50 dark:hover:bg-rose-950/60 rounded-lg text-rose-600 dark:text-rose-400 transition"
                        title="Xóa sản phẩm"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-[#151c2c] rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-150 dark:border-slate-800 pb-3">
              <h3 className="text-base font-black text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                <Plus className="w-4 h-4 text-emerald-600" />
                <span>Thêm Sản Phẩm Mới Vào Hệ Thống</span>
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreateProduct} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="col-span-2">
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Tên Sản Phẩm *</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    placeholder="VD: Laptop Asus TUF Gaming A15 FA506NF..."
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Ngành Hàng</label>
                  <select
                    value={formData.categorySlug}
                    onChange={e => setFormData({ ...formData, categorySlug: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  >
                    <option value="laptop">Laptop</option>
                    <option value="pc">PC Gaming</option>
                    <option value="cpu">CPU Vi xử lý</option>
                    <option value="vga">VGA Card đồ họa</option>
                    <option value="mainboard">Mainboard</option>
                    <option value="ram">RAM</option>
                    <option value="ssd">Ổ cứng SSD</option>
                    <option value="psu">Nguồn PSU</option>
                    <option value="case">Vỏ Case</option>
                    <option value="monitor">Màn hình</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Thương Hiệu</label>
                  <input
                    type="text"
                    value={formData.brandName}
                    onChange={e => setFormData({ ...formData, brandName: e.target.value })}
                    placeholder="VD: ASUS, MSI, Intel, Lenovo..."
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Giá Bán (VNĐ) *</label>
                  <input
                    type="number"
                    required
                    value={formData.price}
                    onChange={e => setFormData({ ...formData, price: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Giá Gốc Niêm Yết (VNĐ)</label>
                  <input
                    type="number"
                    value={formData.originalPrice}
                    onChange={e => setFormData({ ...formData, originalPrice: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Link Ảnh Sản Phẩm</label>
                  <input
                    type="text"
                    value={formData.imageUrl}
                    onChange={e => setFormData({ ...formData, imageUrl: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  />
                  {formData.imageUrl && (
                    <div className="mt-2 flex items-center space-x-3 p-2 bg-slate-900/50 rounded-xl border border-slate-700">
                      <img
                        src={formatProductImageUrl(formData.imageUrl)}
                        alt="Preview"
                        onError={(e) => {
                          e.currentTarget.onerror = null;
                          e.currentTarget.src = DEFAULT_PRODUCT_FALLBACK_IMAGE;
                        }}
                        className="w-12 h-12 object-contain rounded-lg bg-white p-1 border border-slate-700 shrink-0"
                      />
                      <span className="text-[11px] text-slate-400">Xem trước ảnh đại diện sản phẩm</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Số Lượng Nhập Đầu (Qty)</label>
                  <input
                    type="number"
                    value={formData.initialQty}
                    onChange={e => setFormData({ ...formData, initialQty: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div className="flex items-center space-x-4 pt-4">
                  <label className="flex items-center space-x-1.5 cursor-pointer font-bold text-slate-800 dark:text-slate-200">
                    <input
                      type="checkbox"
                      checked={formData.isHot}
                      onChange={e => setFormData({ ...formData, isHot: e.target.checked })}
                      className="rounded text-emerald-600 focus:ring-emerald-500"
                    />
                    <span>Gắn nhãn HOT</span>
                  </label>

                  <label className="flex items-center space-x-1.5 cursor-pointer font-bold text-slate-800 dark:text-slate-200">
                    <input
                      type="checkbox"
                      checked={formData.hasInstallment0}
                      onChange={e => setFormData({ ...formData, hasInstallment0: e.target.checked })}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span>Hỗ trợ Trả Góp 0%</span>
                  </label>
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
                  Lưu Sản Phẩm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {editingProduct && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-[#151c2c] rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-150 dark:border-slate-800 pb-3">
              <h3 className="text-base font-black text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                <Edit2 className="w-4 h-4 text-emerald-600" />
                <span>Chỉnh Sửa Thông Tin Sản Phẩm</span>
              </h3>
              <button
                onClick={() => setEditingProduct(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleUpdateProduct} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Tên Sản Phẩm</label>
                <input
                  type="text"
                  required
                  value={editingProduct.name}
                  onChange={e => setEditingProduct({ ...editingProduct, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Giá Bán (VNĐ)</label>
                  <input
                    type="number"
                    required
                    value={editingProduct.price}
                    onChange={e => setEditingProduct({ ...editingProduct, price: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Giá Gốc (VNĐ)</label>
                  <input
                    type="number"
                    value={editingProduct.originalPrice || ''}
                    onChange={e => setEditingProduct({ ...editingProduct, originalPrice: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Số Lượng Tồn Kho Thực Tế</label>
                <input
                  type="number"
                  value={editingProduct.stockQty !== undefined ? editingProduct.stockQty : (editingProduct.variants?.[0]?.inventory?.qtyOnHand ?? 15)}
                  onChange={e => setEditingProduct({ ...editingProduct, stockQty: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 text-slate-900 dark:text-slate-100 font-mono"
                />
              </div>

              <div className="flex items-center space-x-4 pt-2">
                <label className="flex items-center space-x-1.5 cursor-pointer font-bold text-slate-800 dark:text-slate-200">
                  <input
                    type="checkbox"
                    checked={editingProduct.isHot || false}
                    onChange={e => setEditingProduct({ ...editingProduct, isHot: e.target.checked })}
                    className="rounded text-emerald-600 focus:ring-emerald-500"
                  />
                  <span>Gắn nhãn HOT</span>
                </label>

                <label className="flex items-center space-x-1.5 cursor-pointer font-bold text-slate-800 dark:text-slate-200">
                  <input
                    type="checkbox"
                    checked={editingProduct.hasInstallment0 || false}
                    onChange={e => setEditingProduct({ ...editingProduct, hasInstallment0: e.target.checked })}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span>Hỗ trợ Trả Góp 0%</span>
                </label>
              </div>

              <div className="pt-3 border-t border-slate-150 dark:border-slate-800 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setEditingProduct(null)}
                  className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 rounded-xl font-bold text-slate-700 dark:text-slate-300 transition"
                >
                  Hủy Bỏ
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#059669] hover:bg-[#047857] text-white rounded-xl font-bold transition shadow-sm"
                >
                  Cập Nhật Thay Đổi
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
