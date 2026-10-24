import React from 'react';
import { Filter, RotateCcw, Check, Zap } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface ProductFiltersProps {
  facets: any;
  selectedBrand?: string;
  selectedPriceRange?: string;
  selectedDemand?: string;
  selectedPanel?: string;
  inStockOnly: boolean;
  hasInstallment0: boolean;
  onFilterChange: (filters: {
    brand?: string;
    priceRange?: string;
    demand?: string;
    panel?: string;
    inStockOnly?: boolean;
    hasInstallment0?: boolean;
  }) => void;
  onReset: () => void;
}

export const ProductFilters: React.FC<ProductFiltersProps> = ({
  facets = {},
  selectedBrand,
  selectedPriceRange,
  selectedDemand,
  selectedPanel,
  inStockOnly,
  hasInstallment0,
  onFilterChange,
  onReset
}) => {
  const { t, lang } = useLanguage();
  const brands = facets.brands || {};
  const panels = facets.panels || {};
  const demands = facets.demands || {};

  const priceRanges = [
    { id: 'under15m', label: lang === 'vi' ? 'Dưới 15 triệu' : 'Under 15M', count: facets.priceRanges?.under15m || 0 },
    { id: 'from15to20m', label: lang === 'vi' ? '15 - 20 triệu' : '15 - 20M', count: facets.priceRanges?.from15to20m || 0 },
    { id: 'from20to30m', label: lang === 'vi' ? '20 - 30 triệu' : '20 - 30M', count: facets.priceRanges?.from20to30m || 0 },
    { id: 'above30m', label: lang === 'vi' ? 'Trên 30 triệu' : 'Above 30M', count: facets.priceRanges?.above30m || 0 }
  ];

  const demandOptions = [
    { id: 'study_office', label: lang === 'vi' ? 'Học tập - Văn phòng' : 'Office & Study' },
    { id: 'thin_light', label: lang === 'vi' ? 'Mỏng nhẹ di chuyển' : 'Slim & Lightweight' },
    { id: 'gaming', label: lang === 'vi' ? 'Gaming & Đồ họa nặng' : 'Gaming & Heavy Graphics' },
    { id: 'design_graphics', label: lang === 'vi' ? 'Thiết kế chuẩn màu' : 'Color-Accurate Design' }
  ];

  return (
    <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5 space-y-5 text-xs text-slate-800 dark:text-slate-200 shadow-xs transition-colors">
      {/* Filter Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-150 dark:border-slate-800">
        <div className="flex items-center space-x-2 font-bold text-sm text-slate-900 dark:text-slate-100">
          <Filter className="w-4 h-4 text-[#d70018] dark:text-red-400" />
          <span>{t('filtersTitle')}</span>
        </div>
        <button
          onClick={onReset}
          className="text-[#d70018] dark:text-red-400 hover:text-[#b91c1c] dark:hover:text-red-300 flex items-center space-x-1 font-semibold text-[11px] transition cursor-pointer"
        >
          <RotateCcw className="w-3 h-3" />
          <span>{t('clearFilters')}</span>
        </button>
      </div>

      {/* 1. Availability Toggles */}
      <div className="space-y-2 bg-gray-50/80 dark:bg-slate-800/60 p-3 rounded-xl border border-gray-150 dark:border-slate-700">
        <label className="flex items-center space-x-2.5 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={e => onFilterChange({ inStockOnly: e.target.checked })}
            className="w-4 h-4 text-[#d70018] rounded border-gray-300 dark:border-slate-600 focus:ring-[#d70018]"
          />
          <span className="font-semibold text-slate-800 dark:text-slate-200">{t('inStockOnly')}</span>
        </label>
        <label className="flex items-center space-x-2.5 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={hasInstallment0}
            onChange={e => onFilterChange({ hasInstallment0: e.target.checked })}
            className="w-4 h-4 text-[#d70018] rounded border-gray-300 dark:border-slate-600 focus:ring-[#d70018]"
          />
          <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center space-x-1">
            <span>{t('filterInstallment0')}</span>
            <Zap className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
          </span>
        </label>
      </div>

      {/* 2. Price Range */}
      <div>
        <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-2">{t('filterPrice')}</h4>
        <div className="space-y-1.5">
          {priceRanges.map(pr => {
            const isSelected = selectedPriceRange === pr.id;
            return (
              <button
                key={pr.id}
                onClick={() => onFilterChange({ priceRange: isSelected ? undefined : pr.id })}
                disabled={pr.count === 0}
                className={`w-full flex items-center justify-between p-2 rounded-xl border transition text-left cursor-pointer ${
                  isSelected
                    ? 'border-[#d70018] bg-red-50/60 dark:bg-red-950/40 text-[#d70018] dark:text-red-300 font-bold shadow-xs'
                    : pr.count === 0
                    ? 'border-gray-100 dark:border-slate-800 bg-gray-50 dark:bg-slate-900/40 text-slate-400 dark:text-slate-600 cursor-not-allowed'
                    : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
              >
                <span>{pr.label}</span>
                <span className={`text-[10px] ${isSelected ? 'text-[#d70018] dark:text-red-400 font-bold' : 'text-slate-400 dark:text-slate-500'}`}>
                  ({pr.count})
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Brands with Facet Counts */}
      {Object.keys(brands).length > 0 && (
        <div>
          <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-2">{t('filterBrand')}</h4>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(brands).map(([brandName, count]) => {
              const isSelected = selectedBrand?.toLowerCase() === brandName.toLowerCase();
              return (
                <button
                  key={brandName}
                  onClick={() => onFilterChange({ brand: isSelected ? undefined : brandName })}
                  className={`px-2.5 py-1.5 rounded-xl border text-xs transition flex items-center space-x-1 cursor-pointer ${
                    isSelected
                      ? 'border-[#d70018] bg-red-50/60 dark:bg-red-950/40 text-[#d70018] dark:text-red-300 font-bold shadow-xs'
                      : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700'
                  }`}
                >
                  <span>{brandName}</span>
                  <span className={`text-[10px] ${isSelected ? 'text-red-700 dark:text-red-400 font-bold' : 'text-slate-400 dark:text-slate-500'}`}>
                    ({count as number})
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 4. Demand / Use Cases */}
      <div>
        <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-2">{t('filterDemand')}</h4>
        <div className="space-y-1.5">
          {demandOptions.map(opt => {
            const isSelected = selectedDemand === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => onFilterChange({ demand: isSelected ? undefined : opt.id })}
                className={`w-full flex items-center justify-between p-2 rounded-xl border transition text-left cursor-pointer ${
                  isSelected
                    ? 'border-[#d70018] bg-red-50/60 dark:bg-red-950/40 text-[#d70018] dark:text-red-300 font-bold shadow-xs'
                    : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
              >
                <span>{opt.label}</span>
                {isSelected && <Check className="w-3.5 h-3.5 text-[#d70018] dark:text-red-400" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* 5. Panel Screen Technology */}
      {Object.keys(panels).length > 0 && (
        <div>
          <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-2">{t('filterScreen')}</h4>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(panels).map(([panelName, count]) => {
              const isSelected = selectedPanel?.toLowerCase() === panelName.toLowerCase();
              return (
                <button
                  key={panelName}
                  onClick={() => onFilterChange({ panel: isSelected ? undefined : panelName })}
                  className={`px-2.5 py-1.5 rounded-xl border text-xs transition flex items-center space-x-1 cursor-pointer ${
                    isSelected
                      ? 'border-[#d70018] bg-red-50/60 dark:bg-red-950/40 text-[#d70018] dark:text-red-300 font-bold shadow-xs'
                      : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700'
                  }`}
                >
                  <span>{panelName}</span>
                  <span className={`text-[10px] ${isSelected ? 'text-red-700 dark:text-red-400 font-bold' : 'text-slate-400 dark:text-slate-500'}`}>
                    ({count as number})
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
