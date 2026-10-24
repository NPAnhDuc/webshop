import React, { useState } from 'react';
import {
  Gamepad2,
  Palette,
  Laptop,
  Cpu,
  Monitor,
  Sparkles,
  ArrowRight,
  SlidersHorizontal,
  Flame,
  Award,
  ShieldCheck,
  MapPin,
  PhoneCall,
  CheckCircle2,
  ExternalLink,
  Zap,
  Wrench
} from 'lucide-react';
import { Product } from '../../types';
import { ProductCard } from './ProductCard';
import { useLanguage } from '../../context/LanguageContext';

interface PCStorefrontShowcasesProps {
  products: Product[];
  onSelectProduct: (product: Product) => void;
  onNavigatePCBuilder: () => void;
  onFilterCategory: (categorySlug: string) => void;
  onFilterDemand?: (demand: string) => void;
  onAskBot?: (product: Product) => void;
  isComparing?: (product: Product) => boolean;
  onToggleCompare?: (product: Product) => void;
  onAddToCartToast?: (productName: string) => void;
}

export const PCStorefrontShowcases: React.FC<PCStorefrontShowcasesProps> = ({
  products,
  onSelectProduct,
  onNavigatePCBuilder,
  onFilterCategory,
  onFilterDemand,
  onAskBot,
  isComparing,
  onToggleCompare,
  onAddToCartToast
}) => {
  const { lang, t } = useLanguage();

  // Active tab states for each specialized block
  const [gamingTab, setGamingTab] = useState<'all' | 'under_15' | '15_to_25' | 'above_25'>('all');
  const [workstationTab, setWorkstationTab] = useState<'all' | '2d' | '3d' | 'video' | 'ai'>('all');
  const [laptopTab, setLaptopTab] = useState<'all' | 'ASUS' | 'Lenovo' | 'Apple' | 'Acer' | 'Dell'>('all');
  const [componentTab, setComponentTab] = useState<'all' | 'cpu' | 'vga' | 'mainboard' | 'ssd' | 'ram'>('all');
  const [monitorTab, setMonitorTab] = useState<'all' | 'gaming' | 'oled' | '2k'>('all');

  // Filter products for each section
  // 1. PC Gaming
  const gamingProducts = products.filter(p => {
    const isGamingCategory = p.categorySlug === 'pc' || p.categorySlug === 'laptop' || p.specs.demand?.includes('gaming');
    if (!isGamingCategory && !p.isHot) return false;
    if (gamingTab === 'under_15') return p.price < 15000000;
    if (gamingTab === '15_to_25') return p.price >= 15000000 && p.price <= 25000000;
    if (gamingTab === 'above_25') return p.price > 25000000;
    return true;
  }).slice(0, 5);

  // 2. PC Đồ Họa & Workstation AI
  const workstationProducts = products.filter(p => {
    const isDesign = p.specs.demand?.includes('design_graphics') || p.specs.demand?.includes('technical') || p.specs.panel === 'OLED' || (p.specs.cores && p.specs.cores >= 8);
    if (!isDesign && p.categorySlug !== 'cpu' && p.categorySlug !== 'vga') return false;
    if (workstationTab === '2d') return p.price <= 25000000;
    if (workstationTab === '3d') return (p.specs.vram_gb && p.specs.vram_gb >= 8) || p.price > 20000000;
    if (workstationTab === 'video') return (p.specs.storage_gb && p.specs.storage_gb >= 1000) || (p.specs.ram_gb && p.specs.ram_gb >= 16);
    if (workstationTab === 'ai') return p.price > 30000000 || p.specs.demand?.includes('technical');
    return true;
  }).slice(0, 5);

  // 3. Laptop Gaming & Đồ Họa
  const laptopProducts = products.filter(p => {
    if (p.categorySlug !== 'laptop') return false;
    if (laptopTab === 'all') return true;
    return p.brandName.toLowerCase().includes(laptopTab.toLowerCase());
  }).slice(0, 5);

  // 4. Linh Kiện Máy Tính
  const componentProducts = products.filter(p => {
    const isComp = ['cpu', 'vga', 'mainboard', 'ssd', 'ram', 'psu', 'case'].includes(p.categorySlug);
    if (!isComp) return false;
    if (componentTab === 'all') return true;
    return p.categorySlug === componentTab;
  }).slice(0, 5);

  // 5. Màn Hình
  const monitorProducts = products.filter(p => {
    if (p.categorySlug !== 'monitor') return false;
    if (monitorTab === 'gaming') return (p.specs.refresh_hz || 60) >= 144;
    if (monitorTab === 'oled') return p.specs.panel === 'OLED';
    return true;
  }).slice(0, 5);

  return (
    <div className="space-y-12">
      {/* ========================================================================= */}
      {/* SECTION 1: PC GAMING - ESPORTS CHIẾN GAME                                 */}
      {/* ========================================================================= */}
      <section id="section-pc-gaming" className="scroll-mt-24 space-y-3">
        {/* Header Bar */}
        <div className="bg-slate-900 text-white p-3.5 sm:p-4 rounded-2xl shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-[#d70018] text-white flex items-center justify-center font-black shadow-md flex-shrink-0">
              <Gamepad2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base sm:text-lg font-black tracking-tight text-white uppercase">
                  PC Gaming - Esports Chiến Game
                </h3>
                <span className="bg-red-600 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-full">
                  HOT DEALS
                </span>
              </div>
              <p className="text-[11px] text-slate-300">
                Tối ưu FPS mượt mà cho Black Myth: Wukong, CS2, Cyberpunk 2077, GTA V, Valorant
              </p>
            </div>
          </div>

          {/* Price Range Filter Tabs */}
          <div className="flex items-center space-x-1 overflow-x-auto scrollbar-none self-start md:self-auto">
            {[
              { id: 'all', label: 'Tất cả PC Gaming' },
              { id: 'under_15', label: 'Dưới 15 Triệu' },
              { id: '15_to_25', label: '15 - 25 Triệu' },
              { id: 'above_25', label: 'Trên 25 Triệu' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setGamingTab(tab.id as any)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                  gamingTab === tab.id
                    ? 'bg-[#d70018] text-white shadow-sm'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {gamingProducts.map(product => (
            <ProductCard
              key={product.id}
              product={product}
              onSelect={onSelectProduct}
              onAskBot={onAskBot}
              isComparing={isComparing ? isComparing(product) : false}
              onToggleCompare={onToggleCompare}
              onAddToCartToast={onAddToCartToast}
            />
          ))}
        </div>

        {/* Bottom Action Footer */}
        <div className="flex items-center justify-end space-x-2 pt-1">
          <button
            onClick={() => onFilterCategory('pc')}
            className="px-3.5 py-1.5 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 hover:text-[#d70018] dark:hover:text-red-400 text-slate-800 dark:text-slate-200 text-xs font-bold rounded-xl transition flex items-center space-x-1 cursor-pointer"
          >
            <span>Xem tất cả cấu hình PC Gaming</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 2: PC ĐỒ HỌA - WORKSTATION - AI RENDER                            */}
      {/* ========================================================================= */}
      <section id="section-pc-workstation" className="scroll-mt-24 space-y-3">
        {/* Header Bar */}
        <div className="bg-slate-900 text-white p-3.5 sm:p-4 rounded-2xl shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black shadow-md flex-shrink-0">
              <Palette className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base sm:text-lg font-black tracking-tight text-white uppercase">
                  PC Đồ Họa - Workstation - AI Render
                </h3>
                <span className="bg-blue-600 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-full">
                  STUDIO PRO
                </span>
              </div>
              <p className="text-[11px] text-slate-300">
                Chuyên dụng cho Premiere 4K/8K, 3ds Max, Blender, Lumion Kiến Trúc & Deep Learning AI
              </p>
            </div>
          </div>

          {/* Software Tabs */}
          <div className="flex items-center space-x-1 overflow-x-auto scrollbar-none self-start md:self-auto">
            {[
              { id: 'all', label: 'Tất cả Đồ Họa' },
              { id: '2d', label: '2D & Photoshop' },
              { id: '3d', label: '3D Max & Blender' },
              { id: 'video', label: 'Dựng Phim 4K' },
              { id: 'ai', label: 'Máy Trạm AI' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setWorkstationTab(tab.id as any)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                  workstationTab === tab.id
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Exclusive Privilege Banner */}
        <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-800 dark:text-slate-200">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <span>
              <strong>ĐẶC QUYỀN ĐỒ HỌA:</strong> Tặng gói <strong>Cân màu màn hình SpyderX Elite trọn đời</strong> + Hỗ trợ cài đặt trọn bộ Adobe 2026, AutoCAD, 3ds Max, V-Ray theo yêu cầu!
            </span>
          </div>
          <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400 whitespace-nowrap">
            Cam kết hoàn tiền 100% nếu giật lag render
          </span>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {workstationProducts.map(product => (
            <ProductCard
              key={product.id}
              product={product}
              onSelect={onSelectProduct}
              onAskBot={onAskBot}
              isComparing={isComparing ? isComparing(product) : false}
              onToggleCompare={onToggleCompare}
              onAddToCartToast={onAddToCartToast}
            />
          ))}
        </div>

        {/* Bottom Action Footer */}
        <div className="flex items-center justify-end space-x-2 pt-1">
          <button
            onClick={() => {
              if (onFilterDemand) onFilterDemand('design_graphics');
            }}
            className="px-3.5 py-1.5 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-blue-500 hover:text-blue-600 text-slate-800 dark:text-slate-200 text-xs font-bold rounded-xl transition flex items-center space-x-1 cursor-pointer"
          >
            <span>Xem tất cả cấu hình Đồ Họa & AI</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 3: LAPTOP GAMING & ĐỒ HỌA CHÍNH HÃNG                             */}
      {/* ========================================================================= */}
      <section id="section-laptops" className="scroll-mt-24 space-y-3">
        {/* Header Bar */}
        <div className="bg-slate-900 text-white p-3.5 sm:p-4 rounded-2xl shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-slate-700 text-white flex items-center justify-center font-black shadow-md flex-shrink-0">
              <Laptop className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base sm:text-lg font-black tracking-tight text-white uppercase">
                  Laptop Gaming & Đồ Họa Chính Hãng
                </h3>
                <span className="bg-blue-600 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-full">
                  TRẢ GÓP 0%
                </span>
              </div>
              <p className="text-[11px] text-slate-300">
                Phân phối chính hãng ASUS ROG, Lenovo Legion, Acer Predator, Dell XPS, MSI, Apple MacBook
              </p>
            </div>
          </div>

          {/* Brand Tabs */}
          <div className="flex items-center space-x-1 overflow-x-auto scrollbar-none self-start md:self-auto">
            {['all', 'ASUS', 'Lenovo', 'Apple', 'Acer', 'Dell'].map(brand => (
              <button
                key={brand}
                onClick={() => setLaptopTab(brand as any)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                  laptopTab === brand
                    ? 'bg-[#d70018] text-white shadow-sm'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {brand === 'all' ? 'Tất cả hãng' : brand}
              </button>
            ))}
          </div>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {laptopProducts.map(product => (
            <ProductCard
              key={product.id}
              product={product}
              onSelect={onSelectProduct}
              onAskBot={onAskBot}
              isComparing={isComparing ? isComparing(product) : false}
              onToggleCompare={onToggleCompare}
              onAddToCartToast={onAddToCartToast}
            />
          ))}
        </div>

        {/* Bottom Action Footer */}
        <div className="flex items-center justify-end space-x-2 pt-1">
          <button
            onClick={() => onFilterCategory('laptop')}
            className="px-3.5 py-1.5 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 hover:text-[#d70018] text-slate-800 dark:text-slate-200 text-xs font-bold rounded-xl transition flex items-center space-x-1 cursor-pointer"
          >
            <span>Xem toàn bộ Laptop chính hãng</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 4: LINH KIỆN MÁY TÍNH - NÂNG CẤP BUILD DÀN PC                      */}
      {/* ========================================================================= */}
      <section id="section-pc-components" className="scroll-mt-24 space-y-3">
        {/* Header Bar */}
        <div className="bg-slate-900 text-white p-3.5 sm:p-4 rounded-2xl shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-[#d70018] text-white flex items-center justify-center font-black shadow-md flex-shrink-0">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base sm:text-lg font-black tracking-tight text-white uppercase">
                  Linh Kiện Máy Tính - Nâng Cấp Build Dàn Máy
                </h3>
                <span className="bg-slate-800 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-full border border-slate-700">
                  GENUINE 100%
                </span>
              </div>
              <p className="text-[11px] text-slate-300">
                CPU Intel & AMD, Card VGA Nvidia, Bo Mạch Chủ B760/Z790, RAM DDR5, Ổ Cứng NVMe PCIe 4.0
              </p>
            </div>
          </div>

          {/* Component Category Tabs */}
          <div className="flex items-center space-x-1 overflow-x-auto scrollbar-none self-start md:self-auto">
            {[
              { id: 'all', label: 'Tất cả linh kiện' },
              { id: 'cpu', label: 'CPU Vi Xử Lý' },
              { id: 'vga', label: 'Card VGA' },
              { id: 'mainboard', label: 'Bo Mạch Main' },
              { id: 'ssd', label: 'Ổ Cứng SSD' },
              { id: 'ram', label: 'RAM DDR5' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setComponentTab(tab.id as any)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                  componentTab === tab.id
                    ? 'bg-[#d70018] text-white shadow-sm'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Big Interactive Callout Banner */}
        <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold flex-shrink-0 shadow-sm">
              <Wrench className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-black text-slate-900 dark:text-slate-100">
                Chưa biết chọn linh kiện nào tương thích với dàn máy?
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Công cụ Build PC của TechStore sẽ tự động đối chiếu Socket CPU, kích thước VGA và tính tổng nguồn điện Wattage cần thiết!
              </p>
            </div>
          </div>

          <button
            onClick={onNavigatePCBuilder}
            className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-black rounded-xl transition flex items-center justify-center space-x-1.5 shadow-md flex-shrink-0 cursor-pointer active:scale-95"
          >
            <SlidersHorizontal className="w-4 h-4 text-amber-400" />
            <span>Mở Trình Xây Dựng Cấu Hình Ngay</span>
          </button>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {componentProducts.map(product => (
            <ProductCard
              key={product.id}
              product={product}
              onSelect={onSelectProduct}
              onAskBot={onAskBot}
              isComparing={isComparing ? isComparing(product) : false}
              onToggleCompare={onToggleCompare}
              onAddToCartToast={onAddToCartToast}
            />
          ))}
        </div>

        {/* Bottom Action Footer */}
        <div className="flex items-center justify-end space-x-2 pt-1">
          <button
            onClick={() => onFilterCategory('cpu')}
            className="px-3.5 py-1.5 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 hover:text-[#d70018] text-slate-800 dark:text-slate-200 text-xs font-bold rounded-xl transition flex items-center space-x-1 cursor-pointer"
          >
            <span>Xem kho linh kiện rời</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 5: MÀN HÌNH MÁY TÍNH CHUYÊN NGHIỆP                                */}
      {/* ========================================================================= */}
      {monitorProducts.length > 0 && (
        <section id="section-monitors" className="scroll-mt-24 space-y-3">
          {/* Header Bar */}
          <div className="bg-slate-900 text-white p-3.5 sm:p-4 rounded-2xl shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center font-black shadow-md flex-shrink-0">
                <Monitor className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="text-base sm:text-lg font-black tracking-tight text-white uppercase">
                    Màn Hình Máy Tính Đồ Họa & Gaming
                  </h3>
                  <span className="bg-purple-600 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-full">
                    OLED / 240HZ
                  </span>
                </div>
                <p className="text-[11px] text-slate-300">
                  Tần số quét cao 144Hz - 240Hz, Tấm nền Fast-IPS & OLED chuẩn màu 100% sRGB / DCI-P3
                </p>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center space-x-1 overflow-x-auto scrollbar-none self-start md:self-auto">
              {[
                { id: 'all', label: 'Tất cả Màn Hình' },
                { id: 'gaming', label: 'Gaming 144Hz+' },
                { id: 'oled', label: 'Chuẩn Màu OLED' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setMonitorTab(tab.id as any)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                    monitorTab === tab.id
                      ? 'bg-purple-600 text-white shadow-sm'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
            {monitorProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onSelect={onSelectProduct}
                onAskBot={onAskBot}
                isComparing={isComparing ? isComparing(product) : false}
                onToggleCompare={onToggleCompare}
                onAddToCartToast={onAddToCartToast}
              />
            ))}
          </div>
        </section>
      )}

      {/* ========================================================================= */}
      {/* SECTION 6: HỆ THỐNG SHOWROOM & ĐỐI TÁC CÔNG NGHỆ                          */}
      {/* ========================================================================= */}
      <section id="section-showrooms" className="scroll-mt-24 space-y-4 pt-4 border-t border-gray-200 dark:border-slate-800">
        {/* Brand Partners Showcase */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 dark:text-slate-400">
              ĐỐI TÁC THƯƠNG HIỆU PHẦN CỨNG CHIẾN LƯỢC TOÀN CẦU
            </h4>
            <span className="text-[11px] text-[#d70018] dark:text-red-400 font-bold">
              Ủy quyền chính thức 100%
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
            {[
              { name: 'INTEL', title: 'Titanium Partner' },
              { name: 'NVIDIA', title: 'Authorized' },
              { name: 'ASUS ROG', title: 'Official Club' },
              { name: 'MSI', title: 'Gaming Certified' },
              { name: 'GIGABYTE', title: 'AORUS Elite' },
              { name: 'KINGSTON', title: 'Premier Partner' },
              { name: 'CORSAIR', title: 'Authorized' },
              { name: 'SAMSUNG', title: 'V-NAND Partner' }
            ].map((p, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-xl p-2.5 text-center shadow-2xs hover:border-[#d70018] dark:hover:border-red-500 transition group cursor-pointer"
              >
                <div className="font-black text-xs text-slate-800 dark:text-slate-100 group-hover:text-[#d70018] dark:group-hover:text-red-400 tracking-wider">
                  {p.name}
                </div>
                <div className="text-[9px] text-slate-500 dark:text-slate-400 font-semibold mt-0.5">
                  {p.title}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4 Flagship Showrooms */}
        <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-gray-150 dark:border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-[#d70018] dark:text-red-400" />
              <h4 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase">
                HỆ THỐNG SHOWROOM TRẢI NGHIỆM THỰC TẾ
              </h4>
            </div>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              Mở cửa từ <strong>8h00 - 21h30</strong> tất cả các ngày trong tuần
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-150 dark:border-slate-700/60 space-y-1">
              <div className="font-bold text-[#d70018] dark:text-red-400 flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                <span>Showroom 1 (Thái Hà - HN)</span>
              </div>
              <p className="text-slate-700 dark:text-slate-300">Số 377-379 Thái Hà, Q. Đống Đa, Hà Nội</p>
              <p className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">Hotline: 097.111.3323</p>
            </div>

            <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-150 dark:border-slate-700/60 space-y-1">
              <div className="font-bold text-[#d70018] dark:text-red-400 flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                <span>Showroom 2 (Lê Thanh Nghị - HN)</span>
              </div>
              <p className="text-slate-700 dark:text-slate-300">Số 131 Lê Thanh Nghị, Q. Hai Bà Trưng, Hà Nội</p>
              <p className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">Hotline: 098.333.6623</p>
            </div>

            <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-150 dark:border-slate-700/60 space-y-1">
              <div className="font-bold text-blue-600 dark:text-blue-400 flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                <span>Showroom 3 (Lý Thường Kiệt - HCM)</span>
              </div>
              <p className="text-slate-700 dark:text-slate-300">Số 249 Lý Thường Kiệt, P.15, Q.10, TP.HCM</p>
              <p className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">Hotline: 090.888.6623</p>
            </div>

            <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-150 dark:border-slate-700/60 space-y-1">
              <div className="font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                <span>Showroom 4 (Nguyễn Văn Linh - ĐN)</span>
              </div>
              <p className="text-slate-700 dark:text-slate-300">Số 83-85 Nguyễn Văn Linh, Q. Hải Châu, Đà Nẵng</p>
              <p className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">Hotline: 091.777.9923</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
