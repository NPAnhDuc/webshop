import React, { useState, useEffect } from 'react';
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
  Sparkles
} from 'lucide-react';
import { fetchAdminKPIs, fetchAdminCharts, fetchPinnedWidgets } from '../../services/api';
import { ChartSpec } from '../../types';
import { CuteRobotAvatar } from '../common/CuteRobotAvatar';

export const DashboardView: React.FC<{ onNavigateToChatbot: () => void }> = ({ onNavigateToChatbot }) => {
  const [kpis, setKpis] = useState<any>(null);
  const [charts, setCharts] = useState<ChartSpec[]>([]);
  const [pinnedWidgets, setPinnedWidgets] = useState<ChartSpec[]>([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return <div className="text-center py-16 text-slate-400 text-xs">Đang tải dữ liệu báo cáo kinh doanh...</div>;
  }

  return (
    <div className="space-y-8">
      {/* 1. Header with Period Filter & Bot Prompt */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 gap-4">
        <div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight">
            Báo Cáo Sức Khỏe Kinh Doanh & Vận Hành
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Dữ liệu tổng hợp theo thời gian thực từ đơn hàng, kho và chiến dịch
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onNavigateToChatbot}
            className="group relative px-4 py-2 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 hover:from-slate-800 hover:to-indigo-900 text-white rounded-xl text-xs font-bold flex items-center space-x-3 shadow-md hover:shadow-lg transition border border-indigo-500/30 active:scale-95"
          >
            <CuteRobotAvatar
              mode="admin"
              size="sm"
              isWaving={true}
              showSpeechBubble={false}
              className="w-7 h-7 flex-shrink-0 group-hover:scale-110 transition-transform"
            />
            <div className="text-left">
              <span className="block text-white font-bold leading-tight">Hỏi Trợ Lý Dữ Liệu AI</span>
              <span className="block text-[10px] text-amber-300 font-normal">Sẵn sàng phân tích KPI & RAG &rarr;</span>
            </div>
          </button>
        </div>
      </div>

      {/* 2. Row of 8 Standard Retail KPI Cards (Section 6.5.3 & 12.6) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Doanh thu */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Tổng Doanh Thu</span>
            <DollarSign className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-900">
            {new Intl.NumberFormat('vi-VN').format(kpis?.totalRevenue || 0)}₫
          </div>
          <p className="mt-1 text-[11px] text-emerald-600 font-medium flex items-center">
            <ArrowUpRight className="w-3 h-3 mr-0.5" /> +14.2% so với tháng trước
          </p>
        </div>

        {/* Lợi nhuận gộp & Biên % */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Lợi Nhuận Gộp (Margin)</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-xl font-bold text-emerald-700">
            {new Intl.NumberFormat('vi-VN').format(kpis?.grossProfit || 0)}₫
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            Biên lợi nhuận gộp: <strong className="text-slate-800">{kpis?.grossMarginPercent}%</strong>
          </p>
        </div>

        {/* Số đơn & AOV */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Số Đơn Hàng Thành Công</span>
            <ShoppingBag className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-900">
            {kpis?.totalOrders || 0} đơn
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            AOV (Giá trị TB): <strong className="text-slate-800">{new Intl.NumberFormat('vi-VN').format(kpis?.aov || 0)}₫</strong>
          </p>
        </div>

        {/* Sức khỏe kho: Giá trị tồn & Ngày tồn */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Vốn Tồn Kho & Tuổi Tồn</span>
            <Package className="w-4 h-4 text-amber-600" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-900">
            {new Intl.NumberFormat('vi-VN').format(kpis?.inventoryValue || 0)}₫
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            Ngày tồn kho TB: <strong className="text-amber-700">{kpis?.avgInventoryDays} ngày</strong> (An toàn: ≤60)
          </p>
        </div>
      </div>

      {/* 3. Core Analytical Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Revenue vs Plan (Line SVG) */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Doanh thu thực tế so với Kế hoạch (8 tuần gần nhất)
            </h3>
            <span className="text-[11px] text-slate-400">Đơn vị: Tỷ VND</span>
          </div>

          <div className="h-64 flex items-end justify-between gap-3 pt-6 pb-2 px-2 border-b border-slate-100">
            {charts[0]?.data?.map((d: any, idx: number) => {
              const maxVal = 3.5;
              const actualH = (d.actual / maxVal) * 100;
              const targetH = (d.target / maxVal) * 100;

              return (
                <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group relative">
                  {/* Tooltip */}
                  <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[10px] px-2 py-1 rounded shadow pointer-events-none whitespace-nowrap z-10">
                    {d.period}: Thực tế {d.actual} tỷ / Chỉ tiêu {d.target} tỷ
                  </div>

                  <div className="w-full flex items-end justify-center space-x-1 h-full">
                    {/* Target bar outline / dashed marker */}
                    <div
                      className="w-2.5 bg-slate-200 rounded-t"
                      style={{ height: `${targetH}%` }}
                      title={`Chỉ tiêu: ${d.target} tỷ`}
                    />
                    {/* Actual bar */}
                    <div
                      className="w-3 bg-blue-600 rounded-t transition-all group-hover:bg-blue-700"
                      style={{ height: `${actualH}%` }}
                      title={`Thực tế: ${d.actual} tỷ`}
                    />
                  </div>
                  <span className="text-[10px] text-slate-500 mt-2 font-medium">{d.period}</span>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-center space-x-6 text-xs text-slate-600 pt-1">
            <span className="flex items-center space-x-1.5">
              <span className="w-3 h-3 bg-blue-600 rounded-xs" />
              <span>Doanh thu thực tế</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-3 h-3 bg-slate-300 rounded-xs" />
              <span>Chỉ tiêu kế hoạch</span>
            </span>
          </div>
        </div>

        {/* Chart 2: Category Breakdown (Bar SVG) */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Cơ cấu doanh thu theo nhóm hàng tháng 10/2026
            </h3>
            <span className="text-[11px] text-slate-400">Tỉ trọng (%)</span>
          </div>

          <div className="space-y-4 pt-4">
            {charts[1]?.data?.map((cat: any, idx: number) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-700">
                  <span>{cat.category}</span>
                  <span className="text-slate-900">{cat.share}%</span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div
                    className="bg-blue-600 h-full rounded-full transition-all duration-500"
                    style={{ width: `${cat.share}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <p className="text-[11px] text-slate-500 pt-4 border-t border-slate-100">
            * Nhóm Laptop văn phòng và Gaming chiếm tới 67% tổng doanh thu của toàn cửa hàng.
          </p>
        </div>
      </div>

      {/* 4. Pinned Widgets from AI Chatbot (Section 6.5.1 & 12.6) */}
      {pinnedWidgets.length > 0 && (
        <div className="space-y-4 pt-4">
          <div className="flex items-center space-x-2">
            <Pin className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Biểu đồ được ghim từ Trợ lý Dữ liệu AI ({pinnedWidgets.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pinnedWidgets.map((w, i) => (
              <div key={i} className="bg-white p-5 rounded-xl border border-blue-200 shadow-sm space-y-3">
                <div className="flex justify-between items-start">
                  <h4 className="text-xs font-bold text-slate-900">{w.title}</h4>
                  <span className="text-[10px] bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-semibold">
                    Đã ghim
                  </span>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg text-xs space-y-2">
                  {w.data?.slice(0, 4).map((row: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-slate-700">
                      <span>{row.name || row.week || row.period}</span>
                      <strong className="text-slate-900">{row.daysInStock ? `${row.daysInStock} ngày` : row.actual ? `${row.actual} tỷ` : ''}</strong>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
