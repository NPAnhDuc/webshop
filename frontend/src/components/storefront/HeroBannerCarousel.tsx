import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  SlidersHorizontal,
  ArrowRight,
  Flame,
  ChevronLeft,
  ChevronRight,
  Zap,
  RotateCcw,
  Gift,
  CreditCard,
  ChevronRight as ChevronRightIcon,
  ShieldCheck,
  Truck,
  Wrench,
  CheckCircle2,
  Laptop,
  Monitor,
  Cpu,
  Gamepad2,
  Layers,
  HardDrive,
  Box,
  Tag
} from 'lucide-react';

interface HeroBannerCarouselProps {
  onNavigatePCBuilder: () => void;
  onFilterDemand: (demand: string) => void;
  onSelectCategory?: (category: string) => void;
}

export const HeroBannerCarousel: React.FC<HeroBannerCarouselProps> = ({
  onNavigatePCBuilder,
  onFilterDemand,
  onSelectCategory
}) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      badge: 'DEAL HOT CHÍNH HÃNG',
      badgeColor: 'bg-[#d70018] text-white font-bold',
      title: 'Mừng Đại Lễ Công Nghệ • Deal Thật Hời',
      subtitle: 'Giảm giá cực sốc tới 25% cho toàn bộ dòng laptop sinh viên, văn phòng và phụ kiện chính hãng.',
      ctaText: 'Xem Deal Sốc',
      demand: 'thin_light',
      image: '/images/laptop/asus-zenbook-14-um425ua-675dc82b5a64.png',
      priceTag: 'Chỉ từ 14.990.000₫',
      bgColor: 'from-slate-950 via-slate-900 to-slate-950'
    },
    {
      badge: 'SIÊU PHẨM GAMING 2026',
      badgeColor: 'bg-red-600 text-white font-black',
      title: 'Laptop Gaming RTX 40 Series • Chiến Mọi Tựa Game',
      subtitle: 'Lenovo Legion Slim, Asus TUF, Acer Nitro cấu hình Intel Gen 13/14 + RTX 4060/4070 mượt mà.',
      ctaText: 'Xem Laptop Gaming',
      demand: 'gaming',
      image: '/images/laptop/lenovo-legion-slim-5i-16irh8-7bf3496c4c55.png',
      priceTag: 'Tặng Balo + Chuột Gaming',
      bgColor: 'from-zinc-950 via-slate-900 to-black'
    },
    {
      badge: 'ĐẶC QUYỀN TECHSTORE',
      badgeColor: 'bg-slate-900 text-amber-400 font-black border border-slate-700',
      title: 'Xây Dựng Cấu Hình PC • Tự Ráp Máy Nhận Quà 2 Triệu',
      subtitle: 'Tự tay chọn CPU, Main, VGA theo ý muốn với tính năng thẩm định phần cứng độc quyền. Lắp ráp siêu tốc 2H.',
      ctaText: 'Vào Trình Build PC Ngay',
      isBuilder: true,
      image: '/images/case/nzxt-h5-flow-2024-6d80f639a090.jpg',
      priceTag: 'Trả góp 0% duyệt 15P',
      bgColor: 'from-slate-950 via-zinc-900 to-black'
    },
    {
      badge: 'CHUẨN MÀU ĐỒ HỌA',
      badgeColor: 'bg-blue-600 text-white font-bold',
      title: 'Màn Hình & Laptop OLED • Tặng Gói Cân Màu SpyderX',
      subtitle: 'Hình ảnh sống động 100% DCI-P3, độ sáng cao 600 nits, hiển thị màu sắc trung thực cho Designer.',
      ctaText: 'Xem Dòng OLED',
      demand: 'design_graphics',
      image: '/images/laptop/asus-zenbook-14-oled-ux3405ma-0414777d12d4.png',
      priceTag: 'Hỗ trợ trả góp 0%',
      bgColor: 'from-slate-950 via-slate-900 to-slate-950'
    }
  ];

  const tabs = [
    { title: 'MỪNG ĐẠI TIỆC', sub: 'Chọn quà ngay' },
    { title: 'LAPTOP GAMING', sub: 'RTX 40 Series' },
    { title: 'BUILD PC GAMING', sub: 'Tặng quà 2 triệu' },
    { title: 'OLED CHUẨN MÀU', sub: 'Cân màu free' }
  ];

  // Preload all banner images into browser cache for instant slide switching
  useEffect(() => {
    slides.forEach(slide => {
      const img = new Image();
      img.src = slide.image;
      const webp = new Image();
      webp.src = slide.image.replace(/\.(png|jpg|jpeg)$/i, '.webp');
    });
  }, []);

  // Auto-rotate every 5.5 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % slides.length);
    }, 5500);
    return () => clearInterval(timer);
  }, [slides.length]);

  const active = slides[currentSlide];

  const categoryTree = [
    { label: 'Laptop, Macbook', slug: 'laptop', icon: Laptop },
    { label: 'PC, Màn hình, Máy in', slug: 'pc', icon: Monitor },
    { label: 'Linh kiện PC, Build máy', slug: 'pc-builder', icon: Wrench, isBuilder: true },
    { label: 'CPU Vi xử lý', slug: 'cpu', icon: Cpu },
    { label: 'Card đồ họa VGA', slug: 'vga', icon: Gamepad2 },
    { label: 'Bo mạch chủ & RAM', slug: 'mainboard', icon: Layers },
    { label: 'Ổ cứng SSD NVMe', slug: 'ssd', icon: HardDrive },
    { label: 'Nguồn & Vỏ Case', slug: 'case', icon: Box },
    { label: 'Thu cũ đổi mới trợ giá', slug: 'trade-in', icon: RotateCcw },
    { label: 'Khuyến mãi hot TechStore', slug: 'all', icon: Tag }
  ];

  return (
    <div className="mb-6 space-y-3">
      {/* 1. TechStore 3-Column Hero Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
        
        {/* Left Column: Vertical Category Menu (lg:col-span-3) */}
        <div className="hidden lg:block lg:col-span-3">
          <div className="bg-white dark:bg-[#151c2c] rounded-2xl border border-gray-200 dark:border-slate-800 shadow-xs p-1.5 h-full flex flex-col justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors">
            {categoryTree.map((item, idx) => {
              const ItemIcon = item.icon;
              return (
                <div
                  key={idx}
                  onClick={() => {
                    if (item.isBuilder) {
                      onNavigatePCBuilder();
                    } else if (onSelectCategory) {
                      onSelectCategory(item.slug);
                    }
                  }}
                  className="flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018] dark:hover:text-red-400 cursor-pointer transition group"
                >
                  <div className="flex items-center space-x-2.5">
                    <ItemIcon className="w-4 h-4 text-slate-500 group-hover:text-[#d70018] transition-colors flex-shrink-0" />
                    <span className="truncate">{item.label}</span>
                  </div>
                  <ChevronRightIcon className="w-3.5 h-3.5 text-slate-400 group-hover:text-[#d70018] group-hover:translate-x-0.5 transition" />
                </div>
              );
            })}
          </div>
        </div>

        {/* Center Column: Big Banner Slider with Tab Bar (lg:col-span-6) */}
        <div className="lg:col-span-6 flex flex-col">
          <div className="relative rounded-2xl overflow-hidden bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-md min-h-[300px] sm:min-h-[340px] flex items-center flex-1">
            {/* Background Image */}
            <div
              className="absolute inset-0 bg-cover bg-center transition-all duration-700 opacity-40 transform scale-105"
              style={{ backgroundImage: `url(${active.image.replace(/\.(png|jpg|jpeg)$/i, '.webp')})` }}
            />
            {/* Gradient Overlay */}
            <div className={`absolute inset-0 bg-gradient-to-r ${active.bgColor} opacity-95`} />

            {/* Slide Content */}
            <div className="relative z-10 p-6 sm:p-8 space-y-3 max-w-lg">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider ${active.badgeColor}`}>
                {active.badge}
              </span>

              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight leading-tight">
                {active.title}
              </h2>

              <p className="text-xs text-white/80 line-clamp-2 leading-relaxed">
                {active.subtitle}
              </p>

              <div className="pt-2 flex items-center space-x-3">
                {active.isBuilder ? (
                  <button
                    onClick={onNavigatePCBuilder}
                    className="px-4 py-2 bg-[#d70018] hover:bg-[#b91c1c] text-white font-bold rounded-xl text-xs flex items-center space-x-1.5 transition shadow-md active:scale-95 cursor-pointer"
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5" />
                    <span>{active.ctaText}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                ) : (
                  <button
                    onClick={() => onFilterDemand(active.demand!)}
                    className="px-4 py-2 bg-[#d70018] hover:bg-[#b91c1c] text-white font-bold rounded-xl text-xs flex items-center space-x-1.5 transition shadow-md active:scale-95 cursor-pointer"
                  >
                    <span>{active.ctaText}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}

                <div className="px-3 py-2 rounded-xl bg-white/15 backdrop-blur-sm border border-white/20 text-yellow-300 font-bold text-xs">
                  {active.priceTag}
                </div>
              </div>
            </div>

            {/* Arrow Controls */}
            <button
              onClick={() => setCurrentSlide(prev => (prev - 1 + slides.length) % slides.length)}
              className="absolute left-2 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-black/40 hover:bg-black/70 text-white/90 hover:text-white backdrop-blur-xs transition cursor-pointer"
              aria-label="Previous Slide"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentSlide(prev => (prev + 1) % slides.length)}
              className="absolute right-2 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-black/40 hover:bg-black/70 text-white/90 hover:text-white backdrop-blur-xs transition cursor-pointer"
              aria-label="Next Slide"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Bottom Tab Bar (Switches active slide on click) */}
          <div className="grid grid-cols-4 gap-1.5 mt-2 bg-white dark:bg-[#151c2c] rounded-xl p-1.5 border border-gray-200 dark:border-slate-800 shadow-xs">
            {tabs.map((tab, idx) => {
              const isActive = currentSlide === idx;
              return (
                <button
                  key={idx}
                  onClick={() => setCurrentSlide(idx)}
                  className={`py-1.5 px-2 rounded-lg text-center transition flex flex-col items-center justify-center cursor-pointer ${
                    isActive
                      ? 'bg-red-50 dark:bg-red-950/40 border-b-2 border-[#d70018] text-[#d70018] dark:text-red-400'
                      : 'hover:bg-gray-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <span className={`text-[11px] font-bold leading-tight ${isActive ? 'text-[#d70018] dark:text-red-400' : 'text-slate-800 dark:text-slate-200'}`}>
                    {tab.title}
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 font-normal truncate">
                    {tab.sub}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Column: 3 Stacked TechStore Promo Cards (lg:col-span-3) */}
        <div className="hidden lg:flex lg:col-span-3 flex-col gap-2.5">
          {/* Card 1: Thu cũ đổi mới */}
          <div className="flex-1 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-xs hover:shadow-md transition flex items-center space-x-3 group cursor-pointer">
            <div className="w-11 h-11 rounded-xl bg-red-50 dark:bg-red-950/60 text-[#d70018] dark:text-red-400 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition">
              <RotateCcw className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-1.5">
                <span className="text-[9px] font-black uppercase px-1.5 py-0.2 bg-red-100 dark:bg-red-950 text-[#d70018] dark:text-red-300 rounded">HOT</span>
                <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-[#d70018] dark:group-hover:text-red-400 transition">Thu Cũ Đổi Mới</h4>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-tight mt-0.5">Trợ giá lên đến <strong className="text-[#d70018] dark:text-red-400">4.000.000₫</strong> khi lên đời máy</p>
            </div>
          </div>

          {/* Card 2: Build PC Gaming Studio */}
          <div
            onClick={onNavigatePCBuilder}
            className="flex-1 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-2xl p-3.5 shadow-xs hover:shadow-md transition flex items-center space-x-3 group cursor-pointer"
          >
            <div className="w-11 h-11 rounded-xl bg-slate-900 text-amber-400 flex items-center justify-center flex-shrink-0 group-hover:rotate-12 transition">
              <SlidersHorizontal className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-1.5">
                <span className="text-[9px] font-black uppercase px-1.5 py-0.2 bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-200 rounded">PRO</span>
                <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-slate-700 dark:group-hover:text-slate-300 transition">Xây Dựng Cấu Hình PC</h4>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-tight mt-0.5">Tự ráp máy theo ý, tặng voucher <strong className="text-red-600 dark:text-red-400">2.500.000₫</strong></p>
            </div>
          </div>

          {/* Card 3: Ưu đãi thanh toán ngân hàng / VNPAY */}
          <div className="flex-1 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-xs hover:shadow-md transition flex items-center space-x-3 group cursor-pointer">
            <div className="w-11 h-11 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition">
              <CreditCard className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-1.5">
                <span className="text-[9px] font-black uppercase px-1.5 py-0.2 bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 rounded">VNPAY</span>
                <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-blue-700 dark:group-hover:text-blue-400 transition">Ưu Đãi Trả Góp & Thẻ</h4>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-tight mt-0.5">Giảm thêm đến <strong className="text-blue-600 dark:text-blue-400">500.000₫</strong> qua thẻ & ví trả sau</p>
            </div>
          </div>
        </div>

      </div>

      {/* 2. 5 Cam Kết Vàng Uy Tín */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 pt-1">
        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-xl p-2.5 flex items-center space-x-2.5 shadow-2xs hover:border-slate-400 dark:hover:border-slate-700 transition">
          <div className="w-8 h-8 rounded-lg bg-red-50 dark:bg-red-950/60 text-[#d70018] dark:text-red-400 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h5 className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate">100% Linh Kiện Mới</h5>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Đền 200% nếu phát hiện giả</p>
          </div>
        </div>

        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-xl p-2.5 flex items-center space-x-2.5 shadow-2xs hover:border-slate-400 dark:hover:border-slate-700 transition">
          <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center flex-shrink-0">
            <Truck className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h5 className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate">Giao Lắp Miễn Phí</h5>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Siêu tốc 2H tại HN & HCM</p>
          </div>
        </div>

        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-xl p-2.5 flex items-center space-x-2.5 shadow-2xs hover:border-slate-400 dark:hover:border-slate-700 transition">
          <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center flex-shrink-0">
            <Wrench className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h5 className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate">Bảo Trì Vệ Sinh Free</h5>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Tra keo tản nhiệt trọn đời</p>
          </div>
        </div>

        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-xl p-2.5 flex items-center space-x-2.5 shadow-2xs hover:border-slate-400 dark:hover:border-slate-700 transition">
          <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center flex-shrink-0">
            <CreditCard className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h5 className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate">Trả Góp 0% Lãi Suất</h5>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Duyệt 15P qua CCCD / Thẻ</p>
          </div>
        </div>

        <div className="col-span-2 md:col-span-1 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-xl p-2.5 flex items-center space-x-2.5 shadow-2xs hover:border-slate-400 dark:hover:border-slate-700 transition">
          <div className="w-8 h-8 rounded-lg bg-red-50 dark:bg-red-950/60 text-[#d70018] dark:text-red-400 flex items-center justify-center flex-shrink-0">
            <RotateCcw className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h5 className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate">1 Đổi 1 Trong 30 Ngày</h5>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Lỗi phần cứng đổi máy mới</p>
          </div>
        </div>
      </div>
    </div>
  );
};
