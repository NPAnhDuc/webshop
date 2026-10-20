import React from 'react';
import { Layers, X, ArrowRight } from 'lucide-react';
import { Product } from '../../types';

interface ComparisonBarProps {
  products: Product[];
  onRemove: (productId: string) => void;
  onClear: () => void;
  onOpenModal: () => void;
}

export const ComparisonBar: React.FC<ComparisonBarProps> = ({
  products,
  onRemove,
  onClear,
  onOpenModal
}) => {
  if (products.length === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 bg-white/95 dark:bg-[#151c2c]/95 backdrop-blur-md text-slate-800 dark:text-slate-100 px-5 py-3 rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-800 flex items-center space-x-5 animate-in slide-in-from-bottom-5 duration-200 max-w-2xl w-[94%] sm:w-auto">
      <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 dark:text-slate-100">
        <Layers className="w-4 h-4 text-[#059669] dark:text-emerald-400" />
        <span>So sánh ({products.length}/3):</span>
      </div>

      {/* Thumbnails */}
      <div className="flex items-center space-x-2.5 overflow-x-auto">
        {products.map(p => (
          <div key={p.id} className="relative group bg-gray-50 dark:bg-slate-800 rounded-lg p-1 border border-gray-200 dark:border-slate-700 flex items-center space-x-2 pr-2">
            <img src={p.imageUrl} alt={p.name} className="w-8 h-8 object-contain rounded bg-white dark:bg-slate-900 p-0.5" />
            <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 max-w-[100px] truncate hidden sm:inline">
              {p.name.split(' ')[1] || p.name}
            </span>
            <button
              onClick={() => onRemove(p.id)}
              className="text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition cursor-pointer"
              title="Bỏ chọn"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>

      <div className="flex items-center space-x-2 border-l border-gray-200 dark:border-slate-700 pl-4">
        <button
          onClick={onOpenModal}
          disabled={products.length < 2}
          className="px-3.5 py-1.5 bg-[#059669] hover:bg-[#047857] dark:bg-emerald-600 dark:hover:bg-emerald-500 disabled:bg-gray-200 dark:disabled:bg-slate-800 disabled:text-slate-400 dark:disabled:text-slate-600 text-white font-bold rounded-lg text-xs flex items-center space-x-1 transition shadow-xs cursor-pointer"
        >
          <span>So sánh ngay</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onClear}
          className="text-[11px] text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition cursor-pointer"
        >
          Xóa
        </button>
      </div>
    </div>
  );
};
