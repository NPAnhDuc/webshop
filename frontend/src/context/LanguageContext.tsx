import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'vi' | 'en';

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  toggleLang: () => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  vi: {
    // Top marquee & Header
    hotline: 'Hotline: 1800.6868 (Miễn phí)',
    warranty: 'Bảo hành 1 đổi 1 trong 30 ngày',
    storeLocator: 'Hệ thống 120 cửa hàng toàn quốc',
    freeShipping: 'Miễn phí giao hàng hỏa tốc 2H',
    tMemberSpecial: 'Đặc quyền T-Member tích điểm đến 5%',
    
    // Navbar
    searchPlaceholder: 'Bạn cần tìm laptop, CPU, VGA hay linh kiện gì? (VD: ASUS ROG, RTX 4070...)',
    buildPC: 'Xây Dựng Cấu Hình PC',
    buildPCSub: 'Tự ráp & tương thích',
    trackOrder: 'Tra Cứu Đơn Hàng',
    trackOrderSub: 'Kiểm tra vận chuyển',
    account: 'T-Member / Quản Trị',
    accountSub: 'Ưu đãi & Đăng nhập',
    cart: 'Giỏ hàng',
    categories: 'Danh Mục Sản Phẩm',
    all: 'Tất cả sản phẩm',
    laptop: 'Laptop Văn Phòng',
    gaming: 'Laptop Gaming',
    apple: 'MacBook / Apple',
    cpu: 'Vi Xử Lý (CPU)',
    mainboard: 'Bo Mạch Chủ',
    ram: 'Bộ Nhớ RAM',
    vga: 'Card Đồ Họa (VGA)',
    ssd: 'Ổ Cứng SSD',
    psu: 'Nguồn Máy Tính (PSU)',
    case: 'Vỏ Thùng Case',
    cooler: 'Tản Nhiệt Khí/AIO',
    
    // Theme & Lang
    themeDark: 'Giao diện Tối',
    themeLight: 'Giao diện Sáng',
    langVN: 'Tiếng Việt',
    langEN: 'English',
    
    // Hero & Flash Sale
    exclusiveDeals: 'ĐẶC QUYỀN TECHSTORE',
    flashSaleTitle: 'TECHSTORE FLASH SALE CUỐI TUẦN',
    flashSaleSubtitle: 'Giá sốc sập sàn • Số lượng có hạn • Giữ hàng tự động trong 15 phút',
    endsIn: 'KẾT THÚC SAU:',
    hours: 'Giờ',
    mins: 'Phút',
    secs: 'Giây',
    buyNow: 'Mua ngay',
    sold: 'Đã bán',
    left: 'Còn',
    
    // Product Cards & Details
    tMemberPerk: 'Giảm thêm đến 500k cho T-Member & T-VIP',
    inStock: 'Còn hàng - Giao 2H',
    outOfStock: 'Tạm hết hàng',
    lowStock: 'Kho còn ít',
    savePercent: 'Tiết kiệm',
    askAIConsult: 'Hỏi AI Tư Vấn',
    compare: 'So sánh',
    addToCart: 'Thêm vào giỏ',
    specs: 'Thông số kỹ thuật',
    warrantyMonths: 'Tháng',
    oneToOneSwap: '1 đổi 1 30 ngày',
    installment0: 'Trả góp 0%',
    
    // Filters & Sorting
    filtersTitle: 'Bộ Lọc Tìm Kiếm',
    clearFilters: 'Xóa bộ lọc',
    filterBrand: 'Thương hiệu',
    filterPrice: 'Khoảng giá',
    filterDemand: 'Nhu cầu sử dụng',
    filterScreen: 'Màn hình',
    inStockOnly: 'Chỉ xem hàng có sẵn',
    filterInstallment0: 'Hỗ trợ trả góp 0%',
    sort: 'Sắp xếp:',
    sortFeatured: 'Nổi bật nhất',
    sortPriceAsc: 'Giá tăng dần',
    sortPriceDesc: 'Giá giảm dần',
    sortDiscountDesc: 'Giảm giá nhiều nhất',
    sortNewest: 'Mới nhất',
    found: 'Tìm thấy',
    productsMatch: 'sản phẩm phù hợp',
    forKeyword: 'cho từ khóa',
    noProductFound: 'Không tìm thấy sản phẩm phù hợp',
    noProductFoundSub: 'Hãy thử nới lỏng các tiêu chí bộ lọc giá, thương hiệu hoặc tìm kiếm từ khóa khác.',
    
    // PC Builder
    pcBuilderTitle: 'XÂY DỰNG CẤU HÌNH PC',
    pcBuilderSub: 'Tự tay chọn linh kiện máy tính phù hợp ngân sách, tự động kiểm tra tương thích chân cắm CPU, RAM & công suất nguồn. Miễn phí công lắp ráp, cài đặt và bảo hành 1 đổi 1 30 ngày.',
    compatible100: 'Tương thích 100%',
    presetsTitle: 'Cấu Hình Mẫu Đề Xuất (1-Click Presets)',
    presetsSub: 'Đã được kỹ thuật viên TechStore thẩm định chuẩn tương thích & công suất',
    schematicTitle: 'Sơ Đồ Linh Kiện Lắp Ráp Trực Quan',
    schematicSub: 'Nhấp trực tiếp vào ô linh kiện bên dưới để chọn hoặc đổi sản phẩm',
    compatibilityEngine: 'Hệ Thống Thẩm Định Tương Thích',
    estimatedWattage: 'Công suất tiêu thụ ước tính:',
    recommendedPSU: 'Khuyến nghị công suất nguồn:',
    totalRigPrice: 'Tổng tiền cấu hình:',
    addAllToCart: 'Thêm toàn bộ vào giỏ hàng',
    copySpecSheet: 'In báo giá / Tải PDF',
    resetRig: 'Làm mới',
    selectComponent: 'Chọn linh kiện',
    changeComponent: 'Đổi',
    required: 'Bắt buộc',
    installed: 'Đã lắp:',
    
    // Chatbot AI
    aiChatButton: 'Hỏi Trợ Lý AI',
    aiChatTitle: 'Trợ lý AI TechStore',
    aiChatSub: 'Tư vấn chọn máy & kiểm tra kho 24/7',
    aiChatPlaceholder: 'Nhập câu hỏi... (VD: laptop 20tr màn OLED, RTX 4060)',
    aiChatThinking: 'Trợ lý AI đang đối chiếu dữ liệu kho...',
    aiHumanHelp: 'Chuyển chuyên viên tư vấn',
    
    // Cart & Checkout
    cartTitle: 'Giỏ hàng của bạn',
    cartEmptyTitle: 'Giỏ hàng của bạn đang trống',
    cartEmptySub: 'Hãy dạo một vòng và chọn chiếc laptop hoặc linh kiện ưng ý nhé!',
    exploreStore: 'Khám phá sản phẩm',
    subtotal: 'Tạm tính hàng hóa:',
    shippingFee: 'Phí vận chuyển toàn quốc:',
    free100: 'Miễn phí 100%',
    totalPayment: 'Tổng thanh toán:',
    proceedOrder: 'Tiến hành đặt hàng',
    confirmOrder: 'Xác nhận đặt hàng ngay',
    codPayment: 'Thanh toán COD khi nhận',
    bankPayment: 'Chuyển khoản QR ngân hàng',
    orderSuccessTitle: 'Đặt hàng thành công!',
    orderSuccessMsg: 'Đơn hàng đã được lưu & giữ hàng trong kho. Chuyên viên TechStore sẽ gọi xác nhận trong 15 phút.',
    
    // Side Wings & Extras
    sideWingHotDeal: 'Ưu Đãi Độc Quyền',
    sideWingVoucher: 'Voucher 500K',
    sideWingBuildPC: 'Tự Ráp PC 1-Click',
    sideWingSupport: 'Hotline 1800.6868',
    sideWingChat: 'Chat cùng Bot AI',
    sideWingBackToTop: 'Lên đầu trang'
  },
  en: {
    // Top marquee & Header
    hotline: 'Hotline: 1800.6868 (Toll Free)',
    warranty: '1-to-1 replacement within 30 days',
    storeLocator: 'Over 120 stores nationwide',
    freeShipping: 'Free 2-hour express delivery',
    tMemberSpecial: 'T-Member special: Earn up to 5% rewards',
    
    // Navbar
    searchPlaceholder: 'Search laptops, CPUs, GPUs or components (e.g. ASUS ROG, RTX 4070...)',
    buildPC: 'Custom PC Builder',
    buildPCSub: 'DIY Rig & Compatibility',
    trackOrder: 'Track Your Order',
    trackOrderSub: 'Check delivery status',
    account: 'T-Member / Admin',
    accountSub: 'Perks & Sign in',
    cart: 'Cart',
    categories: 'Product Categories',
    all: 'All Products',
    laptop: 'Ultrabook & Office',
    gaming: 'Gaming Laptops',
    apple: 'MacBook / Apple',
    cpu: 'Processors (CPU)',
    mainboard: 'Motherboards',
    ram: 'RAM Memory',
    vga: 'Graphics Cards (GPU)',
    ssd: 'Solid State Drive (SSD)',
    psu: 'Power Supply (PSU)',
    case: 'PC Chassis / Case',
    cooler: 'CPU Cooler / AIO',
    
    // Theme & Lang
    themeDark: 'Dark Theme',
    themeLight: 'Light Theme',
    langVN: 'Tiếng Việt',
    langEN: 'English',
    
    // Hero & Flash Sale
    exclusiveDeals: 'TECHSTORE EXCLUSIVE PERKS',
    flashSaleTitle: 'TECHSTORE WEEKEND FLASH SALE',
    flashSaleSubtitle: 'Deep discounts • Limited quantities • 15-minute stock hold guarantee',
    endsIn: 'ENDS IN:',
    hours: 'Hours',
    mins: 'Mins',
    secs: 'Secs',
    buyNow: 'Buy Now',
    sold: 'Sold',
    left: 'Left',
    
    // Product Cards & Details
    tMemberPerk: 'Extra up to 500k discount for T-Members & VIPs',
    inStock: 'In Stock - Fast 2H Delivery',
    outOfStock: 'Out of Stock',
    lowStock: 'Low Stock',
    savePercent: 'Save',
    askAIConsult: 'Ask AI Expert',
    compare: 'Compare',
    addToCart: 'Add to Cart',
    specs: 'Specifications',
    warrantyMonths: 'Months',
    oneToOneSwap: '30-Day 1-to-1 Swap',
    installment0: '0% Interest',
    
    // Filters & Sorting
    filtersTitle: 'Filter Products',
    clearFilters: 'Clear Filters',
    filterBrand: 'Brand',
    filterPrice: 'Price Range',
    filterDemand: 'Usage Demands',
    filterScreen: 'Display Panel',
    inStockOnly: 'In Stock Only',
    filterInstallment0: '0% Installment Only',
    sort: 'Sort by:',
    sortFeatured: 'Featured',
    sortPriceAsc: 'Price: Low to High',
    sortPriceDesc: 'Price: High to Low',
    sortDiscountDesc: 'Highest Discount',
    sortNewest: 'Newest Arrivals',
    found: 'Found',
    productsMatch: 'matching products',
    forKeyword: 'for keyword',
    noProductFound: 'No matching products found',
    noProductFoundSub: 'Try loosening filter criteria or searching for different keywords.',
    
    // PC Builder
    pcBuilderTitle: 'CUSTOM PC BUILDER',
    pcBuilderSub: 'Select parts that fit your budget with automated socket, RAM, and PSU wattage checks. Free assembly, OS tuning, and 30-day 1-to-1 replacement.',
    compatible100: '100% Compatible',
    presetsTitle: 'Recommended Builds (1-Click Presets)',
    presetsSub: 'Thoroughly tested and validated by TechStore hardware engineers',
    schematicTitle: 'Visual Component Assembly Matrix',
    schematicSub: 'Click directly on any hardware slot below to select or change parts',
    compatibilityEngine: 'Compatibility Validation Engine',
    estimatedWattage: 'Estimated Power Draw:',
    recommendedPSU: 'Recommended PSU Wattage:',
    totalRigPrice: 'Total Rig Cost:',
    addAllToCart: 'Add All Components to Cart',
    copySpecSheet: 'Copy Spec Sheet / Print',
    resetRig: 'Reset Build',
    selectComponent: 'Select Part',
    changeComponent: 'Change',
    required: 'Required',
    installed: 'Installed:',
    
    // Chatbot AI
    aiChatButton: 'Ask AI Assistant',
    aiChatTitle: 'TechStore AI Assistant',
    aiChatSub: 'Real-time hardware advice & inventory check',
    aiChatPlaceholder: 'Ask anything... (e.g. 20M gaming laptop, RTX 4060)',
    aiChatThinking: 'AI Assistant is querying inventory database...',
    aiHumanHelp: 'Talk to human specialist',
    
    // Cart & Checkout
    cartTitle: 'Your Shopping Cart',
    cartEmptyTitle: 'Your cart is currently empty',
    cartEmptySub: 'Take a look around and pick the perfect laptop or PC components!',
    exploreStore: 'Explore Catalog',
    subtotal: 'Cart Subtotal:',
    shippingFee: 'Nationwide Delivery:',
    free100: '100% Free',
    totalPayment: 'Total Payment:',
    proceedOrder: 'Proceed to Checkout',
    confirmOrder: 'Confirm Order Now',
    codPayment: 'Cash on Delivery (COD)',
    bankPayment: 'Bank Transfer / QR Code',
    orderSuccessTitle: 'Order Placed Successfully!',
    orderSuccessMsg: 'Your items are reserved in stock. A TechStore specialist will contact you in 15 minutes.',
    
    // Side Wings & Extras
    sideWingHotDeal: 'Exclusive Deals',
    sideWingVoucher: 'Voucher 500K',
    sideWingBuildPC: '1-Click Rig Builder',
    sideWingSupport: 'Call 1800.6868',
    sideWingChat: 'Chat with AI',
    sideWingBackToTop: 'Back to Top'
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem('techstore_lang');
      if (saved === 'vi' || saved === 'en') return saved;
      return 'vi';
    } catch {
      return 'vi';
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('techstore_lang', lang);
    } catch (e) {
      console.error('Failed to save language in localStorage', e);
    }
  }, [lang]);

  const toggleLang = () => {
    setLangState(prev => (prev === 'vi' ? 'en' : 'vi'));
  };

  const setLang = (newLang: Language) => {
    setLangState(newLang);
  };

  const t = (key: string): string => {
    return translations[lang]?.[key] || translations['vi']?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
