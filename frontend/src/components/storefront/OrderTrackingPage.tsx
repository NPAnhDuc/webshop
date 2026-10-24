import React, { useState, useEffect } from 'react';
import {
  PackageCheck,
  Search,
  CheckCircle2,
  Clock,
  Truck,
  AlertCircle,
  ArrowLeft,
  Home,
  ShieldCheck,
  PhoneCall,
  MapPin,
  Calendar,
  CreditCard,
  FileText,
  RotateCcw,
  Sparkles,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { lookupOrder } from '../../services/api';
import { Order } from '../../types';

interface OrderTrackingPageProps {
  initialOrderCode?: string;
  onBackToHome: () => void;
  onNavigateProduct?: (productSlugOrId: string) => void;
}

export const OrderTrackingPage: React.FC<OrderTrackingPageProps> = ({
  initialOrderCode = '',
  onBackToHome,
  onNavigateProduct
}) => {
  const [activeTab, setActiveTab] = useState<'order' | 'warranty'>('order');

  // Order lookup state
  const [phone, setPhone] = useState('0981234567');
  const [orderCode, setOrderCode] = useState(initialOrderCode || 'ORD-2026-1005');
  const [loadingOrder, setLoadingOrder] = useState(false);
  const [order, setOrder] = useState<Order | null>(null);
  const [orderError, setOrderError] = useState<string | null>(null);

  // Warranty lookup state
  const [serialQuery, setSerialQuery] = useState('');
  const [warrantyResult, setWarrantyResult] = useState<any | null>(null);
  const [loadingWarranty, setLoadingWarranty] = useState(false);

  // Auto search on mount if initialOrderCode is present
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (orderCode && phone) {
      handleSearchOrder();
    }
  }, []);

  const handleSearchOrder = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!phone.trim() || !orderCode.trim()) {
      setOrderError('Vui lòng nhập cả số điện thoại và mã đơn hàng');
      return;
    }

    setLoadingOrder(true);
    setOrderError(null);
    setOrder(null);

    try {
      const res = await lookupOrder(phone.trim(), orderCode.trim());
      if (res.success && res.data) {
        setOrder(res.data);
      } else {
        setOrderError(res.message || 'Không tìm thấy đơn hàng. Quý khách vui lòng kiểm tra lại số điện thoại hoặc mã đơn.');
      }
    } catch (err) {
      console.error(err);
      setOrderError('Lỗi kết nối đến máy chủ tra cứu. Vui lòng thử lại sau vài giây.');
    } finally {
      setLoadingOrder(false);
    }
  };

  const handleSearchWarranty = (e: React.FormEvent) => {
    e.preventDefault();
    if (!serialQuery.trim()) return;

    setLoadingWarranty(true);
    setTimeout(() => {
      // Mock warranty information lookup
      setWarrantyResult({
        serial: serialQuery.trim().toUpperCase(),
        productName: 'Laptop ASUS ROG Strix G16 (2026) G614JVR',
        purchaseDate: '15/08/2025',
        warrantyExpiry: '15/08/2027',
        remainingMonths: 18,
        status: 'active',
        serviceType: 'Bảo hành chính hãng 24 tháng tận nơi (On-site ASUS VIP Care)',
        retailer: 'TechStore Studio Flagship Store',
        rmaHistory: [
          { date: '20/01/2026', note: 'Bảo dưỡng định kỳ: Vệ sinh tản nhiệt & tra keo kim loại lỏng miễn phí', status: 'Hoàn tất' }
        ]
      });
      setLoadingWarranty(false);
    }, 400);
  };

  const getStepState = (currentStatus: string, stepIndex: number) => {
    const statuses = ['new', 'confirmed', 'shipping', 'completed'];
    const currentIdx = statuses.indexOf(currentStatus);
    if (currentIdx === -1) return 'pending';
    if (currentIdx > stepIndex) return 'completed';
    if (currentIdx === stepIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 sm:px-6 py-5 w-full flex-1 text-slate-800 dark:text-slate-100">
      {/* 1. Breadcrumbs */}
      <nav className="mb-4 flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
        <button
          onClick={onBackToHome}
          className="hover:text-[#d70018] dark:hover:text-red-400 font-bold flex items-center space-x-1.5 transition cursor-pointer"
        >
          <Home className="w-3.5 h-3.5" />
          <span>Trang Chủ</span>
        </button>
        <span className="text-slate-400">/</span>
        <span className="text-slate-700 dark:text-slate-300 font-semibold">Tra Cứu & Hậu Mãi</span>
        <span className="text-slate-400">/</span>
        <span className="text-[#d70018] dark:text-red-400 font-extrabold uppercase">
          {activeTab === 'order' ? 'Tiến Độ Đơn Hàng' : 'Bảo Hành Điện Tử'}
        </span>
      </nav>

      {/* 2. Page Header Banner */}
      <div className="mb-6 bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 text-white rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-radial from-red-600/10 via-transparent to-transparent pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-red-600/20 text-red-400 border border-red-500/30 text-[11px] font-bold">
              <PackageCheck className="w-3.5 h-3.5" />
              <span>HỆ THỐNG TRA CỨU TỰ ĐỘNG TECHSTORE</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              Trung Tâm Tra Cứu Đơn Hàng & Bảo Hành
            </h1>
            <p className="text-xs sm:text-sm text-slate-300">
              Kiểm tra hành trình vận chuyển theo thời gian thực, phiếu bảo hành điện tử chính hãng và lịch sử bảo dưỡng máy tính của bạn.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onBackToHome}
              className="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer shadow-xs active:scale-95"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Quay Lại Mua Sắm</span>
            </button>
          </div>
        </div>

        {/* Tab switch pills */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('order')}
            className={`px-4 py-2 rounded-xl text-xs font-extrabold transition cursor-pointer flex items-center space-x-2 ${
              activeTab === 'order'
                ? 'bg-[#d70018] text-white shadow-md'
                : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Truck className="w-3.5 h-3.5" />
            <span>Tiến Độ Vận Chuyển Đơn Hàng</span>
          </button>
          <button
            onClick={() => setActiveTab('warranty')}
            className={`px-4 py-2 rounded-xl text-xs font-extrabold transition cursor-pointer flex items-center space-x-2 ${
              activeTab === 'warranty'
                ? 'bg-[#d70018] text-white shadow-md'
                : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Tra Cứu Bảo Hành Điện Tử (Serial / IMEI)</span>
          </button>
        </div>
      </div>

      {/* 3. Main Tab Content */}
      {activeTab === 'order' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Search Form */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-5 shadow-xs">
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-slate-100 flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
                <Search className="w-4 h-4 text-[#d70018]" />
                <span>Nhập Thông Tin Tra Cứu</span>
              </h3>

              <form onSubmit={handleSearchOrder} className="mt-4 space-y-3.5 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Số điện thoại đặt hàng:
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={e => setPhone(e.target.value)}
                    placeholder="Ví dụ: 0981234567"
                    className="w-full px-3.5 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-[#d70018] font-medium"
                    required
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Mã đơn hàng:
                  </label>
                  <input
                    type="text"
                    value={orderCode}
                    onChange={e => setOrderCode(e.target.value.toUpperCase())}
                    placeholder="Ví dụ: ORD-2026-1005"
                    className="w-full px-3.5 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-[#d70018] font-mono font-bold"
                    required
                  />
                  <p className="text-[10px] text-slate-400 mt-1">
                    * Mã đơn được gửi qua tin nhắn SMS / Zalo ngay sau khi quý khách đặt mua.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loadingOrder}
                  className="w-full py-3 bg-[#d70018] hover:bg-[#b91c1c] disabled:bg-slate-300 text-white font-extrabold rounded-xl transition flex items-center justify-center space-x-2 shadow-xs cursor-pointer active:scale-95"
                >
                  <Search className="w-4 h-4" />
                  <span>{loadingOrder ? 'Đang Tra Cứu...' : 'Tra Cứu Ngay'}</span>
                </button>
              </form>

              {/* Sample orders shortcut */}
              <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-800 text-[11px] text-slate-500">
                <span className="font-semibold block mb-1">Mã đơn mẫu thử nghiệm:</span>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    type="button"
                    onClick={() => {
                      setPhone('0981234567');
                      setOrderCode('ORD-2026-1005');
                    }}
                    className="px-2 py-1 bg-gray-100 dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-700 dark:text-slate-300 hover:text-[#d70018] rounded-lg font-mono text-[10px] transition"
                  >
                    ORD-2026-1005
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setPhone('0912345678');
                      setOrderCode('ORD-2026-1002');
                    }}
                    className="px-2 py-1 bg-gray-100 dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-700 dark:text-slate-300 hover:text-[#d70018] rounded-lg font-mono text-[10px] transition"
                  >
                    ORD-2026-1002
                  </button>
                </div>
              </div>
            </div>

            {/* Support helpline box */}
            <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-5 shadow-xs space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Tổng Đài Trợ Giúp Vận Chuyển
              </h4>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-950/60 text-[#d70018] flex items-center justify-center font-bold">
                  <PhoneCall className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-base font-black text-[#d70018] font-mono block">1900.0323</span>
                  <span className="text-[11px] text-slate-500">Miễn phí cước gọi (8:00 - 21:30 hàng ngày)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Order Status & Details */}
          <div className="lg:col-span-2 space-y-4">
            {orderError && (
              <div className="p-4 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 rounded-2xl text-xs text-red-700 dark:text-red-300 flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <div>
                  <p className="font-bold">Không tìm thấy thông tin đơn hàng</p>
                  <p className="text-[11px]">{orderError}</p>
                </div>
              </div>
            )}

            {order ? (
              <div className="space-y-4">
                {/* 1. Progress Step Tracker */}
                <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-100 dark:border-slate-800 gap-2">
                    <div>
                      <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400">Mã đơn hàng</span>
                      <h2 className="text-xl font-black text-[#d70018] dark:text-red-400 font-mono">
                        {order.orderCode}
                      </h2>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-slate-500">Trạng thái:</span>
                      <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 uppercase">
                        {order.status === 'new'
                          ? 'Mới tiếp nhận'
                          : order.status === 'confirmed'
                          ? 'Đã duyệt & Đang soạn hàng'
                          : order.status === 'shipping'
                          ? 'Đang giao hàng'
                          : 'Giao hàng thành công'}
                      </span>
                    </div>
                  </div>

                  {/* 4-Step Visual Timeline */}
                  <div className="mt-6">
                    <div className="grid grid-cols-4 gap-2 text-center relative">
                      {[
                        { label: 'Đặt hàng thành công', sub: 'Chờ duyệt', icon: CheckCircle2, status: 'new' },
                        { label: 'Duyệt & Đóng gói', sub: 'Kho xử lý', icon: PackageCheck, status: 'confirmed' },
                        { label: 'Đang vận chuyển', sub: 'Shipper giao', icon: Truck, status: 'shipping' },
                        { label: 'Hoàn tất giao nhận', sub: 'Đã nhận hàng', icon: ShieldCheck, status: 'completed' }
                      ].map((step, idx) => {
                        const state = getStepState(order.status, idx);
                        const StepIcon = step.icon;

                        return (
                          <div key={idx} className="flex flex-col items-center relative">
                            {/* Line connecting */}
                            {idx < 3 && (
                              <div
                                className={`hidden sm:block absolute top-4 left-1/2 w-full h-1 -z-0 ${
                                  state === 'completed'
                                    ? 'bg-emerald-500'
                                    : 'bg-gray-200 dark:bg-slate-700'
                                }`}
                              />
                            )}

                            <div
                              className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs relative z-10 transition ${
                                state === 'completed'
                                  ? 'bg-emerald-500 text-white shadow-md'
                                  : state === 'active'
                                  ? 'bg-[#d70018] text-white ring-4 ring-red-100 dark:ring-red-950 shadow-md animate-pulse'
                                  : 'bg-gray-100 dark:bg-slate-800 text-slate-400 border border-gray-200 dark:border-slate-700'
                              }`}
                            >
                              <StepIcon className="w-4 h-4" />
                            </div>

                            <span className="mt-2 text-[11px] sm:text-xs font-bold text-slate-800 dark:text-slate-200 leading-tight">
                              {step.label}
                            </span>
                            <span className="text-[10px] text-slate-400 hidden sm:block">
                              {step.sub}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* 2. Customer & Delivery Address Card */}
                <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-5 shadow-xs grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Thông tin người nhận</span>
                    <p className="font-extrabold text-sm text-slate-900 dark:text-slate-100">
                      {order.customerName}
                    </p>
                    <p className="text-slate-600 dark:text-slate-300 font-mono">
                      {order.customerPhone}
                    </p>
                    <p className="text-slate-500 text-[11px] flex items-center space-x-1 pt-1">
                      <MapPin className="w-3.5 h-3.5 text-[#d70018] flex-shrink-0" />
                      <span>{order.customerAddress}, {order.customerCity}</span>
                    </p>
                  </div>

                  <div className="space-y-1.5 sm:border-l sm:border-gray-100 dark:sm:border-slate-800 sm:pl-4">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Hình thức thanh toán & Vận chuyển</span>
                    <div className="flex items-center space-x-2 pt-0.5">
                      <CreditCard className="w-4 h-4 text-emerald-600" />
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        {order.paymentMethod === 'cod' ? 'Thanh toán tiền mặt khi nhận hàng (COD)' : 'Chuyển khoản QR TechStore'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Đơn vị giao hàng: <strong className="text-slate-700 dark:text-slate-300">TechStore Express (Hỏa tốc)</strong>
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Thời gian dự kiến nhận: <strong className="text-emerald-600 dark:text-emerald-400 font-bold">1 - 2 ngày làm việc</strong>
                    </p>
                  </div>
                </div>

                {/* 3. Products in Order */}
                <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-5 shadow-xs space-y-3">
                  <h3 className="font-extrabold text-sm text-slate-900 dark:text-slate-100 pb-2 border-b border-gray-100 dark:border-slate-800">
                    Sản Phẩm Trong Đơn Hàng ({order.items?.length || 0})
                  </h3>

                  <div className="divide-y divide-gray-100 dark:divide-slate-800">
                    {(order.items || []).map((it, idx) => (
                      <div key={idx} className="py-3 flex items-center justify-between gap-4">
                        <div className="flex items-center space-x-3 min-w-0">
                          <div className="w-12 h-12 rounded-xl bg-gray-50 dark:bg-slate-800 border border-gray-100 dark:border-slate-700 p-1 flex-shrink-0 flex items-center justify-center font-bold text-xs text-slate-400">
                            PC
                          </div>
                          <div className="min-w-0">
                            <h4
                              onClick={() => onNavigateProduct && it.productId && onNavigateProduct(it.productId)}
                              className="text-xs font-bold text-slate-900 dark:text-slate-100 hover:text-[#d70018] cursor-pointer truncate"
                            >
                              {it.productName}
                            </h4>
                            <span className="text-[11px] text-slate-500">
                              Đơn giá: {new Intl.NumberFormat('vi-VN').format(it.price)}₫ × <strong className="text-slate-800 dark:text-slate-200">{it.qty}</strong>
                            </span>
                          </div>
                        </div>

                        <div className="text-right flex-shrink-0 font-mono font-bold text-xs sm:text-sm text-slate-900 dark:text-slate-100">
                          {new Intl.NumberFormat('vi-VN').format(it.price * it.qty)}₫
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="pt-3 border-t border-gray-100 dark:border-slate-800 flex justify-between items-center text-sm font-extrabold">
                    <span className="text-slate-600 dark:text-slate-300">Tổng thanh toán:</span>
                    <span className="text-base sm:text-lg font-black text-[#d70018] dark:text-red-400 font-mono">
                      {new Intl.NumberFormat('vi-VN').format(order.total)}₫
                    </span>
                  </div>
                </div>

                {/* 4. Timeline details log */}
                {order.statusTimeline && order.statusTimeline.length > 0 && (
                  <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-5 shadow-xs space-y-3">
                    <h3 className="font-extrabold text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      Nhật Ký Xử Lý Đơn Hàng
                    </h3>
                    <div className="pl-3 border-l-2 border-emerald-500 space-y-3 text-xs">
                      {order.statusTimeline.map((tl, idx) => (
                        <div key={idx} className="relative pl-3">
                          <span className="absolute -left-[19px] top-1.5 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-white dark:ring-slate-900" />
                          <p className="font-bold text-slate-800 dark:text-slate-200">{tl.note || tl.status}</p>
                          <p className="text-[10px] text-slate-400 font-mono">
                            {new Date(tl.timestamp).toLocaleString('vi-VN')}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-12 text-center space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-gray-50 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                  <PackageCheck className="w-8 h-8" />
                </div>
                <h3 className="font-black text-slate-900 dark:text-slate-100 text-base">
                  Vui lòng nhập thông tin để tra cứu
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                  Điền số điện thoại và mã đơn hàng ở biểu mẫu bên trái, sau đó nhấn "Tra Cứu Ngay" để xem tiến độ đóng gói và giao nhận.
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Tab 2: Warranty Lookup */
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs">
            <h3 className="font-black text-base text-slate-900 dark:text-slate-100 flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
              <ShieldCheck className="w-5 h-5 text-[#d70018]" />
              <span>Tra Cứu Thời Hạn Bảo Hành Điện Tử</span>
            </h3>

            <form onSubmit={handleSearchWarranty} className="mt-4 space-y-3 text-xs">
              <label className="block font-bold text-slate-700 dark:text-slate-300">
                Nhập Số Serial (S/N) hoặc Mã IMEI sản phẩm:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={serialQuery}
                  onChange={e => setSerialQuery(e.target.value.toUpperCase())}
                  placeholder="Ví dụ: ROG-SN-89240129 hoặc SỐ ĐT"
                  className="flex-1 px-4 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-mono font-bold focus:outline-none focus:border-[#d70018]"
                  required
                />
                <button
                  type="submit"
                  disabled={loadingWarranty}
                  className="px-6 py-2.5 bg-[#d70018] hover:bg-[#b91c1c] text-white font-extrabold rounded-xl transition flex items-center space-x-1.5 shadow-xs cursor-pointer active:scale-95"
                >
                  <Search className="w-4 h-4" />
                  <span>{loadingWarranty ? 'Đang Tra...' : 'Tra Cứu'}</span>
                </button>
              </div>
              <p className="text-[11px] text-slate-500">
                * Số Serial thường được in trên tem mã vạch ở đáy laptop, thân vỏ case hoặc trên vỏ hộp sản phẩm.
              </p>
            </form>
          </div>

          {warrantyResult && (
            <div className="bg-white dark:bg-[#151c2c] border border-emerald-300 dark:border-emerald-800 rounded-3xl p-6 shadow-md space-y-4 animate-in fade-in">
              <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <span className="font-extrabold text-sm text-emerald-700 dark:text-emerald-400">
                    BẢO HÀNH CHÍNH HÃNG HỢP LỆ
                  </span>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200">
                  S/N: {warrantyResult.serial}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400">Tên thiết bị</span>
                  <p className="font-extrabold text-sm text-slate-900 dark:text-slate-100">{warrantyResult.productName}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400">Gói dịch vụ</span>
                  <p className="font-bold text-slate-800 dark:text-slate-200">{warrantyResult.serviceType}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400">Ngày kích hoạt</span>
                  <p className="font-semibold text-slate-700 dark:text-slate-300 font-mono">{warrantyResult.purchaseDate}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400">Hạn bảo hành đến ngày</span>
                  <p className="font-black text-emerald-600 dark:text-emerald-400 font-mono text-sm">{warrantyResult.warrantyExpiry} (Còn {warrantyResult.remainingMonths} tháng)</p>
                </div>
              </div>

              {/* Maintenance history */}
              {warrantyResult.rmaHistory && warrantyResult.rmaHistory.length > 0 && (
                <div className="pt-3 border-t border-gray-100 dark:border-slate-800 space-y-2">
                  <span className="font-bold text-xs text-slate-700 dark:text-slate-300 block">Lịch sử bảo dưỡng / Sửa chữa:</span>
                  <div className="space-y-1.5 text-xs">
                    {warrantyResult.rmaHistory.map((item: any, idx: number) => (
                      <div key={idx} className="p-3 bg-gray-50 dark:bg-slate-900 rounded-xl flex justify-between items-center">
                        <div>
                          <p className="font-semibold text-slate-800 dark:text-slate-200">{item.note}</p>
                          <span className="text-[10px] text-slate-400 font-mono">{item.date}</span>
                        </div>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400">
                          {item.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
