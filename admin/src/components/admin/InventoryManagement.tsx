import React, { useState, useEffect } from 'react';
import {
  Boxes,
  Plus,
  AlertTriangle,
  XCircle,
  CheckCircle2,
  Search,
  PackagePlus,
  RefreshCw
} from 'lucide-react';
import { fetchAdminInventory, createStockReceipt, formatProductImageUrl, DEFAULT_PRODUCT_FALLBACK_IMAGE } from '../../services/api';

export const InventoryManagement: React.FC = () => {
  const [inventoryList, setInventoryList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [receiptModal, setReceiptModal] = useState<{ variantId: string; productName: string; variantName: string } | null>(null);
  const [receiptQty, setReceiptQty] = useState(10);
  const [receiptNote, setReceiptNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadData = () => {
    setLoading(true);
    fetchAdminInventory()
      .then(data => setInventoryList(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateReceipt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!receiptModal || receiptQty <= 0) return;
    setSubmitting(true);
    try {
      await createStockReceipt({
        variantId: receiptModal.variantId,
        qty: receiptQty,
        note: receiptNote || 'Phiếu nhập bổ sung hàng hóa'
      });
      setReceiptModal(null);
      setReceiptQty(10);
      setReceiptNote('');
      loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const filtered = inventoryList.filter(item =>
    item.productName.toLowerCase().includes(search.toLowerCase()) ||
    item.categoryName.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight flex items-center space-x-2">
            <Boxes className="w-5 h-5 text-blue-600" />
            <span>Quản Lý Tồn Kho & Phiếu Nhập Hàng</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Theo dõi tồn khả dụng theo thời gian thực (Tồn thực tế trừ đơn đang giữ hàng)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Tìm theo tên máy, danh mục..."
              className="pl-8 pr-3 py-1.5 border border-slate-200 rounded-lg text-xs bg-white text-slate-900 focus:outline-none focus:border-blue-600"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
          </div>
          <button
            onClick={loadData}
            className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition"
            title="Tải lại dữ liệu"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Đang đồng bộ dữ liệu kho...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="p-3.5">Sản phẩm & Cấu hình</th>
                  <th className="p-3.5">SKU</th>
                  <th className="p-3.5 text-right">Giá vốn</th>
                  <th className="p-3.5 text-right">Giá bán</th>
                  <th className="p-3.5 text-center">Tồn thực tế</th>
                  <th className="p-3.5 text-center">Đang giữ</th>
                  <th className="p-3.5 text-center">Khả dụng</th>
                  <th className="p-3.5">Trạng thái kho</th>
                  <th className="p-3.5 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map(prod =>
                  prod.variants.map((v: any) => (
                    <tr key={v.id} className="hover:bg-slate-50/80 transition">
                      <td className="p-3.5 flex items-center space-x-3">
                        <img
                          src={formatProductImageUrl(prod.imageUrl)}
                          alt={prod.productName || ''}
                          onError={(e) => {
                            e.currentTarget.onerror = null;
                            e.currentTarget.src = DEFAULT_PRODUCT_FALLBACK_IMAGE;
                          }}
                          className="w-10 h-10 object-contain rounded bg-white p-0.5 border border-slate-200 dark:border-slate-700 flex-shrink-0"
                          loading="lazy"
                        />
                        <div>
                          <span className="font-bold text-slate-900 block">{prod.productName}</span>
                          <span className="text-[11px] text-slate-500">{v.name}</span>
                        </div>
                      </td>
                      <td className="p-3.5 font-mono text-slate-600">{v.sku}</td>
                      <td className="p-3.5 text-right font-medium text-slate-600">
                        {new Intl.NumberFormat('vi-VN').format(v.costPrice)}₫
                      </td>
                      <td className="p-3.5 text-right font-bold text-slate-900">
                        {new Intl.NumberFormat('vi-VN').format(v.price)}₫
                      </td>
                      <td className="p-3.5 text-center font-bold text-slate-900">{v.qtyOnHand}</td>
                      <td className="p-3.5 text-center text-amber-600 font-semibold">{v.qtyReserved}</td>
                      <td className="p-3.5 text-center font-black text-blue-700">{v.availableQty}</td>
                      <td className="p-3.5">
                        {v.isOutOfStock ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700">
                            <XCircle className="w-3 h-3" />
                            <span>Hết hàng</span>
                          </span>
                        ) : v.isLowStock ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Sắp hết</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Còn hàng</span>
                          </span>
                        )}
                      </td>
                      <td className="p-3.5 text-right">
                        <button
                          onClick={() => setReceiptModal({ variantId: v.id, productName: prod.productName, variantName: v.name })}
                          className="px-2.5 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded font-semibold text-xs flex items-center space-x-1 ml-auto transition"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Nhập hàng</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Stock Receipt Modal */}
      {receiptModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <PackagePlus className="w-4 h-4 text-blue-600" />
                <span>Tạo Phiếu Nhập Hàng Vào Kho</span>
              </h3>
              <button onClick={() => setReceiptModal(null)} className="text-slate-400 hover:text-slate-600">&times;</button>
            </div>

            <div>
              <p className="text-xs font-bold text-slate-800">{receiptModal.productName}</p>
              <p className="text-[11px] text-slate-500">{receiptModal.variantName}</p>
            </div>

            <form onSubmit={handleCreateReceipt} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Số lượng nhập thêm:</label>
                <input
                  type="number"
                  min="1"
                  value={receiptQty}
                  onChange={e => setReceiptQty(parseInt(e.target.value, 10) || 1)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm font-bold text-slate-900"
                  required
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Ghi chú phiếu nhập:</label>
                <input
                  type="text"
                  value={receiptNote}
                  onChange={e => setReceiptNote(e.target.value)}
                  placeholder="Ví dụ: Nhập lô hàng từ nhà phân phối Synnex FPT"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setReceiptModal(null)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg font-semibold hover:bg-slate-50"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold"
                >
                  {submitting ? 'Đang cập nhật...' : 'Xác nhận nhập kho'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
