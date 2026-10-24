import React, { useState } from 'react';
import {
  ArrowLeft,
  Home,
  Scale,
  Sparkles,
  ShoppingCart,
  Trash2,
  Check,
  Minus,
  Plus,
  ExternalLink,
  Zap,
  Flame,
  Award,
  Eye,
  CheckCircle2,
  ShieldCheck,
  Layers,
  Cpu,
  Monitor,
  HardDrive
} from 'lucide-react';
import { Product } from '../../types';
import { useCart } from '../../context/CartContext';
import { calculateGamingTelemetry } from '../../utils/hardwareBenchmarks';

interface ComparisonPageProps {
  products: Product[];
  onRemoveProduct: (productId: string) => void;
  onClearAll: () => void;
  onSelectProduct: (productSlugOrId: string) => void;
  onBackToHome: () => void;
  onToast: (title: string, message?: string, type?: 'success' | 'info' | 'warning') => void;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  products,
  onRemoveProduct,
  onClearAll,
  onSelectProduct,
  onBackToHome,
  onToast
}) => {
  const { addToCart } = useCart();
  const [onlyDifferences, setOnlyDifferences] = useState(false);

  const specsRows = [
    {
      category: 'Giá & Khuyến Mãi',
      icon: Zap,
      rows: [
        { label: 'Giá bán chính thức', key: 'price', format: (p: Product) => `${new Intl.NumberFormat('vi-VN').format(p.price)}₫` },
        { label: 'Giá gốc niêm yết', key: 'origPrice', format: (p: Product) => p.originalPrice ? `${new Intl.NumberFormat('vi-VN').format(p.originalPrice)}₫` : 'Không có' },
        { label: 'Mức giảm giá', key: 'discount', format: (p: Product) => p.discountPercent ? `Giảm ${p.discountPercent}%` : 'Giá chuẩn' },
        { label: 'Hỗ trợ trả góp 0%', key: 'installment0', format: (p: Product) => p.hasInstallment0 ? 'Có (0% lãi suất duyệt 15p)' : 'Trả góp tiêu chuẩn' }
      ]
    },
    {
      category: 'Màn Hình Hiển Thị',
      icon: Monitor,
      rows: [
        { label: 'Kích thước màn hình', key: 'screen_inch', format: (p: Product) => p.specs.screen_inch ? `${p.specs.screen_inch} inch` : 'Theo màn hình ngoài' },
        { label: 'Độ phân giải', key: 'resolution', format: (p: Product) => p.specs.resolution || 'FHD 1920x1080' },
        { label: 'Công nghệ tấm nền', key: 'panel', format: (p: Product) => p.specs.panel || 'IPS Anti-Glare' },
        { label: 'Tần số quét', key: 'refresh_hz', format: (p: Product) => p.specs.refresh_hz ? `${p.specs.refresh_hz}Hz` : '60Hz' }
      ]
    },
    {
      category: 'Vi Xử Lý & Đồ Họa',
      icon: Cpu,
      rows: [
        { label: 'Thương hiệu CPU', key: 'cpu_brand', format: (p: Product) => p.specs.cpu_brand || 'Intel / AMD' },
        { label: 'Model CPU chi tiết', key: 'cpu_model', format: (p: Product) => p.specs.cpu_model || 'Tiêu chuẩn' },
        { label: 'Số nhân / Số luồng', key: 'cores', format: (p: Product) => p.specs.cores ? `${p.specs.cores} Nhân` : 'Đa nhân' },
        { label: 'Card đồ họa (GPU)', key: 'gpu_model', format: (p: Product) => p.specs.gpu_model || 'Đồ họa tích hợp' },
        { label: 'Dung lượng VRAM', key: 'vram_gb', format: (p: Product) => p.specs.vram_gb ? `${p.specs.vram_gb}GB GDDR6` : 'Share RAM' }
      ]
    },
    {
      category: 'Bộ Nhớ & Lưu Trữ',
      icon: HardDrive,
      rows: [
        { label: 'Dung lượng RAM', key: 'ram_gb', format: (p: Product) => p.specs.ram_gb ? `${p.specs.ram_gb}GB` : 'N/A' },
        { label: 'Chuẩn RAM', key: 'ram_type', format: (p: Product) => p.specs.ram_type || 'DDR5' },
        { label: 'Ổ cứng SSD', key: 'storage_gb', format: (p: Product) => p.specs.storage_gb ? `${p.specs.storage_gb >= 1024 ? '1TB' : `${p.specs.storage_gb}GB`} NVMe SSD` : 'SSD' }
      ]
    },
    {
      category: 'Hậu Mãi & Bảo Hành',
      icon: ShieldCheck,
      rows: [
        { label: 'Thời gian bảo hành', key: 'warranty', format: (p: Product) => `${p.specs.warranty_months || 24} tháng chính hãng` },
        { label: 'Chính sách đổi trả', key: 'return_policy', format: () => '1 đổi 1 trong 30 ngày nếu lỗi NSX' },
        { label: 'Tình trạng tồn kho', key: 'stock', format: (p: Product) => p.stockStatus?.status === 'out_of_stock' ? 'Hết hàng' : `Còn hàng (${p.stockStatus?.availableQty || 15} máy sẵn tại showroom)` }
      ]
    }
  ];

  return (
    <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 sm:px-6 py-5 w-full flex-1 text-slate-800 dark:text-slate-100">
      {/* 1. Breadcrumb */}
      <nav className="mb-4 flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
        <button
          onClick={onBackToHome}
          className="hover:text-[#d70018] dark:hover:text-red-400 font-bold flex items-center space-x-1.5 transition cursor-pointer"
        >
          <Home className="w-3.5 h-3.5" />
          <span>Trang Chủ</span>
        </button>
        <span className="text-slate-400">/</span>
        <span className="text-[#d70018] dark:text-red-400 font-extrabold uppercase">
          So Sánh Chi Tiết Thông Số Sản Phẩm
        </span>
      </nav>

      {/* 2. Top Header Bar */}
      <div className="mb-6 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-slate-900 dark:bg-slate-800 text-white flex items-center justify-center font-bold">
              <Scale className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-black text-slate-900 dark:text-slate-100">
                So Sánh Cấu Hình & Hiệu Năng Sản Phẩm ({products.length})
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Đối chiếu trực quan từng thông số kỹ thuật, giá bán và ước tính FPS gaming thực tế
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {products.length > 1 && (
            <button
              onClick={() => setOnlyDifferences(!onlyDifferences)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer border ${
                onlyDifferences
                  ? 'bg-amber-500 text-slate-950 border-amber-600 shadow-sm'
                  : 'bg-gray-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-gray-200 dark:border-slate-700 hover:border-amber-400'
              }`}
            >
              <span>{onlyDifferences ? 'Đang lọc điểm khác nhau ✓' : 'Chỉ hiện điểm khác nhau'}</span>
            </button>
          )}

          {products.length > 0 && (
            <button
              onClick={onClearAll}
              className="px-3.5 py-2 bg-red-50 dark:bg-red-950/40 hover:bg-red-100 text-[#d70018] dark:text-red-400 border border-red-200 dark:border-red-900/60 rounded-xl text-xs font-bold transition flex items-center space-x-1 cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Xóa Hết ({products.length})</span>
            </button>
          )}

          <button
            onClick={onBackToHome}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-slate-700 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer shadow-xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Thêm Sản Phẩm Khác</span>
          </button>
        </div>
      </div>

      {/* 3. Empty State or Comparison Table */}
      {products.length === 0 ? (
        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-16 text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
            <Scale className="w-8 h-8" />
          </div>
          <h2 className="text-lg font-black text-slate-900 dark:text-slate-100">
            Danh Sách So Sánh Đang Trống
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
            Quý khách hãy nhấn vào biểu tượng <strong>So sánh [ ]</strong> ở góc mỗi sản phẩm ngoài trang chủ để đưa sản phẩm vào bảng đối chiếu này (tối đa 4 sản phẩm cùng lúc).
          </p>
          <button
            onClick={onBackToHome}
            className="mt-2 px-6 py-2.5 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
          >
            Quay Lại Chọn Sản Phẩm
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-xs">
          {/* Top Sticky Row with Product Previews */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-gray-200 dark:border-slate-800 bg-gray-50 dark:bg-slate-900/60">
                  <th className="p-4 w-52 min-w-[200px] text-slate-500 dark:text-slate-400 uppercase font-black text-[11px] align-top">
                    Thông số so sánh
                  </th>
                  {products.map(p => (
                    <th key={p.id} className="p-4 min-w-[240px] max-w-[300px] align-top text-center border-l border-gray-200 dark:border-slate-800 relative">
                      {/* Remove Button */}
                      <button
                        onClick={() => onRemoveProduct(p.id)}
                        className="absolute top-2 right-2 p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition"
                        title="Bỏ so sánh máy này"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>

                      {/* Product Image */}
                      <div
                        onClick={() => onSelectProduct(p.slug || p.id)}
                        className="cursor-pointer group relative aspect-square max-h-40 p-2 bg-white dark:bg-slate-800 rounded-2xl flex items-center justify-center overflow-hidden mx-auto mb-3 border border-gray-150 dark:border-slate-700 shadow-2xs"
                      >
                        <img
                          src={p.imageUrl}
                          alt={p.name}
                          className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform"
                        />
                      </div>

                      {/* Product Brand & Name */}
                      <span className="text-[10px] font-extrabold text-[#d70018] uppercase tracking-wider block mb-1">
                        {p.brandName}
                      </span>
                      <h3
                        onClick={() => onSelectProduct(p.slug || p.id)}
                        className="font-bold text-xs sm:text-sm text-slate-900 dark:text-slate-100 line-clamp-2 hover:text-[#d70018] cursor-pointer min-h-[38px] leading-snug"
                        title={p.name}
                      >
                        {p.name}
                      </h3>

                      {/* Price */}
                      <div className="mt-2 text-base font-black text-[#d70018] dark:text-red-400 font-mono">
                        {new Intl.NumberFormat('vi-VN').format(p.price)}₫
                      </div>

                      {/* Buttons */}
                      <div className="mt-3 flex items-center space-x-2">
                        <button
                          onClick={() => {
                            addToCart(p);
                            onToast('Đã thêm vào giỏ hàng', p.name, 'success');
                          }}
                          className="flex-1 py-2 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl font-extrabold text-[11px] flex items-center justify-center space-x-1 transition shadow-xs cursor-pointer active:scale-95"
                        >
                          <ShoppingCart className="w-3.5 h-3.5" />
                          <span>Chọn Mua</span>
                        </button>
                        <button
                          onClick={() => onSelectProduct(p.slug || p.id)}
                          className="p-2 bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl transition cursor-pointer"
                          title="Xem chi tiết máy"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              {/* Specs Rows divided by Category */}
              <tbody>
                {specsRows.map(section => {
                  const SectionIcon = section.icon;

                  // Filter rows if "onlyDifferences" is active
                  const displayedRows = section.rows.filter(r => {
                    if (!onlyDifferences) return true;
                    const vals = products.map(p => r.format(p));
                    return new Set(vals).size > 1;
                  });

                  if (displayedRows.length === 0) return null;

                  return (
                    <React.Fragment key={section.category}>
                      {/* Section Category Header Banner */}
                      <tr className="bg-slate-100 dark:bg-slate-800/80 border-t-2 border-b border-gray-200 dark:border-slate-700 font-extrabold text-slate-900 dark:text-slate-100">
                        <td colSpan={products.length + 1} className="py-2.5 px-4 text-xs">
                          <div className="flex items-center space-x-2">
                            <SectionIcon className="w-4 h-4 text-[#d70018]" />
                            <span className="uppercase tracking-wider">{section.category}</span>
                          </div>
                        </td>
                      </tr>

                      {/* Attribute rows */}
                      {displayedRows.map((r, rowIdx) => {
                        const vals = products.map(p => r.format(p));
                        const isDiff = new Set(vals).size > 1;

                        return (
                          <tr
                            key={r.key}
                            className={`border-b border-gray-100 dark:border-slate-800/60 transition ${
                              isDiff
                                ? 'bg-amber-50/50 dark:bg-amber-950/20'
                                : rowIdx % 2 === 0
                                ? 'bg-white dark:bg-[#151c2c]'
                                : 'bg-gray-50/40 dark:bg-slate-900/30'
                            }`}
                          >
                            <td className="p-3.5 font-bold text-slate-600 dark:text-slate-300 text-xs">
                              <div className="flex items-center space-x-1.5">
                                <span>{r.label}</span>
                                {isDiff && (
                                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-amber-400 text-slate-950 uppercase">
                                    Khác biệt
                                  </span>
                                )}
                              </div>
                            </td>

                            {products.map(p => {
                              const val = r.format(p);
                              return (
                                <td
                                  key={p.id}
                                  className="p-3.5 text-center text-xs border-l border-gray-100 dark:border-slate-800/60 font-medium text-slate-800 dark:text-slate-200"
                                >
                                  {val}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
