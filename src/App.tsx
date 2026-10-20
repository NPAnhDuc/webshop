import React, { useState, useEffect } from 'react';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { ProductCard } from './components/storefront/ProductCard';
import { ProductFilters } from './components/storefront/ProductFilters';
import { FlashSaleBanner } from './components/storefront/FlashSaleBanner';
import { HeroBannerCarousel } from './components/storefront/HeroBannerCarousel';
import { PCStorefrontShowcases } from './components/storefront/PCStorefrontShowcases';
import { ComparisonBar } from './components/storefront/ComparisonBar';
import { ComparisonModal } from './components/storefront/ComparisonModal';
import { ToastContainer, ToastMessage } from './components/common/Toast';
import { ProductDetailModal } from './components/storefront/ProductDetailModal';
import { CartDrawer } from './components/storefront/CartDrawer';
import { CheckoutModal } from './components/common/CheckoutModal';
import { OrderLookupModal } from './components/common/OrderLookupModal';
import { CustomerChatWidget } from './components/chatbot/CustomerChatWidget';
import { PCBuilderView } from './components/pc-builder/PCBuilderView';

import { AdminLayout, AdminTabType } from './components/admin/AdminLayout';
import { DashboardView } from './components/admin/DashboardView';
import { InventoryManagement } from './components/admin/InventoryManagement';
import { OrderManagement } from './components/admin/OrderManagement';
import { DocumentManagement } from './components/admin/DocumentManagement';
import { AdminChatbotView } from './components/admin/AdminChatbotView';
import { ProductManagement } from './components/admin/ProductManagement';
import { PromotionManagement } from './components/admin/PromotionManagement';
import { CustomerManagement } from './components/admin/CustomerManagement';
import { QuotationManagement } from './components/admin/QuotationManagement';
import { ReviewManagement } from './components/admin/ReviewManagement';
import { StoreSettingsManagement } from './components/admin/StoreSettingsManagement';

import { CartProvider } from './context/CartContext';
import { WishlistProvider, useWishlist } from './context/WishlistContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import { SideWings } from './components/common/SideWings';
import { fetchProducts } from './services/api';
import { Product } from './types';
import {
  Sparkles,
  SlidersHorizontal,
  Flame,
  Laptop,
  CheckCircle2,
  Lock,
  ArrowRight,
  ShieldCheck,
  Zap,
  RotateCcw,
  Award,
  Activity,
  Wrench,
  CreditCard
} from 'lucide-react';

const AppContent: React.FC = () => {
  const { isAuthenticated, login } = useAuth();
  const { t, lang } = useLanguage();

  // Navigation Views: 'storefront' | 'pc-builder' | 'admin'
  const [currentView, setCurrentView] = useState<'storefront' | 'pc-builder' | 'admin'>('storefront');
  const [adminTab, setAdminTab] = useState<AdminTabType>('dashboard');

  // Storefront Product State
  const [products, setProducts] = useState<Product[]>([]);
  const [facets, setFacets] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [totalProducts, setTotalProducts] = useState(0);

  // Filters State
  const [currentCategory, setCurrentCategory] = useState<string>('all');
  const [selectedBrand, setSelectedBrand] = useState<string | undefined>();
  const [selectedPriceRange, setSelectedPriceRange] = useState<string | undefined>();
  const [selectedDemand, setSelectedDemand] = useState<string | undefined>();
  const [selectedPanel, setSelectedPanel] = useState<string | undefined>();
  const [inStockOnly, setInStockOnly] = useState(false);
  const [hasInstallment0, setHasInstallment0] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'featured' | 'price_asc' | 'price_desc' | 'newest' | 'discount_desc'>('featured');
  const { wishlistIds } = useWishlist();
  const [wishlistFilterOnly, setWishlistFilterOnly] = useState(false);

  // Comparison State (W-06)
  const [comparingProducts, setComparingProducts] = useState<Product[]>([]);
  const [showComparisonModal, setShowComparisonModal] = useState(false);

  // Toast Notification System
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Modals & Selected states
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [showOrderLookup, setShowOrderLookup] = useState(false);
  const [successOrderCode, setSuccessOrderCode] = useState<string | null>(null);

  // Admin login modal state
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [loginUsername, setLoginUsername] = useState('admin');
  const [loginPassword, setLoginPassword] = useState('admin123');
  const [loginError, setLoginError] = useState('');

  const addToast = (title: string, message?: string, type: 'success' | 'warning' | 'info' = 'success') => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    setToasts(prev => [...prev, { id, title, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3500);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Fetch Products with active filters
  const loadProducts = () => {
    setLoading(true);

    let minPrice: number | undefined;
    let maxPrice: number | undefined;

    if (selectedPriceRange === 'under15m') maxPrice = 15000000;
    else if (selectedPriceRange === 'from15to20m') { minPrice = 15000000; maxPrice = 20000000; }
    else if (selectedPriceRange === 'from20to30m') { minPrice = 20000000; maxPrice = 30000000; }
    else if (selectedPriceRange === 'above30m') minPrice = 30000000;

    fetchProducts({
      category: currentCategory,
      brand: selectedBrand,
      minPrice,
      maxPrice,
      demand: selectedDemand,
      panel: selectedPanel,
      inStockOnly,
      hasInstallment0,
      q: searchQuery,
      sort: sortBy,
      limit: 24
    })
      .then(res => {
        setProducts(res.products || []);
        setFacets(res.facets || {});
        setTotalProducts(res.total || 0);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (currentView === 'storefront') {
      loadProducts();
    }
  }, [
    currentCategory,
    selectedBrand,
    selectedPriceRange,
    selectedDemand,
    selectedPanel,
    inStockOnly,
    hasInstallment0,
    searchQuery,
    sortBy,
    currentView
  ]);

  const handleResetFilters = () => {
    setSelectedBrand(undefined);
    setSelectedPriceRange(undefined);
    setSelectedDemand(undefined);
    setSelectedPanel(undefined);
    setInStockOnly(false);
    setHasInstallment0(false);
    setSearchQuery('');
    setSortBy('featured');
    setCurrentCategory('all');
  };

  const handleToggleCompare = (product: Product) => {
    setComparingProducts(prev => {
      const exists = prev.some(p => p.id === product.id);
      if (exists) {
        return prev.filter(p => p.id !== product.id);
      } else {
        if (prev.length >= 3) {
          addToast('Chỉ so sánh tối đa 3 máy', 'Vui lòng bỏ bớt 1 máy để chọn máy mới', 'warning');
          return prev;
        }
        addToast('Đã thêm vào danh sách so sánh', product.name, 'info');
        return [...prev, product];
      }
    });
  };

  const handleAdminClick = () => {
    if (!isAuthenticated) {
      setShowAdminLogin(true);
    } else {
      setCurrentView('admin');
    }
  };

  const handleAdminLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginUsername === 'admin' && (loginPassword === 'admin123' || loginPassword === 'admin')) {
      login('jwt-mock-owner', {
        id: 'usr-1',
        name: 'Chị Lan (Chủ Shop)',
        role: 'owner',
        email: 'lan.techstore@gmail.com'
      });
      setShowAdminLogin(false);
      setCurrentView('admin');
      addToast('Đăng nhập quản trị thành công', 'Chào mừng Chị Lan (Chủ shop)', 'success');
    } else if (loginUsername === 'kho' && loginPassword === 'kho123') {
      login('jwt-mock-wh', {
        id: 'usr-2',
        name: 'Anh Tuấn (Nhân Viên Kho)',
        role: 'warehouse',
        email: 'tuan.kho@techstore.vn'
      });
      setShowAdminLogin(false);
      setCurrentView('admin');
      addToast('Đăng nhập thủ kho thành công', 'Chào mừng Anh Tuấn (Kho)', 'success');
    } else {
      setLoginError('Tên đăng nhập hoặc mật khẩu không đúng (Gợi ý: admin / admin123)');
    }
  };

  // Render Admin View
  if (currentView === 'admin' && isAuthenticated) {
    return (
      <AdminLayout
        currentTab={adminTab}
        onSelectTab={setAdminTab}
        onBackToStorefront={() => setCurrentView('storefront')}
      >
        {adminTab === 'dashboard' && <DashboardView onNavigateToChatbot={() => setAdminTab('chatbot')} />}
        {adminTab === 'products' && <ProductManagement />}
        {adminTab === 'inventory' && <InventoryManagement />}
        {adminTab === 'orders' && <OrderManagement />}
        {adminTab === 'promotions' && <PromotionManagement />}
        {adminTab === 'quotations' && <QuotationManagement />}
        {adminTab === 'customers' && <CustomerManagement />}
        {adminTab === 'reviews' && <ReviewManagement />}
        {adminTab === 'documents' && <DocumentManagement />}
        {adminTab === 'chatbot' && <AdminChatbotView />}
        {adminTab === 'settings' && <StoreSettingsManagement />}
      </AdminLayout>
    );
  }

  // Render PC Builder View
  if (currentView === 'pc-builder') {
    return (
      <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 flex flex-col justify-between selection:bg-emerald-600 selection:text-white transition-colors duration-200">
        <Navbar
          onSearch={q => {
            setSearchQuery(q);
            setCurrentView('storefront');
          }}
          onOpenLookup={() => setShowOrderLookup(true)}
          onNavigatePCBuilder={() => setCurrentView('pc-builder')}
          onNavigateAdmin={handleAdminClick}
          onNavigateHome={() => setCurrentView('storefront')}
          onSelectCategory={cat => {
            setCurrentCategory(cat);
            setCurrentView('storefront');
          }}
          currentCategory={currentCategory}
          onToggleWishlistFilter={() => {
            setWishlistFilterOnly(prev => !prev);
            setCurrentView('storefront');
          }}
          isWishlistFilterActive={wishlistFilterOnly}
        />
        <PCBuilderView
          onBackToHome={() => setCurrentView('storefront')}
          onSelectProduct={prod => setSelectedProduct(prod)}
          onToast={(title, msg) => addToast(title, msg, 'success')}
        />
        <Footer />
        <CartDrawer onProceedToCheckout={() => setShowCheckout(true)} />
        <CheckoutModal
          isOpen={showCheckout}
          onClose={() => setShowCheckout(false)}
          onOrderSuccess={code => {
            setSuccessOrderCode(code);
            addToast('Đặt hàng thành công!', `Mã đơn: ${code}`, 'success');
          }}
        />
        <ToastContainer toasts={toasts} onDismiss={removeToast} />
      </div>
    );
  }

  // Render Main Storefront View
  return (
    <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 flex flex-col justify-between selection:bg-emerald-600 selection:text-white relative transition-colors duration-200">
      {/* Interactive Side Wings for Wide Screens */}
      <SideWings
        onNavigatePCBuilder={() => setCurrentView('pc-builder')}
        onOpenLookup={() => setShowOrderLookup(true)}
      />

      {/* 1. Header Navigation */}
      <Navbar
        onSearch={q => setSearchQuery(q)}
        onOpenLookup={() => setShowOrderLookup(true)}
        onNavigatePCBuilder={() => setCurrentView('pc-builder')}
        onNavigateAdmin={handleAdminClick}
        onNavigateHome={() => {
          handleResetFilters();
          setCurrentView('storefront');
        }}
        onSelectCategory={cat => setCurrentCategory(cat)}
        currentCategory={currentCategory}
        onToggleWishlistFilter={() => setWishlistFilterOnly(prev => !prev)}
        isWishlistFilterActive={wishlistFilterOnly}
      />

      {/* Main Container */}
      <main className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 sm:px-6 py-5 w-full flex-1">
        {/* Order Placed Success Banner */}
        {successOrderCode && (
          <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 rounded-2xl flex items-center justify-between text-xs text-emerald-900 dark:text-emerald-200 shadow-xs animate-in fade-in">
            <div className="flex items-center space-x-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
              <div>
                <p className="font-bold text-sm">
                  {lang === 'vi' ? 'Đặt hàng thành công! Mã đơn: ' : 'Order placed successfully! Order Code: '}
                  <span className="font-mono">{successOrderCode}</span>
                </p>
                <p className="text-emerald-700 dark:text-emerald-300">
                  {lang === 'vi'
                    ? 'Đơn hàng đã được lưu & giữ hàng trong kho. Chuyên viên TechStore sẽ gọi xác nhận trong 15 phút.'
                    : 'Your order is confirmed & reserved. A TechStore specialist will contact you within 15 minutes.'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setSuccessOrderCode(null)}
              className="text-emerald-700 dark:text-emerald-300 hover:text-emerald-900 dark:hover:text-emerald-100 font-bold px-2 py-1 cursor-pointer"
            >
              {lang === 'vi' ? 'Đóng ×' : 'Close ×'}
            </button>
          </div>
        )}

        {/* Hero Banner Luxury Carousel (TechStore 3-Column Hero Layout) */}
        {!searchQuery && currentCategory === 'all' && (
          <HeroBannerCarousel
            onNavigatePCBuilder={() => setCurrentView('pc-builder')}
            onFilterDemand={demand => setSelectedDemand(demand)}
            onSelectCategory={cat => setCurrentCategory(cat)}
          />
        )}

        {/* Flash Sale Banner with Live Timer (TechStore Hot Sale Cuối Tuần) */}
        {!searchQuery && currentCategory === 'all' && (
          <FlashSaleBanner
            products={products}
            onSelectProduct={prod => setSelectedProduct(prod)}
            onAskBot={prod => setSelectedProduct(prod || null)}
          />
        )}

        {/* CellphoneS-Style High-Conversion Quick Service & Event Bar */}
        {!searchQuery && currentCategory === 'all' && (
          <div className="mb-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
            <button
              onClick={() => setCurrentView('pc-builder')}
              className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-[#059669] dark:hover:border-emerald-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-lg bg-yellow-400 text-slate-950 flex items-center justify-center font-bold flex-shrink-0 group-hover:scale-110 transition">
                <SlidersHorizontal className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#059669] dark:group-hover:text-emerald-400">Tự Ráp PC</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Quà tặng 2 triệu</span>
              </div>
            </button>

            <button
              onClick={() => {
                setSelectedDemand('gaming');
                document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-[#059669] dark:hover:border-emerald-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-lg bg-rose-500 text-white flex items-center justify-center font-bold flex-shrink-0 group-hover:scale-110 transition">
                <Flame className="w-4 h-4 fill-white" />
              </div>
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#059669] dark:group-hover:text-emerald-400">Laptop Gaming</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">RTX 40 Series</span>
              </div>
            </button>

            <button
              onClick={() => {
                setHasInstallment0(true);
                document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-[#059669] dark:hover:border-emerald-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold flex-shrink-0 group-hover:scale-110 transition">
                <CreditCard className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#059669] dark:group-hover:text-emerald-400">Trả Góp 0%</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Duyệt nhanh 15P</span>
              </div>
            </button>

            <button
              onClick={() => {
                setSelectedDemand('thin_light');
                document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-[#059669] dark:hover:border-emerald-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold flex-shrink-0 group-hover:scale-110 transition">
                <Award className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#059669] dark:group-hover:text-emerald-400">Sinh Viên Giảm 500k</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Ưu đãi T-Student</span>
              </div>
            </button>

            <button
              onClick={() => {
                setSelectedPanel('OLED');
                document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-[#059669] dark:hover:border-emerald-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-lg bg-purple-600 text-white flex items-center justify-center font-bold flex-shrink-0 group-hover:scale-110 transition">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#059669] dark:group-hover:text-emerald-400">Màn Hình OLED</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Chuẩn màu 100% P3</span>
              </div>
            </button>

            <button
              onClick={handleResetFilters}
              className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-[#059669] dark:hover:border-emerald-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-lg bg-teal-600 text-white flex items-center justify-center font-bold flex-shrink-0 group-hover:scale-110 transition">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#059669] dark:group-hover:text-emerald-400">1 Đổi 1 30 Ngày</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Chính hãng 100%</span>
              </div>
            </button>
          </div>
        )}

        {/* Nguyễn Công PC & HACOM Signature Industry Showcases */}
        {!searchQuery && currentCategory === 'all' && !selectedBrand && !selectedPriceRange && !selectedDemand && !selectedPanel && !hasInstallment0 && !inStockOnly && !wishlistFilterOnly && (
          <div className="mb-10">
            <PCStorefrontShowcases
              products={products}
              onSelectProduct={prod => setSelectedProduct(prod)}
              onNavigatePCBuilder={() => setCurrentView('pc-builder')}
              onFilterCategory={cat => {
                setCurrentCategory(cat);
                document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              onFilterDemand={dem => {
                setSelectedDemand(dem);
                document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              onAskBot={prod => setSelectedProduct(prod)}
              isComparing={prod => comparingProducts.some(p => p.id === prod.id)}
              onToggleCompare={handleToggleCompare}
              onAddToCartToast={name => addToast(lang === 'vi' ? 'Đã thêm vào giỏ hàng' : 'Added to cart', name, 'success')}
            />
          </div>
        )}

        {/* Catalog Section with Sidebar Filters & Product Grid */}
        <div id="product-catalog-section" className="scroll-mt-24 pt-4 border-t border-gray-200 dark:border-slate-800">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold shadow-xs">
                <SlidersHorizontal className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-black uppercase text-slate-900 dark:text-slate-100">
                  {currentCategory !== 'all' ? `DANH MỤC: ${currentCategory.toUpperCase()}` : 'TOÀN BỘ KHO SẢN PHẨM & BỘ LỌC ĐA CHIỀU'}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Tùy chọn lọc thông số chi tiết theo tiêu chuẩn Showroom Máy tính chuyên nghiệp
                </p>
              </div>
            </div>
            {(selectedBrand || selectedPriceRange || selectedDemand || selectedPanel || inStockOnly || hasInstallment0) && (
              <button
                onClick={handleResetFilters}
                className="text-xs text-red-500 hover:underline font-bold cursor-pointer"
              >
                Xóa tất cả bộ lọc ×
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar Filter */}
          <div className="lg:col-span-1">
            <div className="sticky top-20">
              <ProductFilters
                facets={facets}
                selectedBrand={selectedBrand}
                selectedPriceRange={selectedPriceRange}
                selectedDemand={selectedDemand}
                selectedPanel={selectedPanel}
                inStockOnly={inStockOnly}
                hasInstallment0={hasInstallment0}
                onFilterChange={newFilters => {
                  if (newFilters.brand !== undefined) setSelectedBrand(newFilters.brand);
                  if (newFilters.priceRange !== undefined) setSelectedPriceRange(newFilters.priceRange);
                  if (newFilters.demand !== undefined) setSelectedDemand(newFilters.demand);
                  if (newFilters.panel !== undefined) setSelectedPanel(newFilters.panel);
                  if (newFilters.inStockOnly !== undefined) setInStockOnly(newFilters.inStockOnly);
                  if (newFilters.hasInstallment0 !== undefined) setHasInstallment0(newFilters.hasInstallment0);
                }}
                onReset={handleResetFilters}
              />
            </div>
          </div>

          {/* Right Column: Sorting Bar & Product Cards */}
          <div className="lg:col-span-3 space-y-3.5">
            {/* CellphoneS-style Quick Brand & Price Pills */}
            <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-3 shadow-2xs space-y-2">
              <div className="flex items-center space-x-1.5 overflow-x-auto scrollbar-none">
                <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 whitespace-nowrap mr-1">Thương hiệu:</span>
                {['ASUS', 'Lenovo', 'Apple', 'Dell', 'Acer', 'MSI', 'HP'].map(brand => (
                  <button
                    key={brand}
                    onClick={() => setSelectedBrand(selectedBrand === brand ? undefined : brand)}
                    className={`px-3 py-1 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer border ${
                      selectedBrand === brand
                        ? 'bg-[#059669] text-white border-[#059669] shadow-xs'
                        : 'bg-gray-50 dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 border-gray-200 dark:border-slate-700 hover:border-emerald-400'
                    }`}
                  >
                    {brand}
                  </button>
                ))}
                {selectedBrand && (
                  <button
                    onClick={() => setSelectedBrand(undefined)}
                    className="px-2 py-0.5 text-xs text-red-500 hover:underline font-bold whitespace-nowrap"
                  >
                    Xóa lọc
                  </button>
                )}
              </div>

              <div className="flex items-center space-x-1.5 overflow-x-auto scrollbar-none pt-1 border-t border-gray-100 dark:border-slate-800">
                <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 whitespace-nowrap mr-1">Mức giá:</span>
                {[
                  { label: 'Dưới 15 triệu', val: 'under_15' },
                  { label: '15 - 20 triệu', val: '15_to_20' },
                  { label: '20 - 30 triệu', val: '20_to_30' },
                  { label: 'Trên 30 triệu', val: 'above_30' }
                ].map(pr => (
                  <button
                    key={pr.val}
                    onClick={() => setSelectedPriceRange(selectedPriceRange === pr.val ? undefined : pr.val)}
                    className={`px-3 py-1 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer border ${
                      selectedPriceRange === pr.val
                        ? 'bg-[#059669] text-white border-[#059669] shadow-xs'
                        : 'bg-gray-50 dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 border-gray-200 dark:border-slate-700 hover:border-emerald-400'
                    }`}
                  >
                    {pr.label}
                  </button>
                ))}
                {selectedPriceRange && (
                  <button
                    onClick={() => setSelectedPriceRange(undefined)}
                    className="px-2 py-0.5 text-xs text-red-500 hover:underline font-bold whitespace-nowrap"
                  >
                    Xóa lọc
                  </button>
                )}
              </div>
            </div>

            {/* Sorting Toolbar */}
            <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-3.5 sm:p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-xs text-slate-700 dark:text-slate-300 transition-colors">
              <div className="text-slate-600 dark:text-slate-300">
                {wishlistFilterOnly ? (
                  <span className="font-bold text-rose-500 flex items-center space-x-1.5">
                    <span>❤️ {lang === 'vi' ? 'Danh sách sản phẩm Yêu thích' : 'Wishlist Products'}</span>
                    <span className="text-xs text-slate-500 font-normal">
                      ({products.filter(p => wishlistIds.includes(p.id)).length} {lang === 'vi' ? 'sản phẩm' : 'items'})
                    </span>
                  </span>
                ) : (
                  <>
                    {t('found')} <strong className="text-[#059669] dark:text-emerald-400 font-bold">{totalProducts}</strong> {t('productsMatch')}
                    {searchQuery && <span> {t('forKeyword')} "<span className="text-[#059669] dark:text-emerald-400 font-bold">{searchQuery}</span>"</span>}
                  </>
                )}
              </div>

              {/* Sort Options */}
              <div className="flex items-center space-x-2">
                <span className="text-slate-500 dark:text-slate-400 font-medium">{t('sort')}</span>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as any)}
                  className="px-3 py-1.5 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-semibold focus:outline-none focus:border-[#059669] text-xs cursor-pointer"
                >
                  <option value="featured">{t('sortFeatured')}</option>
                  <option value="price_asc">{t('sortPriceAsc')}</option>
                  <option value="price_desc">{t('sortPriceDesc')}</option>
                  <option value="discount_desc">{t('sortDiscountDesc')}</option>
                  <option value="newest">{t('sortNewest')}</option>
                </select>
              </div>
            </div>

            {/* Product Grid */}
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                {[1, 2, 3, 4, 5, 6].map(n => (
                  <div key={n} className="bg-white dark:bg-[#151c2c] rounded-2xl border border-gray-200 dark:border-slate-800 p-4 h-80 animate-pulse space-y-4 shadow-xs">
                    <div className="bg-gray-100 dark:bg-slate-800 aspect-square rounded-xl" />
                    <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-3/4" />
                    <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : (wishlistFilterOnly ? products.filter(p => wishlistIds.includes(p.id)) : products).length === 0 ? (
              <div className="bg-white dark:bg-[#151c2c] rounded-3xl border border-gray-200 dark:border-slate-800 p-12 text-center space-y-3 shadow-xs text-slate-800 dark:text-slate-200">
                <div className="w-12 h-12 bg-gray-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto text-slate-400">
                  <Laptop className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                  {wishlistFilterOnly
                    ? (lang === 'vi' ? 'Chưa có sản phẩm yêu thích nào' : 'No wishlisted products yet')
                    : t('noProductFound')}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {wishlistFilterOnly
                    ? (lang === 'vi' ? 'Hãy bấm icon trái tim ❤️ trên sản phẩm để lưu lại xem sau!' : 'Click the heart ❤️ icon on any product to save it here!')
                    : t('noProductFoundSub')}
                </p>
                <button
                  onClick={() => {
                    if (wishlistFilterOnly) {
                      setWishlistFilterOnly(false);
                    } else {
                      handleResetFilters();
                    }
                  }}
                  className="mt-2 px-5 py-2.5 bg-[#059669] text-white rounded-xl text-xs font-bold hover:bg-[#047857] transition shadow-xs cursor-pointer"
                >
                  {wishlistFilterOnly ? (lang === 'vi' ? 'Xem tất cả sản phẩm' : 'View all products') : t('clearFilters')}
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                {(wishlistFilterOnly ? products.filter(p => wishlistIds.includes(p.id)) : products).map(prod => (
                  <ProductCard
                    key={prod.id}
                    product={prod}
                    onSelect={p => setSelectedProduct(p)}
                    onAskBot={p => setSelectedProduct(p)}
                    isComparing={comparingProducts.some(p => p.id === prod.id)}
                    onToggleCompare={handleToggleCompare}
                    onAddToCartToast={name => addToast('Đã thêm vào giỏ hàng', name, 'success')}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      </main>

      {/* Floating Comparison Bar (when items are selected for comparison) */}
      <ComparisonBar
        products={comparingProducts}
        onRemove={id => setComparingProducts(prev => prev.filter(p => p.id !== id))}
        onClear={() => setComparingProducts([])}
        onOpenModal={() => setShowComparisonModal(true)}
      />

      {/* Side-by-Side Comparison Matrix Modal */}
      <ComparisonModal
        products={comparingProducts}
        isOpen={showComparisonModal}
        onClose={() => setShowComparisonModal(false)}
        onAskBotCompare={prods => {
          setShowComparisonModal(false);
          setSelectedProduct(prods[0]);
          addToast('Đang mở trợ lý AI để phân tích khác biệt...', prods.map(p => p.name).join(' vs '), 'info');
        }}
      />

      {/* Footer */}
      <Footer />

      {/* Floating Customer AI Chatbot */}
      <CustomerChatWidget
        currentProduct={selectedProduct}
        onSelectProduct={p => setSelectedProduct(p)}
      />

      {/* Cart Drawer */}
      <CartDrawer onProceedToCheckout={() => setShowCheckout(true)} />

      {/* Product Detail Modal */}
      <ProductDetailModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAskBot={prod => {
          setSelectedProduct(prod);
        }}
      />

      {/* Checkout Modal */}
      <CheckoutModal
        isOpen={showCheckout}
        onClose={() => setShowCheckout(false)}
        onOrderSuccess={code => {
          setSuccessOrderCode(code);
          addToast('Đặt hàng thành công!', `Mã đơn hàng: ${code}`, 'success');
        }}
      />

      {/* Order Lookup Modal */}
      <OrderLookupModal
        isOpen={showOrderLookup}
        onClose={() => setShowOrderLookup(false)}
      />

      {/* Toast Notification Container */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Admin Login Modal */}
      {showAdminLogin && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Lock className="w-4 h-4 text-blue-600" />
                <h3 className="font-bold text-sm text-slate-900">Đăng Nhập Cổng Admin</h3>
              </div>
              <button onClick={() => setShowAdminLogin(false)} className="text-slate-400 hover:text-slate-600">&times;</button>
            </div>

            {loginError && (
              <div className="p-2.5 bg-red-50 text-red-700 rounded text-xs font-medium">
                {loginError}
              </div>
            )}

            <form onSubmit={handleAdminLoginSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Tài khoản:</label>
                <input
                  type="text"
                  value={loginUsername}
                  onChange={e => setLoginUsername(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  required
                />
              </div>
              <div>
                <label className="block font-medium text-slate-700 mb-1">Mật khẩu:</label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={e => setLoginPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  required
                />
              </div>

              <div className="p-2.5 bg-slate-50 rounded text-[11px] text-slate-500 space-y-1">
                <p>Tài khoản mẫu:</p>
                <p>• Chủ shop: <strong>admin</strong> / <strong>admin123</strong></p>
                <p>• Thủ kho: <strong>kho</strong> / <strong>kho123</strong></p>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg text-xs transition"
                >
                  Đăng nhập vào hệ thống
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <WishlistProvider>
            <CartProvider>
              <AppContent />
            </CartProvider>
          </WishlistProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;

