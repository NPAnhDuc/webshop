import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { useProductsQuery } from './hooks/useQueries';
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
import { CartDrawer } from './components/storefront/CartDrawer';
import type { AdminTabType } from './components/admin/AdminLayout';

// Lazy-loaded heavy modules for lightning-fast initial page load
const ProductDetailModal = React.lazy(() => import('./components/storefront/ProductDetailModal').then(m => ({ default: m.ProductDetailModal })));
const ProductDetailPage = React.lazy(() => import('./components/storefront/ProductDetailPage').then(m => ({ default: m.ProductDetailPage })));
const OrderTrackingPage = React.lazy(() => import('./components/storefront/OrderTrackingPage').then(m => ({ default: m.OrderTrackingPage })));
const ComparisonPage = React.lazy(() => import('./components/storefront/ComparisonPage').then(m => ({ default: m.ComparisonPage })));
const CheckoutModal = React.lazy(() => import('./components/common/CheckoutModal').then(m => ({ default: m.CheckoutModal })));
const OrderLookupModal = React.lazy(() => import('./components/common/OrderLookupModal').then(m => ({ default: m.OrderLookupModal })));
const CustomerChatWidget = React.lazy(() => import('./components/chatbot/CustomerChatWidget').then(m => ({ default: m.CustomerChatWidget })));
const PCBuilderView = React.lazy(() => import('./components/pc-builder/PCBuilderView').then(m => ({ default: m.PCBuilderView })));

const AdminLayout = React.lazy(() => import('./components/admin/AdminLayout').then(m => ({ default: m.AdminLayout })));
const DashboardView = React.lazy(() => import('./components/admin/DashboardView').then(m => ({ default: m.DashboardView })));
const InventoryManagement = React.lazy(() => import('./components/admin/InventoryManagement').then(m => ({ default: m.InventoryManagement })));
const OrderManagement = React.lazy(() => import('./components/admin/OrderManagement').then(m => ({ default: m.OrderManagement })));
const DocumentManagement = React.lazy(() => import('./components/admin/DocumentManagement').then(m => ({ default: m.DocumentManagement })));
const AdminChatbotView = React.lazy(() => import('./components/admin/AdminChatbotView').then(m => ({ default: m.AdminChatbotView })));
const ProductManagement = React.lazy(() => import('./components/admin/ProductManagement').then(m => ({ default: m.ProductManagement })));
const PromotionManagement = React.lazy(() => import('./components/admin/PromotionManagement').then(m => ({ default: m.PromotionManagement })));
const CustomerManagement = React.lazy(() => import('./components/admin/CustomerManagement').then(m => ({ default: m.CustomerManagement })));
const QuotationManagement = React.lazy(() => import('./components/admin/QuotationManagement').then(m => ({ default: m.QuotationManagement })));
const ReviewManagement = React.lazy(() => import('./components/admin/ReviewManagement').then(m => ({ default: m.ReviewManagement })));
const StoreSettingsManagement = React.lazy(() => import('./components/admin/StoreSettingsManagement').then(m => ({ default: m.StoreSettingsManagement })));

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
  ArrowLeft,
  ShieldCheck,
  Zap,
  RotateCcw,
  Award,
  Activity,
  Wrench,
  CreditCard,
  Home,
  Heart
} from 'lucide-react';

export type AppView = 'storefront' | 'pc-builder' | 'admin' | 'product-detail' | 'track-order' | 'compare';

const AppContent: React.FC = () => {
  const { isAuthenticated, login } = useAuth();
  const { t, lang } = useLanguage();

  // Navigation Views: 'storefront' | 'pc-builder' | 'admin' | 'product-detail' | 'track-order' | 'compare'
  const [currentView, setCurrentView] = useState<AppView>(() => {
    if (typeof window !== 'undefined') {
      const hash = window.location.hash.replace(/^#\/?/, '').toLowerCase();
      if (hash.startsWith('admin')) return 'admin';
      if (hash.startsWith('pc-builder') || hash.startsWith('build-pc')) return 'pc-builder';
      if (hash.startsWith('product/')) return 'product-detail';
      if (hash.startsWith('track-order') || hash.startsWith('lookup')) return 'track-order';
      if (hash.startsWith('compare')) return 'compare';
    }
    return 'storefront';
  });

  const [activeProductSlug, setActiveProductSlug] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      const rawHash = window.location.hash.replace(/^#\/?/, '').trim();
      if (rawHash.toLowerCase().startsWith('product/')) {
        return rawHash.substring('product/'.length).trim() || null;
      }
    }
    return null;
  });

  const [adminTab, setAdminTab] = useState<AdminTabType>('dashboard');

  const navigateToView = (view: AppView, pushHistory = true) => {
    setCurrentView(view);
    let targetHash = '#/';
    if (view === 'storefront') targetHash = currentCategory !== 'all' ? `#/category/${currentCategory}` : '#/';
    else if (view === 'pc-builder') targetHash = '#/pc-builder';
    else if (view === 'admin') targetHash = '#/admin';
    else if (view === 'track-order') targetHash = '#/track-order';
    else if (view === 'compare') targetHash = '#/compare';
    else if (view === 'product-detail' && activeProductSlug) targetHash = `#/product/${activeProductSlug}`;

    if (window.location.hash !== targetHash) {
      if (pushHistory) {
        window.history.pushState(null, '', targetHash);
      } else {
        window.history.replaceState(null, '', targetHash);
      }
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navigateToProduct = (productSlugOrId: string, pushHistory = true) => {
    setActiveProductSlug(productSlugOrId);
    setCurrentView('product-detail');
    const targetHash = `#/product/${productSlugOrId}`;
    if (window.location.hash !== targetHash) {
      if (pushHistory) {
        window.history.pushState(null, '', targetHash);
      } else {
        window.history.replaceState(null, '', targetHash);
      }
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const syncViewFromHash = () => {
      const rawHash = window.location.hash.replace(/^#\/?/, '').trim();
      const hash = rawHash.toLowerCase();

      if (hash.startsWith('admin')) {
        setCurrentView('admin');
      } else if (hash.startsWith('pc-builder') || hash.startsWith('build-pc')) {
        setCurrentView('pc-builder');
      } else if (hash.startsWith('product/')) {
        const slug = rawHash.substring('product/'.length).trim();
        setActiveProductSlug(slug || null);
        setCurrentView('product-detail');
      } else if (hash.startsWith('track-order') || hash.startsWith('lookup')) {
        setCurrentView('track-order');
      } else if (hash.startsWith('compare')) {
        setCurrentView('compare');
      } else if (hash.startsWith('category/')) {
        const cat = rawHash.substring('category/'.length).trim();
        setCurrentView('storefront');
        if (cat) {
          setCurrentCategory(cat);
        }
      } else {
        setCurrentView('storefront');
        if (hash === '' || hash === '/') {
          setCurrentCategory('all');
        }
      }
    };

    window.addEventListener('popstate', syncViewFromHash);
    window.addEventListener('hashchange', syncViewFromHash);
    syncViewFromHash();

    return () => {
      window.removeEventListener('popstate', syncViewFromHash);
      window.removeEventListener('hashchange', syncViewFromHash);
    };
  }, []);

  

  // Filters State
  const [currentCategory, setCurrentCategory] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      const rawHash = window.location.hash.replace(/^#\/?/, '').trim();
      if (rawHash.toLowerCase().startsWith('category/')) {
        return rawHash.substring('category/'.length).trim() || 'all';
      }
    }
    return 'all';
  });
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

// Computed filter parameters memoized for TanStack Query
  const productFilterParams = React.useMemo(() => {
    let minPrice: number | undefined;
    let maxPrice: number | undefined;

    if (selectedPriceRange === 'under15m' || selectedPriceRange === 'under_15') maxPrice = 15000000;
    else if (selectedPriceRange === 'from15to20m' || selectedPriceRange === '15_to_20') { minPrice = 15000000; maxPrice = 20000000; }
    else if (selectedPriceRange === 'from20to30m' || selectedPriceRange === '20_to_30') { minPrice = 20000000; maxPrice = 30000000; }
    else if (selectedPriceRange === 'above30m' || selectedPriceRange === 'above_30') minPrice = 30000000;

    return {
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
    };
  }, [
    currentCategory,
    selectedBrand,
    selectedPriceRange,
    selectedDemand,
    selectedPanel,
    inStockOnly,
    hasInstallment0,
    searchQuery,
    sortBy
  ]);

  // TanStack Query automatically manages caching, prefetching and stale-while-revalidate
  const { data: productQueryResult, isLoading: loading } = useProductsQuery(
    productFilterParams,
    currentView === 'storefront' || currentView === 'product-detail'
  );

  const products = productQueryResult?.products || [];
  const facets = productQueryResult?.facets || {};
  const totalProducts = productQueryResult?.total || 0;

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
    setWishlistFilterOnly(false);
  };

  const handleSelectCategory = (cat: string, pushHistory = true) => {
    setCurrentCategory(cat);
    if (currentView !== 'storefront') {
      setCurrentView('storefront');
    }
    const targetHash = cat === 'all' ? '#/' : `#/category/${cat}`;
    if (window.location.hash !== targetHash) {
      if (pushHistory) {
        window.history.pushState(null, '', targetHash);
      } else {
        window.history.replaceState(null, '', targetHash);
      }
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateHome = () => {
    // 1. Reset all filters and search query
    setSelectedBrand(undefined);
    setSelectedPriceRange(undefined);
    setSelectedDemand(undefined);
    setSelectedPanel(undefined);
    setInStockOnly(false);
    setHasInstallment0(false);
    setSearchQuery('');
    setSortBy('featured');
    setCurrentCategory('all');
    setWishlistFilterOnly(false);

    // 2. Dismiss any open modals or detail views
    setSelectedProduct(null);
    setActiveProductSlug(null);
    setShowCheckout(false);
    setShowOrderLookup(false);
    setShowAdminLogin(false);
    setShowComparisonModal(false);

    // 3. Switch view to storefront with URL hash sync
    navigateToView('storefront', true);

    // 4. Smooth scroll to top of page
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleScrollToSection = (sectionId: string) => {
    if (currentView !== 'storefront') {
      handleNavigateHome();
    } else {
      // If filters hide the showcases, clear them so sections exist in the DOM
      if (currentCategory !== 'all' || searchQuery !== '') {
        setCurrentCategory('all');
        setSearchQuery('');
      }
    }

    setTimeout(() => {
      const el = document.getElementById(sectionId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  const handleToggleCompare = (product: Product) => {
    setComparingProducts(prev => {
      const exists = prev.some(p => p.id === product.id);
      if (exists) {
        return prev.filter(p => p.id !== product.id);
      } else {
        if (prev.length >= 4) {
          addToast('Chỉ so sánh tối đa 4 máy', 'Vui lòng bỏ bớt 1 máy để chọn máy mới', 'warning');
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
      navigateToView('admin', true);
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
      navigateToView('admin', true);
      addToast('Đăng nhập quản trị thành công', 'Chào mừng Chị Lan (Chủ shop)', 'success');
    } else if (loginUsername === 'kho' && loginPassword === 'kho123') {
      login('jwt-mock-wh', {
        id: 'usr-2',
        name: 'Anh Tuấn (Nhân Viên Kho)',
        role: 'warehouse',
        email: 'tuan.kho@techstore.vn'
      });
      setShowAdminLogin(false);
      navigateToView('admin', true);
      addToast('Đăng nhập thủ kho thành công', 'Chào mừng Anh Tuấn (Kho)', 'success');
    } else {
      setLoginError('Tên đăng nhập hoặc mật khẩu không đúng (Gợi ý: admin / admin123)');
    }
  };

  // Prefetch admin modules in background to completely eliminate tab-switching delay & flicker
  useEffect(() => {
    if (currentView === 'admin' && isAuthenticated) {
      import('./components/admin/ProductManagement');
      import('./components/admin/InventoryManagement');
      import('./components/admin/OrderManagement');
      import('./components/admin/PromotionManagement');
      import('./components/admin/QuotationManagement');
      import('./components/admin/CustomerManagement');
      import('./components/admin/ReviewManagement');
      import('./components/admin/DocumentManagement');
      import('./components/admin/AdminChatbotView');
      import('./components/admin/StoreSettingsManagement');
    }
  }, [currentView, isAuthenticated]);

  // Render Admin View
  if (currentView === 'admin' && isAuthenticated) {
    return (
      <>
        <AdminLayout
          currentTab={adminTab}
          onSelectTab={setAdminTab}
          onBackToStorefront={handleNavigateHome}
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
        <ToastContainer toasts={toasts} onDismiss={removeToast} />
      </>
    );
  }

  // Render Customer-Facing Layout
  return (
    <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 flex flex-col justify-between selection:bg-red-600 selection:text-white relative transition-colors duration-200">
      {/* Interactive Side Wings for Wide Screens */}
      <SideWings
        onNavigatePCBuilder={() => navigateToView('pc-builder')}
        onOpenLookup={() => navigateToView('track-order')}
      />

      {/* 1. Header Navigation */}
      <Navbar
        onSearch={q => {
          setSearchQuery(q);
          navigateToView('storefront');
        }}
        onOpenLookup={() => navigateToView('track-order')}
        onNavigatePCBuilder={() => navigateToView('pc-builder')}
        onNavigateAdmin={handleAdminClick}
        onNavigateHome={handleNavigateHome}
        onNavigateSection={handleScrollToSection}
        onSelectCategory={cat => handleSelectCategory(cat)}
        onSelectProduct={prod => navigateToProduct(prod.slug || prod.id)}
        currentCategory={currentCategory}
        onToggleWishlistFilter={() => {
          setWishlistFilterOnly(prev => !prev);
          navigateToView('storefront');
        }}
        isWishlistFilterActive={wishlistFilterOnly}
      />

      {/* Main View Router */}
      {currentView === 'pc-builder' ? (
        <PCBuilderView
          onBackToHome={handleNavigateHome}
          onSelectProduct={prod => navigateToProduct(prod.slug || prod.id)}
          onToast={(title, msg) => addToast(title, msg, 'success')}
        />
      ) : currentView === 'product-detail' && activeProductSlug ? (
        <ProductDetailPage
          productSlugOrId={activeProductSlug}
          initialProduct={products.find(p => p.slug === activeProductSlug || p.id === activeProductSlug) || null}
          onBack={() => {
            if (window.history.length > 1) {
              window.history.back();
            } else {
              handleNavigateHome();
            }
          }}
          onSelectProduct={prod => navigateToProduct(prod.slug || prod.id)}
          onNavigateCategory={cat => handleSelectCategory(cat)}
          onNavigateHome={handleNavigateHome}
          onNavigatePCBuilder={() => navigateToView('pc-builder')}
          onProceedToCheckout={() => setShowCheckout(true)}
          onToast={(title, msg, type) => addToast(title, msg, type === 'error' ? 'warning' : (type || 'success'))}
          isComparing={prod => comparingProducts.some(p => p.id === prod.id)}
          onToggleCompare={handleToggleCompare}
        />
      ) : currentView === 'track-order' ? (
        <OrderTrackingPage
          onBackToHome={handleNavigateHome}
          onNavigateProduct={slug => navigateToProduct(slug)}
        />
      ) : currentView === 'compare' ? (
        <ComparisonPage
          products={comparingProducts}
          onRemoveProduct={id => setComparingProducts(prev => prev.filter(p => p.id !== id))}
          onClearAll={() => setComparingProducts([])}
          onSelectProduct={slug => navigateToProduct(slug)}
          onBackToHome={handleNavigateHome}
          onToast={(title, msg, type) => addToast(title, msg, type || 'info')}
        />
      ) : (
        /* Storefront View (Catalog & Category Mode) */
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
              onNavigatePCBuilder={() => navigateToView('pc-builder')}
              onFilterDemand={demand => setSelectedDemand(demand)}
              onSelectCategory={cat => handleSelectCategory(cat)}
            />
          )}

          {/* Flash Sale Banner with Live Timer (TechStore Hot Sale Cuối Tuần) */}
          {!searchQuery && currentCategory === 'all' && (
            <FlashSaleBanner
              products={products}
              onSelectProduct={prod => navigateToProduct(prod.slug || prod.id)}
              onAskBot={prod => prod && navigateToProduct(prod.slug || prod.id)}
            />
          )}

          {/* CellphoneS-Style High-Conversion Quick Service & Event Bar */}
          {!searchQuery && currentCategory === 'all' && (
            <div className="mb-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
              <button
                onClick={() => navigateToView('pc-builder')}
                className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-[#d70018] group-hover:text-white transition flex items-center justify-center font-bold flex-shrink-0">
                  <SlidersHorizontal className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#d70018] dark:group-hover:text-red-400">Tự Ráp PC</span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Quà tặng 2 triệu</span>
                </div>
              </button>

              <button
                onClick={() => {
                  setSelectedDemand('gaming');
                  document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-[#d70018] group-hover:text-white transition flex items-center justify-center font-bold flex-shrink-0">
                  <Flame className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#d70018] dark:group-hover:text-red-400">Laptop Gaming</span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">RTX 40 Series</span>
                </div>
              </button>

              <button
                onClick={() => {
                  setHasInstallment0(true);
                  document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-blue-600 group-hover:text-white transition flex items-center justify-center font-bold flex-shrink-0">
                  <CreditCard className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#d70018] dark:group-hover:text-red-400">Trả Góp 0%</span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Duyệt nhanh 15P</span>
                </div>
              </button>

              <button
                onClick={() => {
                  setSelectedDemand('thin_light');
                  document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-slate-900 group-hover:text-white dark:group-hover:bg-slate-700 transition flex items-center justify-center font-bold flex-shrink-0">
                  <Award className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#d70018] dark:group-hover:text-red-400">Sinh Viên Giảm 500k</span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Ưu đãi T-Student</span>
                </div>
              </button>

              <button
                onClick={() => {
                  setSelectedPanel('OLED');
                  document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-purple-600 group-hover:text-white transition flex items-center justify-center font-bold flex-shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#d70018] dark:group-hover:text-red-400">Màn Hình OLED</span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Chuẩn màu 100% P3</span>
                </div>
              </button>

              <button
                onClick={handleResetFilters}
                className="p-3 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 hover:border-red-500 dark:hover:border-red-500 rounded-xl transition shadow-2xs hover:shadow-xs flex items-center space-x-2.5 text-left group cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-red-600 group-hover:text-white transition flex items-center justify-center font-bold flex-shrink-0">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block truncate group-hover:text-[#d70018] dark:group-hover:text-red-400">1 Đổi 1 30 Ngày</span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">Chính hãng 100%</span>
                </div>
              </button>
            </div>
          )}

          {/* Dedicated Category Hero Banner when in a specific category */}
          {currentCategory !== 'all' && (
            <div className="mb-6 bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 text-white rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-lg relative overflow-hidden">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-2 text-xs text-red-400 font-bold uppercase tracking-wider">
                    <button onClick={handleNavigateHome} className="flex items-center space-x-1 text-slate-400 hover:text-white transition cursor-pointer">
                      <Home className="w-3.5 h-3.5" />
                      <span>Trang Chủ</span>
                    </button>
                    <span>/</span>
                    <span>Danh Mục Ngành Hàng</span>
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-black uppercase text-white tracking-tight">
                    {currentCategory === 'laptop' ? 'Laptop Gaming & Đồ Họa Cao Cấp'
                      : currentCategory === 'pc' ? 'Bộ Máy Tính PC & Màn Hình Chuyên Nghiệp'
                      : currentCategory === 'cpu' ? 'Vi Xử Lý CPU Intel & AMD Chính Hãng'
                      : currentCategory === 'vga' ? 'Card Màn Hình VGA Đồ Họa & Gaming'
                      : currentCategory === 'mainboard' ? 'Bo Mạch Chủ Mainboard'
                      : currentCategory === 'ram' ? 'Bộ Nhớ Trong RAM DDR4 / DDR5'
                      : currentCategory === 'ssd' ? 'Ổ Cứng SSD Tốc Độ Cao NVMe PCIe'
                      : currentCategory === 'psu' ? 'Nguồn Máy Tính Chuẩn 80 Plus'
                      : currentCategory === 'case' ? 'Vỏ Case & Tản Nhiệt Cao Cấp'
                      : `Danh mục: ${currentCategory.toUpperCase()}`}
                  </h1>
                  <p className="text-xs text-slate-300 max-w-2xl">
                    100% linh kiện chính hãng, bảo hành đổi mới 30 ngày, trả góp 0% lãi suất, hỗ trợ giao hàng hỏa tốc 2 giờ toàn quốc.
                  </p>
                </div>
                <button
                  onClick={handleNavigateHome}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 self-start sm:self-auto cursor-pointer shadow-xs active:scale-95"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Về Trang Chủ</span>
                </button>
              </div>
            </div>
          )}

          {/* Nguyễn Công PC & HACOM Signature Industry Showcases (Homepage only) */}
          {!searchQuery && currentCategory === 'all' && !selectedBrand && !selectedPriceRange && !selectedDemand && !selectedPanel && !hasInstallment0 && !inStockOnly && !wishlistFilterOnly && (
            <div className="mb-10">
              <PCStorefrontShowcases
                products={products}
                onSelectProduct={prod => navigateToProduct(prod.slug || prod.id)}
                onNavigatePCBuilder={() => navigateToView('pc-builder')}
                onFilterCategory={cat => handleSelectCategory(cat)}
                onFilterDemand={dem => {
                  setSelectedDemand(dem);
                  document.getElementById('product-catalog-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                onAskBot={prod => navigateToProduct(prod.slug || prod.id)}
                isComparing={prod => comparingProducts.some(p => p.id === prod.id)}
                onToggleCompare={handleToggleCompare}
                onAddToCartToast={name => addToast(lang === 'vi' ? 'Đã thêm vào giỏ hàng' : 'Added to cart', name, 'success')}
              />
            </div>
          )}

          {/* Catalog Section with Sidebar Filters & Product Grid */}
          <div id="product-catalog-section" className="scroll-mt-24 pt-4 border-t border-gray-200 dark:border-slate-800">
            {/* Breadcrumb Navigation when filtered or in specific category */}
            {currentCategory !== 'all' && (
              <div className="mb-3 flex items-center space-x-2 text-xs">
                <button
                  onClick={handleNavigateHome}
                  className="text-slate-500 hover:text-[#d70018] dark:text-slate-400 dark:hover:text-red-400 font-bold flex items-center space-x-1.5 cursor-pointer"
                >
                  <Home className="w-3.5 h-3.5" />
                  <span>Trang Chủ</span>
                </button>
                <span className="text-slate-400">/</span>
                <span className="text-slate-500 dark:text-slate-400">Danh mục</span>
                <span className="text-slate-400">/</span>
                <span className="font-extrabold text-[#d70018] dark:text-red-400 uppercase">
                  {currentCategory}
                </span>
              </div>
            )}

            <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#d70018] text-white flex items-center justify-center font-bold shadow-xs flex-shrink-0">
                  <SlidersHorizontal className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base sm:text-lg font-black uppercase text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                    <span>{currentCategory !== 'all' ? `DANH MỤC: ${currentCategory.toUpperCase()}` : 'TOÀN BỘ KHO SẢN PHẨM & BỘ LỌC ĐA CHIỀU'}</span>
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Tùy chọn lọc thông số chi tiết theo tiêu chuẩn Showroom Máy tính chuyên nghiệp
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {currentCategory !== 'all' && (
                  <button
                    onClick={handleNavigateHome}
                    className="px-3.5 py-1.5 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer shadow-xs active:scale-95"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    <span>Về Trang Chủ</span>
                  </button>
                )}
                {(currentCategory !== 'all' || selectedBrand || selectedPriceRange || selectedDemand || selectedPanel || inStockOnly || hasInstallment0 || searchQuery) && (
                  <button
                    onClick={handleNavigateHome}
                    className="px-3 py-1.5 text-xs text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl border border-rose-200 dark:border-rose-900/50 font-bold cursor-pointer transition"
                  >
                    Xóa tất cả bộ lọc ×
                  </button>
                )}
              </div>
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
                      { label: 'Dưới 15 triệu', val: 'under15m' },
                      { label: '15 - 20 triệu', val: 'from15to20m' },
                      { label: '20 - 30 triệu', val: 'from20to30m' },
                      { label: 'Trên 30 triệu', val: 'above30m' }
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
                        <span className="flex items-center space-x-1"><Heart className="w-3.5 h-3.5 fill-rose-500 text-rose-500" /><span>{lang === 'vi' ? 'Danh sách sản phẩm Yêu thích' : 'Wishlist Products'}</span></span>
                        <span className="text-xs text-slate-500 font-normal">
                          ({products.filter(p => wishlistIds.includes(p.id)).length} {lang === 'vi' ? 'sản phẩm' : 'items'})
                        </span>
                      </span>
                    ) : (
                      <>
                        {t('found')} <strong className="text-[#d70018] dark:text-red-400 font-bold">{totalProducts}</strong> {t('productsMatch')}
                        {searchQuery && <span> {t('forKeyword')} "<span className="text-[#d70018] dark:text-red-400 font-bold">{searchQuery}</span>"</span>}
                      </>
                    )}
                  </div>

                  {/* Sort Options */}
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500 dark:text-slate-400 font-medium">{t('sort')}</span>
                    <select
                      value={sortBy}
                      onChange={e => setSortBy(e.target.value as any)}
                      className="px-3 py-1.5 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-semibold focus:outline-none focus:border-[#d70018] text-xs cursor-pointer"
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
                        ? (lang === 'vi' ? 'Hãy bấm icon trái tim trên sản phẩm để lưu lại xem sau!' : 'Click the heart ❤️ icon on any product to save it here!')
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
                      className="mt-2 px-5 py-2.5 bg-[#d70018] text-white rounded-xl text-xs font-bold hover:bg-[#b91c1c] transition shadow-xs cursor-pointer"
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
                        onSelect={p => navigateToProduct(p.slug || p.id)}
                        onAskBot={p => navigateToProduct(p.slug || p.id)}
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
      )}

      {/* Floating Comparison Bar (when items are selected for comparison) */}
      <ComparisonBar
        products={comparingProducts}
        onRemove={id => setComparingProducts(prev => prev.filter(p => p.id !== id))}
        onClear={() => setComparingProducts([])}
        onOpenModal={() => navigateToView('compare')}
      />

      {/* Side-by-Side Comparison Matrix Modal */}
      <ComparisonModal
        products={comparingProducts}
        isOpen={showComparisonModal}
        onClose={() => setShowComparisonModal(false)}
        onAskBotCompare={prods => {
          setShowComparisonModal(false);
          navigateToProduct(prods[0].slug || prods[0].id);
        }}
      />

      {/* Footer */}
      <Footer />

      {/* Floating Customer AI Chatbot */}
      <CustomerChatWidget
        currentProduct={selectedProduct}
        onSelectProduct={p => navigateToProduct(p.slug || p.id)}
      />

      {/* Cart Drawer */}
      <CartDrawer onProceedToCheckout={() => setShowCheckout(true)} />

      {/* Product Detail Modal */}
      <ProductDetailModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAskBot={prod => {
          navigateToProduct(prod.slug || prod.id);
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
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <WishlistProvider>
            <CartProvider>
              <React.Suspense fallback={
              <div className="min-h-screen bg-[#f4f6f8] dark:bg-[#0b0f19] flex items-center justify-center">
                <div className="w-8 h-8 rounded-full border-3 border-slate-300 dark:border-slate-700 border-t-[#d70018] animate-spin" />
              </div>
            }>
              <AppContent />
            </React.Suspense>
            </CartProvider>
          </WishlistProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
