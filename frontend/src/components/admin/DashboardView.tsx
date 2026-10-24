import React, { useState, useEffect, useMemo } from 'react';
import {
  TrendingUp,
  DollarSign,
  Package,
  ShoppingBag,
  AlertOctagon,
  Calendar,
  Layers,
  ArrowUpRight,
  Pin,
  Sparkles,
  SlidersHorizontal,
  CheckCircle2,
  X,
  CreditCard,
  Truck,
  RotateCcw,
  BarChart3,
  Percent,
  Check,
  Building,
  Globe,
  HelpCircle,
  Eye,
  Filter
} from 'lucide-react';
import { fetchAdminKPIs, fetchAdminCharts, fetchPinnedWidgets } from '../../services/api';
import { ChartSpec } from '../../types';
import { CuteRobotAvatar } from '../common/CuteRobotAvatar';
import { sound } from '../../utils/sound';

interface DashboardViewProps {
  onNavigateToChatbot: () => void;
}

// Configurable Dashboard Widget/Metric Key definitions
type MetricKey =
  | 'net_revenue'
  | 'gross_profit'
  | 'cm1_margin'
  | 'cm2_margin'
  | 'cm3_margin'
  | 'completed_orders'
  | 'aov'
  | 'inventory_value'
  | 'cod_return_rate'
  | 'repeat_customer_rate'
  | 'roas';

type SectionKey =
  | 'pnl_waterfall'
  | 'revenue_target_chart'
  | 'category_chart'
  | 'channel_breakdown'
  | 'payment_method_breakdown'
  | 'top_products'
  | 'pinned_widgets';

const DEFAULT_ENABLED_METRICS: MetricKey[] = [
  'net_revenue',
  'gross_profit',
  'cm1_margin',
  'cm2_margin',
  'completed_orders',
  'aov',
  'inventory_value',
  'cod_return_rate'
];

const DEFAULT_ENABLED_SECTIONS: SectionKey[] = [
  'pnl_waterfall',
  'revenue_target_chart',
  'category_chart',
  'channel_breakdown',
  'payment_method_breakdown',
  'top_products',
  'pinned_widgets'
];

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigateToChatbot }) => {
  const [kpis, setKpis] = useState<any>(null);
  const [charts, setCharts] = useState<ChartSpec[]>([]);
  const [pinnedWidgets, setPinnedWidgets] = useState<ChartSpec[]>([]);
  const [loading, setLoading] = useState(true);

  // Time Period Filter
  const [selectedPeriod, setSelectedPeriod] = useState<'today' | '7d' | '30d' | 'quarter' | 'year'>('30d');

  // Custom Metric / Widget Selector State
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [enabledMetrics, setEnabledMetrics] = useState<MetricKey[]>(() => {
    try {
      const saved = localStorage.getItem('admin_dashboard_metrics_v2');
      return saved ? JSON.parse(saved) : DEFAULT_ENABLED_METRICS;
    } catch {
      return DEFAULT_ENABLED_METRICS;
    }
  });

  const [enabledSections, setEnabledSections] = useState<SectionKey[]>(() => {
    try {
      const saved = localStorage.getItem('admin_dashboard_sections_v2');
      return saved ? JSON.parse(saved) : DEFAULT_ENABLED_SECTIONS;
    } catch {
      return DEFAULT_ENABLED_SECTIONS;
    }
  });

  // Save to localStorage when changed
  const handleSaveConfig = () => {
    try {
      localStorage.setItem('admin_dashboard_metrics_v2', JSON.stringify(enabledMetrics));
      localStorage.setItem('admin_dashboard_sections_v2', JSON.stringify(enabledSections));
      sound.playVoucherSuccess();
      setShowConfigModal(false);
    } catch (e) {
      console.error('Failed to save dashboard preferences', e);
    }
  };

  const handleResetConfig = () => {
    setEnabledMetrics(DEFAULT_ENABLED_METRICS);
    setEnabledSections(DEFAULT_ENABLED_SECTIONS);
    localStorage.removeItem('admin_dashboard_metrics_v2');
    localStorage.removeItem('admin_dashboard_sections_v2');
    sound.playClick();
  };

  const toggleMetric = (key: MetricKey) => {
    setEnabledMetrics(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  const toggleSection = (key: SectionKey) => {
    setEnabledSections(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  useEffect(() => {
    Promise.all([fetchAdminKPIs(), fetchAdminCharts(), fetchPinnedWidgets()])
      .then(([kpiData, chartData, pinnedData]) => {
        setKpis(kpiData);
        setCharts(chartData);
        setPinnedWidgets(pinnedData);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  // Multiplier by period to simulate realistic filter dynamics
  const periodMultiplier = useMemo(() => {
    switch (selectedPeriod) {
      case 'today':
        return 0.035;
      case '7d':
        return 0.25;
      case '30d':
        return 1.0;
      case 'quarter':
        return 2.85;
      case 'year':
        return 11.4;
      default:
        return 1.0;
    }
  }, [selectedPeriod]);

  // Derived metrics adjusted by period
  const displayKpis = useMemo(() => {
    if (!kpis) return null;
    const rev = Math.round(kpis.totalRevenue * periodMultiplier);
    const profit = Math.round(kpis.grossProfit * periodMultiplier);
    const orders = Math.max(1, Math.round(kpis.totalOrders * periodMultiplier));
    const aov = Math.round(rev / orders);
    const cm1 = Math.round((kpis.cm1 || (kpis.grossProfit * 0.92)) * periodMultiplier);
    const cm2 = Math.round((kpis.cm2 || (kpis.grossProfit * 0.65)) * periodMultiplier);
    const cm3 = Math.round((kpis.cm3 || (kpis.grossProfit * 0.52)) * periodMultiplier);
    const marketingSpend = Math.round((kpis.marketingSpend || (rev * 0.058)));

    return {
      ...kpis,
      totalRevenue: rev,
      grossProfit: profit,
      totalOrders: orders,
      aov,
      cm1,
      cm2,
      cm3,
      marketingSpend
    };
  }, [kpis, periodMultiplier]);

  const formatVND = (num: number) => {
    return new Intl.NumberFormat('vi-VN').format(num) + '₫';
  };

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 rounded-full border-3 border-slate-300 dark:border-slate-700 border-t-[#d70018] animate-spin" />
        <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          Đang tổng hợp báo cáo tài chính & chỉ số kinh doanh thời gian thực...
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-800 dark:text-slate-100 transition-colors">
      {/* 1. Header with Period Filter, Customizer Toggle & AI Bot Prompt */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 tracking-tight">
              Trung Tâm Báo Cáo Sức Khỏe Kinh Doanh
            </h2>
            <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 hidden sm:inline-block">
              LIVE REALTIME
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Báo cáo tài chính P&L, biên đóng góp CM1/CM2/CM3, hiệu quả kênh và kiểm soát thất thoát
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Period Selector */}
          <div className="flex items-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700/80 p-1 rounded-xl text-xs font-semibold shadow-2xs">
            <span className="px-2 text-slate-400 dark:text-slate-500 flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Kỳ:</span>
            </span>
            {(['today', '7d', '30d', 'quarter', 'year'] as const).map(p => (
              <button
                key={p}
                onClick={() => {
                  setSelectedPeriod(p);
                  sound.playClick();
                }}
                className={`px-2.5 py-1 rounded-lg transition cursor-pointer text-xs font-bold ${
                  selectedPeriod === p
                    ? 'bg-[#d70018] text-white shadow-2xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                {p === 'today' ? 'Hôm nay' : p === '7d' ? '7 ngày' : p === '30d' ? '30 ngày' : p === 'quarter' ? 'Quý 4' : 'Năm 2026'}
              </button>
            ))}
          </div>

          {/* Metric & Widget Customizer Button */}
          <button
            onClick={() => {
              setShowConfigModal(true);
              sound.playPop();
            }}
            className="px-3 py-2 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-2xs cursor-pointer"
            title="Tùy chọn hiển thị hoặc ẩn các thẻ chỉ số và biểu đồ theo nhu cầu"
          >
            <SlidersHorizontal className="w-4 h-4 text-slate-500" />
            <span>Tùy Chỉnh Số Liệu ({enabledMetrics.length + enabledSections.length})</span>
          </button>

          {/* AI Assistant Button */}
          <button
            onClick={onNavigateToChatbot}
            className="group px-3.5 py-2 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 hover:from-slate-800 hover:to-indigo-900 text-white rounded-xl text-xs font-bold flex items-center space-x-2.5 shadow-md hover:shadow-lg transition border border-indigo-500/30 active:scale-95 cursor-pointer"
          >
            <CuteRobotAvatar mode="admin" size="sm" isWaving={true} showSpeechBubble={false} className="w-5 h-5 flex-shrink-0 group-hover:scale-110 transition-transform" />
            <span>Hỏi Trợ Lý AI</span>
          </button>
        </div>
      </div>

      {/* 2. DYNAMIC KPI CARDS GRID (Filtered by User's Customizer Selection) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        {/* Metric 1: Net Revenue */}
        {enabledMetrics.includes('net_revenue') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Doanh Thu Thuần</span>
              <DollarSign className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 font-mono tracking-tight">
              {formatVND(displayKpis?.totalRevenue || 0)}
            </div>
            <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-bold flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> +14.2% so với kỳ trước
            </p>
          </div>
        )}

        {/* Metric 2: Gross Profit */}
        {enabledMetrics.includes('gross_profit') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Lợi Nhuận Gộp (Gross)</span>
              <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-emerald-700 dark:text-emerald-400 font-mono tracking-tight">
              {formatVND(displayKpis?.grossProfit || 0)}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Biên lãi gộp: <strong className="text-slate-800 dark:text-slate-200">{displayKpis?.grossMarginPercent}%</strong>
            </p>
          </div>
        )}

        {/* Metric 3: CM1 Contribution Margin */}
        {enabledMetrics.includes('cm1_margin') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Biên CM1 (Sau Phí Sàn)</span>
              <Percent className="w-4 h-4 text-teal-600 dark:text-teal-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-teal-700 dark:text-teal-300 font-mono tracking-tight">
              {formatVND(displayKpis?.cm1 || 0)}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Tỷ lệ CM1: <strong className="text-teal-600 dark:text-teal-400">{displayKpis?.cm1Percent || '14.2'}%</strong> (Trừ sàn + hộp)
            </p>
          </div>
        )}

        {/* Metric 4: CM2 Marketing Margin */}
        {enabledMetrics.includes('cm2_margin') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Biên CM2 (Sau Quảng Cáo)</span>
              <BarChart3 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-purple-700 dark:text-purple-300 font-mono tracking-tight">
              {formatVND(displayKpis?.cm2 || 0)}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Tỷ lệ CM2: <strong className="text-purple-600 dark:text-purple-400">{displayKpis?.cm2Percent || '8.8'}%</strong> (Lãi ròng tiếp thị)
            </p>
          </div>
        )}

        {/* Metric 5: Completed Orders & Cancel Rate */}
        {enabledMetrics.includes('completed_orders') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Số Đơn Hoàn Thành</span>
              <ShoppingBag className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 font-mono tracking-tight">
              {displayKpis?.totalOrders || 0} đơn
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Tỷ lệ hủy trước giao: <strong className="text-slate-800 dark:text-slate-200">{displayKpis?.cancelRate}</strong>
            </p>
          </div>
        )}

        {/* Metric 6: AOV */}
        {enabledMetrics.includes('aov') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Giá Trị Đơn TB (AOV)</span>
              <Layers className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 font-mono tracking-tight">
              {formatVND(displayKpis?.aov || 0)}
            </div>
            <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-bold">
              +5.4% nhờ combo PC Builder
            </p>
          </div>
        )}

        {/* Metric 7: Inventory Value & DIO */}
        {enabledMetrics.includes('inventory_value') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Vốn Tồn Kho & Vòng Quay</span>
              <Package className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 font-mono tracking-tight">
              {formatVND(displayKpis?.inventoryValue || 0)}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Tuổi kho: <strong className="text-amber-600 dark:text-amber-400">{displayKpis?.avgInventoryDays} ngày</strong> (An toàn: ≤60)
            </p>
          </div>
        )}

        {/* Metric 8: COD Return Rate */}
        {enabledMetrics.includes('cod_return_rate') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Tỷ Lệ Hoàn COD (Boom Hàng)</span>
              <RotateCcw className="w-4 h-4 text-red-500 dark:text-red-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-red-600 dark:text-red-400 font-mono tracking-tight">
              {displayKpis?.codReturnRate || '4.2%'}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Thiệt hại 2 chiều ship: <strong className="text-red-500">~{formatVND(Math.round(displayKpis?.totalRevenue * 0.012))}</strong>
            </p>
          </div>
        )}

        {/* Metric 9: Repeat Customer Rate */}
        {enabledMetrics.includes('repeat_customer_rate') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Tỷ Lệ Mua Lặp Lại (Retention)</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 font-mono tracking-tight">
              {displayKpis?.repeatCustomerRate || '28.6%'}
            </div>
            <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-bold">
              Cohort 90 ngày duy trì tốt
            </p>
          </div>
        )}

        {/* Metric 10: ROAS */}
        {enabledMetrics.includes('roas') && (
          <div className="bg-white dark:bg-[#151c2c] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
              <span>Hiệu Suất Ads (ROAS)</span>
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-slate-100 font-mono tracking-tight">
              {displayKpis?.roas || '6.8x'}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Chi phí tiếp thị: {formatVND(displayKpis?.marketingSpend || 0)}
            </p>
          </div>
        )}
      </div>

      {/* 3. FINANCIAL WATERFALL P&L BREAKDOWN (GMV -> CM1 -> CM2 -> CM3) */}
      {enabledSections.includes('pnl_waterfall') && (
        <div className="bg-white dark:bg-[#151c2c] p-5 sm:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-150 dark:border-slate-800 gap-2">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-[#d70018]" />
                <span>Báo Cáo Phân Tầng Dòng Tiền & Biên Lợi Nhuận (Waterfall P&L)</span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Mô hình bóc tách chi phí thực tế theo chuẩn CCO (Kỳ {selectedPeriod.toUpperCase()})
              </p>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 self-start sm:self-auto font-mono">
              Doanh thu đối soát: {formatVND(displayKpis?.totalRevenue || 0)}
            </span>
          </div>

          {/* Waterfall Steps */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            {/* Step 1: Gross Revenue */}
            <div className="bg-slate-50 dark:bg-slate-900/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 block font-bold">1. DOANH THU THUẦN</span>
              <div className="text-lg font-black text-slate-900 dark:text-slate-100 font-mono">
                {formatVND(displayKpis?.totalRevenue || 0)}
              </div>
              <div className="text-[10px] text-slate-500 space-y-0.5 border-t border-slate-200 dark:border-slate-700 pt-1.5">
                <p>• Giá vốn COGS: -{formatVND((displayKpis?.totalRevenue || 0) - (displayKpis?.grossProfit || 0))}</p>
                <p>• Tỷ lệ giá vốn: 82.5%</p>
              </div>
            </div>

            {/* Step 2: CM1 */}
            <div className="bg-teal-50/70 dark:bg-teal-950/30 p-3.5 rounded-xl border border-teal-200 dark:border-teal-900/60 space-y-2">
              <span className="text-[11px] text-teal-800 dark:text-teal-300 block font-bold">2. BIÊN ĐÓNG GÓP CM1</span>
              <div className="text-lg font-black text-teal-700 dark:text-teal-300 font-mono">
                {formatVND(displayKpis?.cm1 || 0)}
              </div>
              <div className="text-[10px] text-teal-700/80 dark:text-teal-400 space-y-0.5 border-t border-teal-200 dark:border-teal-800/80 pt-1.5">
                <p>• Đã trừ phí sàn + thanh toán: 3.8%</p>
                <p>• Đã trừ bao bì carton: ~22k/đơn</p>
              </div>
            </div>

            {/* Step 3: CM2 */}
            <div className="bg-purple-50/70 dark:bg-purple-950/30 p-3.5 rounded-xl border border-purple-200 dark:border-purple-900/60 space-y-2">
              <span className="text-[11px] text-purple-800 dark:text-purple-300 block font-bold">3. BIÊN ĐÓNG GÓP CM2</span>
              <div className="text-lg font-black text-purple-700 dark:text-purple-300 font-mono">
                {formatVND(displayKpis?.cm2 || 0)}
              </div>
              <div className="text-[10px] text-purple-700/80 dark:text-purple-400 space-y-0.5 border-t border-purple-200 dark:border-purple-800/80 pt-1.5">
                <p>• Đã trừ tiền Ads: -{formatVND(displayKpis?.marketingSpend || 0)}</p>
                <p>• ROAS chiến dịch: 6.8x</p>
              </div>
            </div>

            {/* Step 4: CM3 */}
            <div className="bg-emerald-50/70 dark:bg-emerald-950/30 p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-900/60 space-y-2">
              <span className="text-[11px] text-emerald-800 dark:text-emerald-300 block font-bold">4. LÃI VẬN HÀNH CM3</span>
              <div className="text-lg font-black text-emerald-700 dark:text-emerald-300 font-mono">
                {formatVND(displayKpis?.cm3 || 0)}
              </div>
              <div className="text-[10px] text-emerald-700/80 dark:text-emerald-400 space-y-0.5 border-t border-emerald-200 dark:border-emerald-800/80 pt-1.5">
                <p>• Dòng tiền thực nhận về két</p>
                <p>• Biên lãi vận hành ròng: 6.8%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. Core Analytical Charts: Revenue vs Plan & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Revenue vs Plan */}
        {enabledSections.includes('revenue_target_chart') && (
          <div className="bg-white dark:bg-[#151c2c] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Doanh thu thực tế so với Kế hoạch (8 tuần gần nhất)
              </h3>
              <span className="text-[11px] text-slate-400">Đơn vị: Tỷ VND</span>
            </div>

            <div className="h-60 flex items-end justify-between gap-3 pt-6 pb-2 px-2 border-b border-slate-150 dark:border-slate-800">
              {charts[0]?.data?.map((d: any, idx: number) => {
                const maxVal = 3.5;
                const actualH = (d.actual / maxVal) * 100;
                const targetH = (d.target / maxVal) * 100;

                return (
                  <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group relative">
                    <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[10px] px-2 py-1 rounded shadow pointer-events-none whitespace-nowrap z-10 font-bold">
                      {d.period}: Thực tế {d.actual} tỷ / Chỉ tiêu {d.target} tỷ
                    </div>

                    <div className="w-full flex items-end justify-center space-x-1 h-full">
                      <div className="w-2.5 bg-slate-200 dark:bg-slate-700 rounded-t" style={{ height: `${targetH}%` }} title={`Chỉ tiêu: ${d.target} tỷ`} />
                      <div className="w-3.5 bg-blue-600 dark:bg-blue-500 rounded-t transition-all group-hover:bg-blue-700" style={{ height: `${actualH}%` }} title={`Thực tế: ${d.actual} tỷ`} />
                    </div>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 mt-2 font-medium">{d.period}</span>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-center space-x-6 text-xs text-slate-600 dark:text-slate-400 pt-1">
              <span className="flex items-center space-x-1.5">
                <span className="w-3 h-3 bg-blue-600 rounded-xs" />
                <span>Doanh thu thực tế</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-3 h-3 bg-slate-300 dark:bg-slate-700 rounded-xs" />
                <span>Chỉ tiêu kế hoạch</span>
              </span>
            </div>
          </div>
        )}

        {/* Chart 2: Category Breakdown */}
        {enabledSections.includes('category_chart') && (
          <div className="bg-white dark:bg-[#151c2c] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Cơ cấu doanh thu theo nhóm hàng
              </h3>
              <span className="text-[11px] text-slate-400">Tỉ trọng (%)</span>
            </div>

            <div className="space-y-4 pt-2">
              {charts[1]?.data?.map((cat: any, idx: number) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                    <span>{cat.category}</span>
                    <span className="text-slate-900 dark:text-slate-100 font-bold">{cat.share}%</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-[#d70018] h-full rounded-full transition-all duration-500" style={{ width: `${cat.share}%` }} />
                  </div>
                </div>
              ))}
            </div>

            <p className="text-[11px] text-slate-500 dark:text-slate-400 pt-3 border-t border-slate-100 dark:border-slate-800">
              * Nhóm Laptop văn phòng và Gaming chiếm tới 67% tổng doanh thu của toàn cửa hàng.
            </p>
          </div>
        )}
      </div>

      {/* 5. Deep Multi-Channel & Payment Breakdown Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Channel Breakdown */}
        {enabledSections.includes('channel_breakdown') && (
          <div className="bg-white dark:bg-[#151c2c] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-150 dark:border-slate-800">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Hiệu Quả & Rủi Ro Từng Kênh Bán Hàng</h3>
              </div>
              <span className="text-[10px] text-slate-400">4 Kênh chính</span>
            </div>

            <div className="space-y-3">
              {(displayKpis?.channelBreakdown || [
                { channel: 'Website Trực Tiếp (TechStore)', share: 46, returnRate: '1.8%', revenue: 1400000000 },
                { channel: 'Sàn Shopee Mall', share: 29, returnRate: '4.5%', revenue: 890000000 },
                { channel: 'TikTok Shop Livestream', share: 15, returnRate: '11.8%', revenue: 460000000 },
                { channel: 'Tại Showroom Cửa Hàng', share: 10, returnRate: '0.1%', revenue: 310000000 }
              ]).map((ch: any, idx: number) => (
                <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5 text-xs">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-slate-800 dark:text-slate-200">{ch.channel}</span>
                    <span className="text-slate-900 dark:text-slate-100 font-mono">{ch.share}% Doanh số</span>
                  </div>
                  <div className="flex justify-between items-center text-[11px] text-slate-500 dark:text-slate-400">
                    <span>Doanh thu: {formatVND(ch.revenue || 0)}</span>
                    <span className={`font-bold ${parseFloat(ch.returnRate) > 8 ? 'text-red-600 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                      Tỷ lệ hoàn: {ch.returnRate} {parseFloat(ch.returnRate) > 8 ? '⚠️ Cao' : '✓ An toàn'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Payment Methods & Flow */}
        {enabledSections.includes('payment_method_breakdown') && (
          <div className="bg-white dark:bg-[#151c2c] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-150 dark:border-slate-800">
              <div className="flex items-center space-x-2">
                <CreditCard className="w-4 h-4 text-emerald-600" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Phương Thức Thanh Toán & Đối Soát Tiền Mặt</h3>
              </div>
              <span className="text-[10px] text-slate-400">Dòng tiền</span>
            </div>

            <div className="space-y-3">
              {(displayKpis?.paymentBreakdown || [
                { method: 'Chuyển khoản VietQR 24/7', share: 45, risk: 'Thấp (Tiền về tức thì)' },
                { method: 'Trả góp 0% (Fundiin/Visa)', share: 25, risk: 'Thấp (Giải ngân 24h)' },
                { method: 'Thanh toán COD khi nhận', share: 18, risk: 'Trung bình (Giam tiền 7-10N)' },
                { method: 'Thẻ tín dụng Quốc tế', share: 12, risk: 'Thấp (Phí 1.8%)' }
              ]).map((pm: any, idx: number) => (
                <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5 text-xs">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-slate-800 dark:text-slate-200">{pm.method}</span>
                    <span className="text-slate-900 dark:text-slate-100 font-mono">{pm.share}% tỷ trọng</span>
                  </div>
                  <div className="flex justify-between items-center text-[11px] text-slate-500 dark:text-slate-400">
                    <div className="w-1/2 bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                      <div className="bg-emerald-600 h-full rounded-full" style={{ width: `${pm.share}%` }} />
                    </div>
                    <span className="font-medium text-slate-600 dark:text-slate-300">{pm.risk}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 6. Top Selling Products & Critical Stockout Alerts */}
      {enabledSections.includes('top_products') && displayKpis?.topSellingProducts && (
        <div className="bg-white dark:bg-[#151c2c] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-150 dark:border-slate-800">
            <div className="flex items-center space-x-2">
              <Package className="w-4 h-4 text-[#d70018]" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Top 5 Sản Phẩm Bán Chạy & Đóng Góp Doanh Số Cao Nhất</h3>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">Dựa trên đơn giao thành công</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th className="py-2.5 px-3">Top</th>
                  <th className="py-2.5 px-3">Tên sản phẩm</th>
                  <th className="py-2.5 px-3">Danh mục</th>
                  <th className="py-2.5 px-3 text-center">Số lượng bán</th>
                  <th className="py-2.5 px-3 text-right">Doanh thu tạo ra</th>
                  <th className="py-2.5 px-3 text-center">Trạng thái kho</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-150 dark:divide-slate-800">
                {displayKpis.topSellingProducts.map((p: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-850/50 transition">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-400">#{idx + 1}</td>
                    <td className="py-2.5 px-3 font-bold text-slate-900 dark:text-slate-100">{p.name}</td>
                    <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400">{p.category}</td>
                    <td className="py-2.5 px-3 text-center font-mono font-bold text-blue-600 dark:text-blue-400">{p.qty} cái</td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-[#d70018] dark:text-red-400">{formatVND(p.revenue)}</td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
                        Còn hàng tốt
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 7. Pinned Widgets from AI Chatbot */}
      {enabledSections.includes('pinned_widgets') && pinnedWidgets.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center space-x-2">
            <Pin className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Biểu đồ được ghim từ Trợ lý Dữ liệu AI ({pinnedWidgets.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pinnedWidgets.map((w, i) => (
              <div key={i} className="bg-white dark:bg-[#151c2c] p-5 rounded-2xl border border-blue-200 dark:border-blue-900/60 shadow-xs space-y-3">
                <div className="flex justify-between items-start">
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">{w.title}</h4>
                  <span className="text-[10px] bg-blue-50 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded font-semibold">
                    Đã ghim
                  </span>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl text-xs space-y-2 border border-slate-150 dark:border-slate-800">
                  {w.data?.slice(0, 4).map((row: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-slate-700 dark:text-slate-300">
                      <span>{row.name || row.week || row.period}</span>
                      <strong className="text-slate-900 dark:text-slate-100">{row.daysInStock ? `${row.daysInStock} ngày` : row.actual ? `${row.actual} tỷ` : ''}</strong>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 8. CUSTOM METRIC & WIDGET SELECTOR MODAL */}
      {showConfigModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white dark:bg-[#151c2c] text-slate-800 dark:text-slate-100 rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 relative space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <div className="flex items-center space-x-2">
                <SlidersHorizontal className="w-5 h-5 text-[#d70018]" />
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                    Tùy Chỉnh Báo Cáo & Số Liệu Hiển Thị
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Chọn các thẻ chỉ số và khối biểu đồ bạn muốn theo dõi trên trang Tổng quan
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowConfigModal(false)}
                className="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Metric Cards Checkboxes */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center justify-between">
                <span>1. Thẻ chỉ số tài chính & vận hành (KPI Cards):</span>
                <span className="text-[10px] text-slate-400 font-normal">Đã chọn {enabledMetrics.length} thẻ</span>
              </h4>

              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { key: 'net_revenue' as MetricKey, label: 'Doanh Thu Thuần' },
                  { key: 'gross_profit' as MetricKey, label: 'Lợi Nhuận Gộp (Margin)' },
                  { key: 'cm1_margin' as MetricKey, label: 'Biên Đóng Góp CM1' },
                  { key: 'cm2_margin' as MetricKey, label: 'Biên Tiếp Thị CM2' },
                  { key: 'completed_orders' as MetricKey, label: 'Số Đơn Hàng Thành Công' },
                  { key: 'aov' as MetricKey, label: 'Giá Trị Đơn TB (AOV)' },
                  { key: 'inventory_value' as MetricKey, label: 'Vốn Tồn Kho & Tuổi Tồn' },
                  { key: 'cod_return_rate' as MetricKey, label: 'Tỷ Lệ Hoàn COD (Boom Hàng)' },
                  { key: 'repeat_customer_rate' as MetricKey, label: 'Tỷ Lệ Mua Lặp Lại' },
                  { key: 'roas' as MetricKey, label: 'Hiệu Quả Quảng Cáo (ROAS)' }
                ].map(item => {
                  const isChecked = enabledMetrics.includes(item.key);
                  return (
                    <label
                      key={item.key}
                      onClick={() => toggleMetric(item.key)}
                      className={`p-2.5 rounded-xl border text-xs font-medium flex items-center justify-between cursor-pointer transition select-none ${
                        isChecked
                          ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200 font-bold'
                          : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      <span>{item.label}</span>
                      <div className={`w-4 h-4 rounded flex items-center justify-center border ${isChecked ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-300 dark:border-slate-700'}`}>
                        {isChecked && <Check className="w-3 h-3" />}
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Analytic Section Checkboxes */}
            <div className="space-y-3 pt-2 border-t border-slate-150 dark:border-slate-800">
              <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center justify-between">
                <span>2. Các khối phân tích chuyên sâu (Analysis Sections):</span>
                <span className="text-[10px] text-slate-400 font-normal">Đã chọn {enabledSections.length} khối</span>
              </h4>

              <div className="space-y-1.5 text-xs">
                {[
                  { key: 'pnl_waterfall' as SectionKey, label: 'Thác Nước Tài Chính P&L (GMV -> CM1 -> CM2 -> CM3)' },
                  { key: 'revenue_target_chart' as SectionKey, label: 'Biểu Đồ Doanh Thu Thực Tế vs Kế Hoạch (8 tuần)' },
                  { key: 'category_chart' as SectionKey, label: 'Biểu Đồ Cơ Cấu Doanh Thu Theo Nhóm Hàng' },
                  { key: 'channel_breakdown' as SectionKey, label: 'Ma Trận Đánh Giá Hiệu Quả & Rủi Ro Từng Kênh Bán' },
                  { key: 'payment_method_breakdown' as SectionKey, label: 'Phương Thức Thanh Toán & Đối Soát Dòng Tiền Mặt' },
                  { key: 'top_products' as SectionKey, label: 'Top 5 Sản Phẩm Bán Chạy & Cảnh Báo Kho' },
                  { key: 'pinned_widgets' as SectionKey, label: 'Các Biểu Đồ Đã Ghim Từ Trợ Lý Dữ Liệu AI' }
                ].map(item => {
                  const isChecked = enabledSections.includes(item.key);
                  return (
                    <label
                      key={item.key}
                      onClick={() => toggleSection(item.key)}
                      className={`p-2.5 rounded-xl border text-xs font-medium flex items-center justify-between cursor-pointer transition select-none ${
                        isChecked
                          ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/30 text-blue-900 dark:text-blue-200 font-bold'
                          : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      <span>{item.label}</span>
                      <div className={`w-4 h-4 rounded flex items-center justify-center border ${isChecked ? 'bg-blue-600 border-blue-600 text-white' : 'border-slate-300 dark:border-slate-700'}`}>
                        {isChecked && <Check className="w-3 h-3" />}
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex justify-between items-center pt-3 border-t border-slate-200 dark:border-slate-800">
              <button
                type="button"
                onClick={handleResetConfig}
                className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-semibold underline cursor-pointer"
              >
                Khôi phục mặc định
              </button>

              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setShowConfigModal(false)}
                  className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer"
                >
                  Hủy
                </button>
                <button
                  type="button"
                  onClick={handleSaveConfig}
                  className="px-5 py-2 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                >
                  Áp Dụng Cấu Hình
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
