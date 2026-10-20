import React from 'react';
import { X, Sparkles, ShoppingCart, Check, Minus } from 'lucide-react';
import { Product } from '../../types';
import { useCart } from '../../context/CartContext';

interface ComparisonModalProps {
  products: Product[];
  isOpen: boolean;
  onClose: () => void;
  onAskBotCompare: (products: Product[]) => void;
}

export const ComparisonModal: React.FC<ComparisonModalProps> = ({
  products,
  isOpen,
  onClose,
  onAskBotCompare
}) => {
  const { addToCart } = useCart();
  if (!isOpen || products.length === 0) return null;

  // Comparison attributes to compare
  const specsRows = [
    { label: 'Giá bán chính thức', key: 'price', format: (p: Product) => `${new Intl.NumberFormat('vi-VN').format(p.price)}₫` },
    { label: 'Màn hình', key: 'screen', format: (p: Product) => `${p.specs.screen_inch}" ${p.specs.resolution || ''} ${p.specs.panel || ''} ${p.specs.refresh_hz ? `${p.specs.refresh_hz}Hz` : ''}` },
    { label: 'Công nghệ màn', key: 'panel', format: (p: Product) => p.specs.panel || 'IPS' },
    { label: 'Vi xử lý (CPU)', key: 'cpu', format: (p: Product) => `${p.specs.cpu_brand || ''} ${p.specs.cpu_model || ''}` },
    { label: 'Bộ nhớ RAM', key: 'ram', format: (p: Product) => p.specs.ram_gb ? `${p.specs.ram_gb}GB ${p.specs.ram_type || ''}` : 'Chưa rõ' },
    { label: 'Ổ cứng lưu trữ', key: 'storage', format: (p: Product) => p.specs.storage_gb ? `${p.specs.storage_gb >= 1024 ? '1TB' : `${p.specs.storage_gb}GB`} ${p.specs.storage_type || ''}` : 'Chưa rõ' },
    { label: 'Card đồ họa (GPU)', key: 'gpu', format: (p: Product) => p.specs.gpu_model || 'Đồ họa tích hợp' },
    { label: 'Trọng lượng', key: 'weight', format: (p: Product) => p.specs.weight_kg ? `${p.specs.weight_kg} kg` : 'N/A' },
    { label: 'Bảo hành chính hãng', key: 'warranty', format: (p: Product) => `${p.specs.warranty_months || 12} tháng` }
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200 text-slate-800 dark:text-slate-100">
      <div className="bg-white dark:bg-[#151c2c] rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200 dark:border-slate-800 relative flex flex-col">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between sticky top-0 bg-white dark:bg-[#151c2c] z-20">
          <div>
            <h2 className="text-base sm:text-lg font-black text-slate-900 dark:text-slate-100">
              Bảng So Sánh Chi Tiết Sản Phẩm ({products.length})
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Hệ thống tự động đối chiếu các điểm khác biệt giữa các dòng máy
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => onAskBotCompare(products)}
              className="px-3.5 py-2 bg-[#059669] hover:bg-[#047857] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-xs transition cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-yellow-300 dark:text-emerald-400" />
              <span>Hỏi AI Tóm Tắt Khác Biệt</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Table */}
        <div className="p-4 sm:p-6 overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            {/* Header Columns: Products info */}
            <thead>
              <tr className="border-b-2 border-gray-200 dark:border-slate-800">
                <th className="p-3 w-40 text-slate-400 dark:text-slate-500 font-semibold uppercase text-[11px]">Tiêu chí so sánh</th>
                {products.map(p => (
                  <th key={p.id} className="p-3 text-center align-top min-w-[200px]">
                    <img src={p.imageUrl} alt={p.name} className="w-24 h-24 object-contain mx-auto mb-2 border border-gray-150 dark:border-slate-700 rounded-lg p-1 bg-white dark:bg-slate-800" />
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-xs line-clamp-2 leading-snug">{p.name}</h3>
                    <div className="mt-2 text-sm font-black text-[#059669] dark:text-emerald-400 font-mono">
                      {new Intl.NumberFormat('vi-VN').format(p.price)}₫
                    </div>
                    <button
                      onClick={() => addToCart(p)}
                      className="mt-2.5 w-full py-1.5 bg-[#059669] hover:bg-[#047857] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white rounded-xl font-bold text-[11px] flex items-center justify-center space-x-1 transition shadow-xs cursor-pointer"
                    >
                      <ShoppingCart className="w-3 h-3" />
                      <span>Chọn mua</span>
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
              {specsRows.map(row => {
                const values = products.map(p => row.format(p));
                const isDifferent = new Set(values).size > 1;

                return (
                  <tr key={row.key} className={`transition ${isDifferent ? 'bg-amber-50/60 dark:bg-amber-950/30' : 'hover:bg-gray-50 dark:hover:bg-slate-800/50'}`}>
                    <td className="p-3 font-semibold text-slate-700 dark:text-slate-300">
                      <span>{row.label}</span>
                      {isDifferent && (
                        <span className="ml-1 text-[10px] text-amber-700 dark:text-amber-300 font-bold bg-amber-100 dark:bg-amber-900/60 px-1.5 py-0.2 rounded">Khác</span>
                      )}
                    </td>
                    {products.map(p => (
                      <td key={p.id} className="p-3 text-center font-medium text-slate-800 dark:text-slate-200">
                        {row.format(p)}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
