import React, { useState, useMemo } from 'react';
import {
  CreditCard,
  X,
  CheckCircle2,
  HelpCircle,
  Percent,
  Calendar,
  Building2,
  Wallet,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { sound } from '../../utils/sound';

interface InstallmentCalculatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  productName: string;
  price: number;
  onSelectPlan?: (planDetails: { provider: string; termMonths: number; monthlyPayment: number; downPayment: number }) => void;
}

interface ProviderConfig {
  id: string;
  name: string;
  type: 'card' | 'bnpl';
  logoText: string;
  logoBg: string;
  terms: number[]; // e.g. [3, 6, 9, 12]
  conversionRates: Record<number, number>; // e.g. 3: 0, 6: 1.5, 9: 2.0, 12: 2.5 (%)
  minPrice: number;
}

const PROVIDERS: ProviderConfig[] = [
  {
    id: 'fundiin',
    name: 'Fundiin - Trả sau 0% lãi suất',
    type: 'bnpl',
    logoText: 'FUNDIIN',
    logoBg: 'bg-blue-600 text-white',
    terms: [3, 6],
    conversionRates: { 3: 0.0, 6: 1.2 },
    minPrice: 500000
  },
  {
    id: 'kredivo',
    name: 'Kredivo - Mua trước trả sau',
    type: 'bnpl',
    logoText: 'KREDIVO',
    logoBg: 'bg-amber-500 text-white',
    terms: [3, 6, 12],
    conversionRates: { 3: 0.0, 6: 1.5, 12: 2.5 },
    minPrice: 1000000
  },
  {
    id: 'techcombank',
    name: 'Techcombank (Visa / Mastercard)',
    type: 'card',
    logoText: 'TCB',
    logoBg: 'bg-red-600 text-white',
    terms: [3, 6, 9, 12],
    conversionRates: { 3: 0.0, 6: 1.5, 9: 2.2, 12: 2.8 },
    minPrice: 2000000
  },
  {
    id: 'vpbank',
    name: 'VPBank (Visa / Mastercard)',
    type: 'card',
    logoText: 'VPB',
    logoBg: 'bg-emerald-600 text-white',
    terms: [3, 6, 9, 12],
    conversionRates: { 3: 0.0, 6: 1.6, 9: 2.3, 12: 2.9 },
    minPrice: 2000000
  },
  {
    id: 'sacombank',
    name: 'Sacombank (Visa / JCB / Master)',
    type: 'card',
    logoText: 'STB',
    logoBg: 'bg-blue-700 text-white',
    terms: [3, 6, 9, 12],
    conversionRates: { 3: 0.0, 6: 1.8, 9: 2.5, 12: 3.0 },
    minPrice: 2000000
  },
  {
    id: 'mbbank',
    name: 'MB Bank (Visa / Mastercard)',
    type: 'card',
    logoText: 'MB',
    logoBg: 'bg-indigo-600 text-white',
    terms: [3, 6, 9, 12],
    conversionRates: { 3: 0.0, 6: 1.5, 9: 2.1, 12: 2.7 },
    minPrice: 2000000
  }
];

export const InstallmentCalculatorModal: React.FC<InstallmentCalculatorModalProps> = ({
  isOpen,
  onClose,
  productName,
  price,
  onSelectPlan
}) => {
  const [providerType, setProviderType] = useState<'all' | 'card' | 'bnpl'>('all');
  const [selectedProviderId, setSelectedProviderId] = useState<string>('fundiin');
  const [selectedTerm, setSelectedTerm] = useState<number>(6);
  const [downPaymentPercent, setDownPaymentPercent] = useState<number>(0); // 0%, 20%, 30%, 50%

  // Current Provider
  const currentProvider = useMemo(() => {
    return PROVIDERS.find(p => p.id === selectedProviderId) || PROVIDERS[0];
  }, [selectedProviderId]);

  // Filtered Providers by tab
  const filteredProviders = useMemo(() => {
    if (providerType === 'all') return PROVIDERS;
    return PROVIDERS.filter(p => p.type === providerType);
  }, [providerType]);

  // Ensure selected term is valid for current provider
  React.useEffect(() => {
    if (!currentProvider.terms.includes(selectedTerm)) {
      setSelectedTerm(currentProvider.terms[0] || 6);
    }
  }, [currentProvider, selectedTerm]);

  // Math Calculations
  const downPaymentAmount = useMemo(() => {
    return Math.round((price * downPaymentPercent) / 100);
  }, [price, downPaymentPercent]);

  const financedAmount = useMemo(() => {
    return Math.max(0, price - downPaymentAmount);
  }, [price, downPaymentAmount]);

  const conversionFeeRate = useMemo(() => {
    return currentProvider.conversionRates[selectedTerm] || 0;
  }, [currentProvider, selectedTerm]);

  const conversionFeeAmount = useMemo(() => {
    return Math.round((financedAmount * conversionFeeRate) / 100);
  }, [financedAmount, conversionFeeRate]);

  const totalFinancedWithFee = useMemo(() => {
    return financedAmount + conversionFeeAmount;
  }, [financedAmount, conversionFeeAmount]);

  const monthlyPayment = useMemo(() => {
    if (selectedTerm <= 0) return 0;
    return Math.round(totalFinancedWithFee / selectedTerm);
  }, [totalFinancedWithFee, selectedTerm]);

  const totalFinalPayment = useMemo(() => {
    return downPaymentAmount + totalFinancedWithFee;
  }, [downPaymentAmount, totalFinancedWithFee]);

  const formatVND = (num: number) => {
    return new Intl.NumberFormat('vi-VN').format(num) + '₫';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#151c2c] text-slate-800 dark:text-slate-100 rounded-3xl max-w-2xl w-full p-5 sm:p-7 shadow-2xl border border-slate-200 dark:border-slate-800 relative space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-gray-150 dark:border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-2xl bg-red-50 dark:bg-red-950/50 text-[#d70018] dark:text-red-400 flex items-center justify-center border border-red-200 dark:border-red-900/60 shadow-xs">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base sm:text-lg text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                <span>Dự Toán Trả Góp 0% Lãi Suất</span>
                <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                  Duyệt online 15P
                </span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                {productName} • Giá niêm yết: <strong className="text-[#d70018] dark:text-red-400 font-mono">{formatVND(price)}</strong>
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              onClose();
              sound.playClick();
            }}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Category Tabs: Card vs BNPL */}
        <div className="flex space-x-1.5 bg-gray-100 dark:bg-slate-800/80 p-1 rounded-xl border border-gray-200 dark:border-slate-700 text-xs font-semibold">
          <button
            onClick={() => setProviderType('all')}
            className={`flex-1 py-1.5 rounded-lg transition cursor-pointer ${
              providerType === 'all'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            Tất cả đối tác ({PROVIDERS.length})
          </button>
          <button
            onClick={() => setProviderType('bnpl')}
            className={`flex-1 py-1.5 rounded-lg transition cursor-pointer flex items-center justify-center space-x-1 ${
              providerType === 'bnpl'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            <Wallet className="w-3.5 h-3.5 text-blue-500" />
            <span>Ví trả sau (Fundiin / Kredivo)</span>
          </button>
          <button
            onClick={() => setProviderType('card')}
            className={`flex-1 py-1.5 rounded-lg transition cursor-pointer flex items-center justify-center space-x-1 ${
              providerType === 'card'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            <Building2 className="w-3.5 h-3.5 text-red-500" />
            <span>Thẻ tín dụng ngân hàng</span>
          </button>
        </div>

        {/* Provider Selector Grid */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
            1. Chọn cổng thanh toán hoặc ngân hàng hỗ trợ:
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {filteredProviders.map(p => {
              const isSelected = p.id === selectedProviderId;
              return (
                <button
                  key={p.id}
                  onClick={() => {
                    setSelectedProviderId(p.id);
                    sound.playClick();
                  }}
                  className={`p-2.5 rounded-xl border text-left transition flex items-center space-x-2.5 cursor-pointer ${
                    isSelected
                      ? 'border-[#d70018] dark:border-red-500 bg-red-50/50 dark:bg-red-950/30 ring-2 ring-red-100 dark:ring-red-950/60 shadow-xs'
                      : 'border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 hover:border-gray-300 dark:hover:border-slate-700'
                  }`}
                >
                  <span className={`w-8 h-8 rounded-lg text-[10px] font-black flex items-center justify-center flex-shrink-0 ${p.logoBg}`}>
                    {p.logoText}
                  </span>
                  <div className="min-w-0 flex-1">
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100 truncate block">
                      {p.name.split(' - ')[0]}
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate">
                      {p.type === 'bnpl' ? 'Duyệt bằng CCCD' : 'Hạn mức thẻ'}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Terms & Downpayment Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Term Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5 flex items-center justify-between">
              <span>2. Chọn kỳ hạn trả góp:</span>
              <span className="text-[11px] text-[#d70018] dark:text-red-400 font-semibold">{selectedTerm} tháng</span>
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {[3, 6, 9, 12].map(t => {
                const isAvailable = currentProvider.terms.includes(t);
                const isSelected = selectedTerm === t;
                return (
                  <button
                    key={t}
                    disabled={!isAvailable}
                    onClick={() => {
                      setSelectedTerm(t);
                      sound.playClick();
                    }}
                    className={`py-2 text-xs font-bold rounded-xl border transition cursor-pointer ${
                      isSelected
                        ? 'bg-[#d70018] text-white border-[#d70018] shadow-xs'
                        : isAvailable
                        ? 'bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-gray-300'
                        : 'bg-gray-50 dark:bg-slate-900/40 border-gray-150 dark:border-slate-800 text-slate-300 dark:text-slate-600 cursor-not-allowed'
                    }`}
                  >
                    {t}T
                  </button>
                );
              })}
            </div>
          </div>

          {/* Downpayment Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5 flex items-center justify-between">
              <span>3. Số tiền trả trước:</span>
              <span className="text-[11px] text-[#d70018] dark:text-red-400 font-semibold">{formatVND(downPaymentAmount)} ({downPaymentPercent}%)</span>
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {[0, 20, 30, 50].map(pct => {
                const isSelected = downPaymentPercent === pct;
                return (
                  <button
                    key={pct}
                    onClick={() => {
                      setDownPaymentPercent(pct);
                      sound.playClick();
                    }}
                    className={`py-2 text-xs font-bold rounded-xl border transition cursor-pointer ${
                      isSelected
                        ? 'bg-[#d70018] text-white border-[#d70018] shadow-xs'
                        : 'bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-gray-300'
                    }`}
                  >
                    {pct}%
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Calculation Result Summary Box */}
        <div className="bg-gradient-to-br from-slate-50 to-red-50/30 dark:from-slate-900/90 dark:to-red-950/20 p-4 sm:p-5 rounded-2xl border border-red-200/60 dark:border-red-900/40 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-gray-200/80 dark:border-slate-800 gap-2">
            <div>
              <span className="text-xs text-slate-500 dark:text-slate-400 block font-medium">Số tiền cần thanh toán mỗi tháng:</span>
              <div className="text-2xl sm:text-3xl font-black text-[#d70018] dark:text-red-400 font-mono tracking-tight">
                {formatVND(monthlyPayment)}
                <span className="text-xs font-bold text-slate-500 dark:text-slate-400 font-sans ml-1">/tháng</span>
              </div>
            </div>
            <div className="text-right sm:text-right">
              <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                <Percent className="w-3.5 h-3.5" />
                <span>Lãi suất 0% hàng tháng</span>
              </span>
            </div>
          </div>

          {/* Breakdown Table */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs pt-1">
            <div className="bg-white/80 dark:bg-slate-800/60 p-2.5 rounded-xl border border-gray-150 dark:border-slate-700/60">
              <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Tiền trả trước:</span>
              <strong className="font-mono text-slate-800 dark:text-slate-200">{formatVND(downPaymentAmount)}</strong>
            </div>

            <div className="bg-white/80 dark:bg-slate-800/60 p-2.5 rounded-xl border border-gray-150 dark:border-slate-700/60">
              <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Số tiền vay trả góp:</span>
              <strong className="font-mono text-slate-800 dark:text-slate-200">{formatVND(financedAmount)}</strong>
            </div>

            <div className="bg-white/80 dark:bg-slate-800/60 p-2.5 rounded-xl border border-gray-150 dark:border-slate-700/60">
              <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Phí chuyển đổi hồ sơ:</span>
              <strong className="font-mono text-emerald-600 dark:text-emerald-400">
                {conversionFeeAmount === 0 ? '0₫ (Miễn phí)' : formatVND(conversionFeeAmount)}
              </strong>
            </div>

            <div className="bg-white/80 dark:bg-slate-800/60 p-2.5 rounded-xl border border-gray-150 dark:border-slate-700/60">
              <span className="text-slate-400 dark:text-slate-500 block text-[10px]">Tổng thanh toán:</span>
              <strong className="font-mono text-[#d70018] dark:text-red-400">{formatVND(totalFinalPayment)}</strong>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 text-[11px] text-slate-500 dark:text-slate-400 pt-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
            <span>Hồ sơ xét duyệt trực tuyến, chỉ cần CCCD gắn chip (đối với Fundiin/Kredivo) hoặc Thẻ tín dụng còn hạn mức. Không giữ giấy tờ tùy thân.</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2 pt-1">
          <button
            onClick={onClose}
            className="flex-1 py-3 border border-gray-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-gray-50 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            Đóng
          </button>
          <button
            onClick={() => {
              if (onSelectPlan) {
                onSelectPlan({
                  provider: currentProvider.name,
                  termMonths: selectedTerm,
                  monthlyPayment,
                  downPayment: downPaymentAmount
                });
              }
              onClose();
              sound.playVoucherSuccess();
            }}
            className="flex-2 py-3 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl text-xs font-bold transition flex items-center justify-center space-x-1.5 shadow-sm cursor-pointer"
          >
            <span>Chọn Gói Trả Góp Này ({formatVND(monthlyPayment)}/tháng)</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
