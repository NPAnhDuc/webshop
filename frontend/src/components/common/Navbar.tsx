import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  ShoppingCart,
  PhoneCall,
  MapPin,
  FileText,
  SlidersHorizontal,
  ChevronDown,
  LayoutGrid,
  ShieldCheck,
  Truck,
  RotateCcw,
  Sparkles,
  User,
  Menu,
  X,
  ChevronRight,
  Cpu,
  Sun,
  Moon,
  Globe,
  Mic,
  Volume2,
  VolumeX,
  Heart,
  Laptop,
  Monitor,
  Gamepad2,
  Layers,
  CircuitBoard,
  HardDrive,
  Zap,
  Box,
  Tag,
  Home
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useTheme } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { useWishlist } from '../../context/WishlistContext';
import { sound } from '../../utils/sound';
import { Product } from '../../types';
import { fetchStoreSettings } from '../../services/api';

interface NavbarProps {
  onSearch: (q: string) => void;
  onOpenLookup: () => void;
  onNavigatePCBuilder: () => void;
  onNavigateAdmin: () => void;
  onNavigateHome: () => void;
  onSelectCategory: (categorySlug: string) => void;
  onSelectProduct?: (product: Product) => void;
  onNavigateSection?: (sectionId: string) => void;
  currentCategory?: string;
  onOpenBotChat?: () => void;
  onToggleWishlistFilter?: () => void;
  isWishlistFilterActive?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onSearch,
  onOpenLookup,
  onNavigatePCBuilder,
  onNavigateAdmin,
  onNavigateHome,
  onSelectCategory,
  onSelectProduct,
  onNavigateSection,
  currentCategory,
  onOpenBotChat,
  onToggleWishlistFilter,
  isWishlistFilterActive = false
}) => {
  const { openCart, totalItems } = useCart();
  const { theme, toggleTheme } = useTheme();
  const { lang, toggleLang, t } = useLanguage();
  const { count: wishlistCount } = useWishlist();
  const [isMuted, setIsMuted] = useState(sound.getIsMuted());
  const [isListening, setIsListening] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Product[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showCategoryMenu, setShowCategoryMenu] = useState(false);
  const [selectedCity, setSelectedCity] = useState<'HCM' | 'HN'>('HN');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [storeSettings, setStoreSettings] = useState<any>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  const categoryMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStoreSettings()
      .then(data => {
        if (data) setStoreSettings(data);
      })
      .catch(() => {});
  }, []);

  const handleToggleMute = () => {
    setIsMuted(sound.toggleMute());
  };

  const handleVoiceSearch = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert(lang === 'vi' ? 'Trình duyệt của bạn chưa hỗ trợ nhận diện giọng nói (Hãy thử dùng Google Chrome hoặc MS Edge).' : 'Your browser does not support Voice Recognition. Please try Google Chrome or MS Edge.');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = lang === 'vi' ? 'vi-VN' : 'en-US';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setSearchQuery(transcript);
        onSearch(transcript);
        setIsListening(false);
        sound.playPop();
      };

      recognition.onerror = (event: any) => {
        console.warn('Voice search error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (err) {
      console.error('Failed to start voice recognition', err);
      setIsListening(false);
    }
  };

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/products?q=${encodeURIComponent(searchQuery)}&limit=6`);
        const json = await res.json();
        if (json.products) {
          setSuggestions(json.products);
        }
      } catch (err) {
        console.error(err);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
      if (categoryMenuRef.current && !categoryMenuRef.current.contains(e.target as Node)) {
        setShowCategoryMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    onSearch(searchQuery);
  };

  const categories = [
    { slug: 'all', label: t('all'), icon: LayoutGrid },
    { slug: 'laptop', label: t('laptop'), icon: Laptop },
    { slug: 'pc', label: 'PC, Màn hình, Máy in', icon: Monitor },
    { slug: 'cpu', label: t('cpu'), icon: Cpu },
    { slug: 'vga', label: t('vga'), icon: Gamepad2 },
    { slug: 'mainboard', label: t('mainboard'), icon: Layers },
    { slug: 'ram', label: t('ram'), icon: CircuitBoard },
    { slug: 'ssd', label: t('ssd'), icon: HardDrive },
    { slug: 'psu', label: t('psu'), icon: Zap },
    { slug: 'case', label: t('case'), icon: Box }
  ];

  return (
    <header className="sticky top-0 z-40 w-full shadow-md select-none">
      {/* 1. Top Announcement Marquee Strip */}
      <div className="w-full bg-[#0f172a] dark:bg-[#070b13] text-slate-300 text-[11px] py-1.5 px-4 border-b border-slate-800 transition-colors">
        <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-6 overflow-hidden">
            <span className="flex items-center space-x-1.5 whitespace-nowrap">
              <ShieldCheck className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
              <span>
                {storeSettings?.marqueeText ? (
                  <span>{storeSettings.marqueeText}</span>
                ) : lang === 'vi' ? (
                  <>Sản phẩm <strong className="font-bold text-white underline decoration-red-500">Chính hãng 100%</strong> - Xuất VAT đầy đủ</>
                ) : (
                  <>100% <strong className="font-bold text-white underline decoration-red-500">Genuine</strong> - Full VAT Invoice</>
                )}
              </span>
            </span>
            <span className="hidden md:flex items-center space-x-1.5 whitespace-nowrap text-slate-400">
              <Truck className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
              <span>{storeSettings?.freeShippingThreshold ? `Freeship từ ${new Intl.NumberFormat('vi-VN').format(storeSettings.freeShippingThreshold)}₫` : t('freeShipping')}</span>
            </span>
            <span className="hidden lg:flex items-center space-x-1.5 whitespace-nowrap text-slate-400">
              <RotateCcw className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
              <span>{t('warranty')}</span>
            </span>
          </div>

          <div className="flex items-center space-x-2.5 sm:space-x-3.5 text-[11px] flex-shrink-0">
            <a
              href={`tel:${storeSettings?.hotlineSales?.replace(/[^0-9]/g, '') || '19000323'}`}
              className="hidden sm:flex items-center space-x-1 hover:text-white transition"
            >
              <PhoneCall className="w-3 h-3 text-red-400" />
              <span>{storeSettings?.hotlineSales ? `Hotline: ${storeSettings.hotlineSales}` : t('hotline')}</span>
            </a>
            <span className="hidden sm:inline text-slate-700">|</span>
            <button
              onClick={onOpenLookup}
              className="flex items-center space-x-1 hover:text-white transition cursor-pointer"
            >
              <FileText className="w-3 h-3 text-slate-400" />
              <span>{t('trackOrder')}</span>
            </button>
            <span className="text-slate-700">|</span>
            <button
              onClick={onNavigateAdmin}
              className="flex items-center space-x-1 text-slate-200 hover:text-white font-bold transition cursor-pointer"
            >
              <User className="w-3 h-3" />
              <span>{t('account')}</span>
            </button>
            <span className="text-slate-700">|</span>

            {/* Language Switcher Toggle */}
            <button
              onClick={toggleLang}
              className="flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-bold transition text-[11px] cursor-pointer"
              title={lang === 'vi' ? 'Chuyển sang English' : 'Switch to Tiếng Việt'}
            >
              <Globe className="w-3 h-3 text-slate-300" />
              <span>{lang === 'vi' ? 'VN' : 'EN'}</span>
            </button>

            {/* Theme Mode Switcher Toggle */}
            <button
              onClick={toggleTheme}
              className="flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white font-bold transition text-[11px] cursor-pointer"
              title={theme === 'light' ? 'Chuyển sang Giao diện Tối' : 'Chuyển sang Giao diện Sáng'}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-slate-300" />}
              <span className="hidden sm:inline">{theme === 'dark' ? 'Light' : 'Dark'}</span>
            </button>

            {/* Sound Effects Audio Toggle */}
            <button
              onClick={handleToggleMute}
              className={`flex items-center space-x-1 px-2 py-0.5 rounded-lg border transition text-[11px] cursor-pointer ${
                isMuted
                  ? 'bg-slate-900 border-slate-800 text-slate-500'
                  : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200 font-bold'
              }`}
              title={isMuted ? 'Bật âm thanh tương tác' : 'Tắt âm thanh'}
              aria-label="Toggle sound"
            >
              {isMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
              <span className="hidden sm:inline">{isMuted ? 'Mute' : 'Audio'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Main TechStore Bar (Tech Red in Light, Deep Slate in Dark) */}
      <div className="w-full bg-[#d70018] dark:bg-[#0f172a] text-white border-b border-transparent dark:border-slate-800 transition-colors">
        <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 py-2.5 flex items-center justify-between gap-2 md:gap-3">
          
          {/* Brand Logo: TechStore */}
          <button
            onClick={onNavigateHome}
            className="flex items-center space-x-2 text-left group flex-shrink-0 cursor-pointer"
            title="Về trang chủ TechStore"
          >
            <div className="w-10 h-10 rounded-xl bg-white text-[#d70018] dark:bg-slate-800 dark:text-red-500 flex items-center justify-center shadow-md group-hover:scale-105 transition-transform flex-shrink-0">
              <Cpu className="w-6 h-6" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl sm:text-3xl font-black tracking-tight text-white font-sans leading-none">
                  TechStore
                </span>
                <span className="text-[9px] font-extrabold uppercase tracking-wider px-1.5 py-0.5 rounded bg-white text-slate-900 ml-1">
                  STUDIO
                </span>
              </div>
              <span className="text-[10px] text-red-100 dark:text-slate-400 font-medium tracking-wide">
                {lang === 'vi' ? 'PC Đồ Họa - PC Gaming & Linh Kiện Chuyên Nghiệp' : 'Professional Graphics PCs, Gaming & Components'}
              </span>
            </div>
          </button>

          {/* Danh mục Button */}
          <div ref={categoryMenuRef} className="relative hidden lg:block">
            <button
              onClick={() => setShowCategoryMenu(!showCategoryMenu)}
              className="flex items-center space-x-1.5 px-3 py-2 bg-[#b91c1c] hover:bg-[#991b1b] dark:bg-slate-800 dark:hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer border border-red-400/30 dark:border-slate-700"
            >
              <LayoutGrid className="w-4 h-4 text-white" />
              <span>{t('categories')}</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showCategoryMenu ? 'rotate-180' : ''}`} />
            </button>

            {/* Category Dropdown */}
            {showCategoryMenu && (
              <div className="absolute left-0 top-full mt-2 w-64 bg-white dark:bg-[#151c2c] text-slate-800 dark:text-slate-100 rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-800 py-2 z-50 animate-in fade-in zoom-in-95">
                <div className="px-3 py-1.5 text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500 tracking-wider">
                  {lang === 'vi' ? 'Ngành hàng nổi bật' : 'Featured Categories'}
                </div>
                {categories.map(cat => {
                  const CatIcon = cat.icon;
                  return (
                    <button
                      key={cat.slug}
                      onClick={() => {
                        onSelectCategory(cat.slug);
                        setShowCategoryMenu(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018] dark:hover:text-red-400 transition text-left cursor-pointer ${
                        currentCategory === cat.slug
                          ? 'text-[#d70018] dark:text-red-400 bg-red-50 dark:bg-red-950/40 font-bold'
                          : 'text-slate-700 dark:text-slate-200'
                      }`}
                    >
                      <span className="flex items-center space-x-2.5">
                        <CatIcon className="w-4 h-4 text-slate-500" />
                        <span>{cat.label}</span>
                      </span>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Location Picker */}
          <button
            onClick={() => setSelectedCity(prev => prev === 'HN' ? 'HCM' : 'HN')}
            className="hidden xl:flex items-center space-x-1.5 px-2.5 py-1.5 bg-[#b91c1c] hover:bg-[#991b1b] dark:bg-slate-800 dark:hover:bg-slate-700 text-white rounded-xl text-[11px] font-medium transition cursor-pointer flex-shrink-0 border border-red-400/30 dark:border-slate-700"
            title="Đổi khu vực xem giá"
          >
            <MapPin className="w-3.5 h-3.5 text-white" />
            <div className="text-left leading-tight">
              <span className="block text-[9px] text-red-100 dark:text-slate-400">{lang === 'vi' ? 'Xem giá tại' : 'Location'}</span>
              <span className="font-bold">{selectedCity === 'HN' ? 'Hà Nội' : 'Hồ Chí Minh'}</span>
            </div>
            <ChevronDown className="w-3 h-3 text-white/70" />
          </button>

          {/* Big Search Bar */}
          <div ref={searchRef} className="relative flex-1 max-w-xl mx-1 md:mx-2">
            <form onSubmit={handleSearchSubmit} className="relative flex items-center">
              <div className="w-full bg-white dark:bg-slate-900 border border-transparent dark:border-slate-700 rounded-xl flex items-center pl-3 pr-1 py-1 shadow-inner focus-within:ring-2 focus-within:ring-slate-900 dark:focus-within:ring-red-500">
                <Search className="w-4 h-4 text-slate-400 flex-shrink-0 mr-2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => {
                    setSearchQuery(e.target.value);
                    setShowSuggestions(true);
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  placeholder={t('searchPlaceholder')}
                  className="w-full bg-transparent border-none outline-none text-slate-800 dark:text-slate-100 placeholder:text-slate-400 text-xs sm:text-sm py-1"
                />

                {/* Voice Search Button */}
                <button
                  type="button"
                  onClick={handleVoiceSearch}
                  title={isListening ? (lang === 'vi' ? 'Đang lắng nghe...' : 'Listening...') : (lang === 'vi' ? 'Tìm bằng giọng nói' : 'Voice Search')}
                  className={`p-1.5 rounded-lg mr-1.5 transition-all flex items-center justify-center cursor-pointer ${
                    isListening
                      ? 'bg-red-600 text-white animate-pulse ring-2 ring-red-300'
                      : 'text-slate-400 hover:text-slate-900 dark:hover:text-red-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Mic className="w-4 h-4" />
                </button>

                <button
                  type="submit"
                  className="bg-slate-900 hover:bg-slate-800 dark:bg-red-600 dark:hover:bg-red-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition active:scale-95 flex-shrink-0 cursor-pointer"
                >
                  {lang === 'vi' ? 'Tìm' : 'Search'}
                </button>
              </div>
            </form>

            {/* Listening Indicator Popup */}
            {isListening && (
              <div className="absolute left-0 top-full mt-2 px-3 py-1.5 bg-red-600 text-white text-xs font-bold rounded-xl shadow-xl flex items-center space-x-2 z-50 animate-bounce">
                <span className="w-2.5 h-2.5 rounded-full bg-white animate-ping" />
                <span>{lang === 'vi' ? 'Đang lắng nghe... Hãy nói tên máy hoặc linh kiện!' : 'Listening... Say product or component name!'}</span>
              </div>
            )}

            {/* Smart Suggestions Dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute left-0 right-0 top-full mt-2 bg-white dark:bg-[#151c2c] text-slate-800 dark:text-slate-100 rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-800 overflow-hidden z-50 animate-in fade-in">
                <div className="p-2.5 bg-gray-50 dark:bg-slate-850 border-b border-gray-200 dark:border-slate-800 text-xs font-bold text-slate-600 dark:text-slate-300 flex justify-between">
                  <span>{lang === 'vi' ? `Gợi ý tìm kiếm (${suggestions.length})` : `Search suggestions (${suggestions.length})`}</span>
                  <span className="text-[#d70018] hover:underline cursor-pointer" onClick={handleSearchSubmit}>
                    {lang === 'vi' ? 'Xem tất cả →' : 'View all →'}
                  </span>
                </div>
                <div className="divide-y divide-gray-100 dark:divide-slate-800 max-h-80 overflow-y-auto">
                  {suggestions.map(p => (
                    <div
                      key={p.id}
                      onClick={() => {
                        setShowSuggestions(false);
                        if (onSelectProduct) {
                          onSelectProduct(p);
                        } else {
                          onSearch(p.name);
                        }
                      }}
                      className="p-2.5 hover:bg-slate-50 dark:hover:bg-slate-800/80 cursor-pointer flex items-center space-x-3 transition group"
                    >
                      <img
                        src={p.imageUrl}
                        alt={p.name}
                        className="w-12 h-12 object-contain rounded-lg border border-gray-200 dark:border-slate-700 bg-white p-1"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 group-hover:text-[#d70018] dark:group-hover:text-red-400 truncate transition">
                          {p.name}
                        </p>
                        <div className="flex items-center space-x-2 mt-0.5">
                          <span className="text-xs font-bold text-[#d70018] dark:text-red-400 font-mono">
                            {new Intl.NumberFormat('vi-VN').format(p.price)}₫
                          </span>
                          {p.originalPrice && (
                            <span className="text-[11px] text-slate-400 line-through font-mono">
                              {new Intl.NumberFormat('vi-VN').format(p.originalPrice)}₫
                            </span>
                          )}
                          <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded font-medium">
                            {p.brandName}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Quick Action Buttons */}
          <div className="flex items-center space-x-2 sm:space-x-2.5 flex-shrink-0">
            {/* Build PC Button */}
            <button
              onClick={onNavigatePCBuilder}
              className="flex items-center space-x-1.5 px-3 py-2 bg-white hover:bg-slate-100 text-[#d70018] dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-white font-extrabold rounded-xl text-xs shadow-sm transition active:scale-95 group cursor-pointer border border-transparent dark:border-slate-700"
            >
              <SlidersHorizontal className="w-4 h-4 text-[#d70018] dark:text-white" />
              <span className="hidden sm:inline">Build PC</span>
            </button>

            {/* Wishlist Button */}
            <button
              onClick={() => {
                if (onToggleWishlistFilter) {
                  onToggleWishlistFilter();
                  sound.playPop();
                }
              }}
              className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-2 rounded-xl text-xs font-bold transition relative cursor-pointer border border-red-400/30 dark:border-slate-700 ${
                isWishlistFilterActive
                  ? 'bg-white text-rose-600 shadow-sm'
                  : 'bg-[#b91c1c] hover:bg-[#991b1b] dark:bg-slate-800 dark:hover:bg-slate-700 text-white'
              }`}
              title={lang === 'vi' ? 'Xem danh sách yêu thích' : 'Wishlist'}
              aria-label="Wishlist"
            >
              <Heart className={`w-4 h-4 ${isWishlistFilterActive || wishlistCount > 0 ? 'text-rose-300 fill-rose-300' : 'text-white'}`} />
              <span className="hidden md:inline">{lang === 'vi' ? 'Yêu thích' : 'Wishlist'}</span>
              {wishlistCount > 0 && (
                <span className="bg-white text-red-600 text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center shadow-sm">
                  {wishlistCount}
                </span>
              )}
            </button>

            {/* Cart Drawer Trigger */}
            <button
              onClick={openCart}
              className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-2 bg-[#b91c1c] hover:bg-[#991b1b] dark:bg-slate-800 dark:hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition relative cursor-pointer border border-red-400/30 dark:border-slate-700"
              aria-label="Giỏ hàng"
            >
              <ShoppingCart className="w-4 h-4 text-white" />
              <span className="hidden md:inline">{t('cart')}</span>
              {totalItems > 0 && (
                <span className="bg-white text-red-600 text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center shadow-sm">
                  {totalItems}
                </span>
              )}
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl text-white hover:bg-[#b91c1c] dark:hover:bg-slate-800 transition cursor-pointer"
              aria-label="Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* 3. Sub-Navbar */}
      <div className="w-full bg-white dark:bg-[#0c121e] border-b border-gray-200 dark:border-slate-800 shadow-2xs hidden md:block">
        <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 flex items-center justify-between text-xs py-1.5 font-bold text-slate-700 dark:text-slate-300">
          <div className="flex items-center space-x-1 overflow-x-auto scrollbar-none">
            {/* Mega Menu Toggle */}
            <button
              onClick={() => setShowCategoryMenu(!showCategoryMenu)}
              className="px-3 py-1.5 bg-[#d70018] hover:bg-[#b91c1c] text-white rounded-lg flex items-center space-x-1.5 mr-1 cursor-pointer transition shadow-xs flex-shrink-0"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>{lang === 'vi' ? 'DANH MỤC SẢN PHẨM' : 'CATEGORIES'}</span>
              <ChevronDown className={`w-3 h-3 transition-transform ${showCategoryMenu ? 'rotate-180' : ''}`} />
            </button>

            {/* Build PC Link */}
            <button
              onClick={onNavigatePCBuilder}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 text-white rounded-lg flex items-center space-x-1 cursor-pointer transition shadow-xs flex-shrink-0 font-extrabold"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 text-amber-400" />
              <span>{lang === 'vi' ? 'XÂY DỰNG CẤU HÌNH' : 'BUILD PC'}</span>
              <span className="text-[9px] bg-red-600 text-white px-1 py-0.2 rounded font-black">HOT</span>
            </button>

            {/* PC Gaming */}
            <button
              onClick={() => {
                if (onNavigateSection) {
                  onNavigateSection('section-pc-gaming');
                } else {
                  onSelectCategory('all');
                  document.getElementById('section-pc-gaming')?.scrollIntoView({ behavior: 'smooth' });
                }
              }}
              className="px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018]"
            >
              <Gamepad2 className="w-3.5 h-3.5 text-red-600" />
              <span>PC GAMING</span>
            </button>

            {/* PC Đồ Họa - AI */}
            <button
              onClick={() => {
                if (onNavigateSection) {
                  onNavigateSection('section-pc-workstation');
                } else {
                  onSelectCategory('all');
                  document.getElementById('section-pc-workstation')?.scrollIntoView({ behavior: 'smooth' });
                }
              }}
              className="px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-blue-600"
            >
              <Cpu className="w-3.5 h-3.5 text-blue-600" />
              <span>PC ĐỒ HỌA - AI</span>
            </button>

            {/* Laptop */}
            <button
              onClick={() => onSelectCategory('laptop')}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer ${
                currentCategory === 'laptop'
                  ? 'bg-red-50 dark:bg-red-950/40 text-[#d70018] dark:text-red-400'
                  : 'hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018]'
              }`}
            >
              <Laptop className="w-3.5 h-3.5 text-slate-500" />
              <span>LAPTOP CHÍNH HÃNG</span>
            </button>

            {/* Linh Kiện PC */}
            <button
              onClick={() => {
                if (onNavigateSection) {
                  onNavigateSection('section-pc-components');
                } else {
                  onSelectCategory('all');
                  document.getElementById('section-pc-components')?.scrollIntoView({ behavior: 'smooth' });
                }
              }}
              className="px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018]"
            >
              <CircuitBoard className="w-3.5 h-3.5 text-slate-500" />
              <span>LINH KIỆN MÁY TÍNH</span>
            </button>

            {/* Màn Hình */}
            <button
              onClick={() => onSelectCategory('monitor')}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer ${
                currentCategory === 'monitor'
                  ? 'bg-red-50 dark:bg-red-950/40 text-[#d70018] dark:text-red-400'
                  : 'hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018]'
              }`}
            >
              <Monitor className="w-3.5 h-3.5 text-slate-500" />
              <span>MÀN HÌNH</span>
            </button>

            {/* Khuyến Mãi */}
            <button
              onClick={() => {
                if (onNavigateSection) {
                  onNavigateSection('section-flash-sale');
                } else {
                  onSelectCategory('all');
                  window.scrollTo({ top: 400, behavior: 'smooth' });
                }
              }}
              className="px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer text-red-600 dark:text-rose-400 hover:bg-red-50 dark:hover:bg-red-950/30"
            >
              <Tag className="w-3.5 h-3.5 text-red-600" />
              <span>KHUYẾN MÃI</span>
            </button>
          </div>

          {/* Showroom Hotline callout on right */}
          <div className="hidden xl:flex items-center space-x-2 text-[11px] text-slate-500 dark:text-slate-400 font-semibold flex-shrink-0">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              <span>Hà Nội: <strong>097.111.3323</strong></span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span>TP.HCM: <strong>090.888.6623</strong></span>
            </span>
          </div>
        </div>
      </div>

      {/* 4. Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-gray-200 dark:border-slate-800 bg-white dark:bg-[#151c2c] p-4 space-y-4 shadow-xl">
          {/* Quick theme and language row for mobile */}
          <div className="flex items-center justify-between pb-3 border-b border-gray-150 dark:border-slate-800 text-xs">
            <span className="font-semibold text-slate-600 dark:text-slate-300">Cài đặt hiển thị:</span>
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleLang}
                className="px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-slate-800 font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1"
              >
                <Globe className="w-3.5 h-3.5 text-red-600" />
                <span>{lang === 'vi' ? 'Tiếng Việt' : 'English'}</span>
              </button>
              <button
                onClick={toggleTheme}
                className="px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-slate-800 font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1"
              >
                {theme === 'dark' ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-slate-700" />}
                <span>{theme === 'dark' ? 'Sáng' : 'Tối'}</span>
              </button>
            </div>
          </div>

          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder={t('searchPlaceholder')}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg text-sm text-slate-800 dark:text-slate-100"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          </form>

          <div className="grid grid-cols-2 gap-2 text-xs font-semibold">
            <button
              onClick={() => {
                onNavigateHome();
                setMobileMenuOpen(false);
              }}
              className="p-2.5 rounded-lg bg-[#d70018] text-white text-left font-bold col-span-2 flex items-center justify-between cursor-pointer shadow-xs"
            >
              <span className="flex items-center space-x-1.5">
                <Home className="w-4 h-4" />
                <span>{lang === 'vi' ? 'Về Trang Chủ (Làm Mới Toàn Bộ)' : 'Home (Reset View)'}</span>
              </span>
              <ChevronRight className="w-4 h-4" />
            </button>
            {categories.map(cat => {
              const CatIcon = cat.icon;
              return (
                <button
                  key={cat.slug}
                  onClick={() => {
                    onSelectCategory(cat.slug);
                    setMobileMenuOpen(false);
                  }}
                  className="p-2.5 rounded-lg bg-gray-50 dark:bg-slate-800/70 text-slate-800 dark:text-slate-200 text-left hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#d70018] dark:hover:text-red-400 flex items-center space-x-2"
                >
                  <CatIcon className="w-4 h-4 text-slate-500" />
                  <span className="truncate">{cat.label}</span>
                </button>
              );
            })}
            <button
              onClick={() => {
                onNavigatePCBuilder();
                setMobileMenuOpen(false);
              }}
              className="p-2.5 rounded-lg bg-slate-900 dark:bg-slate-800 text-white text-left font-bold col-span-2 flex items-center justify-between"
            >
              <span className="flex items-center space-x-1.5">
                <SlidersHorizontal className="w-4 h-4 text-amber-400" />
                <span>{t('buildPC')}</span>
              </span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
