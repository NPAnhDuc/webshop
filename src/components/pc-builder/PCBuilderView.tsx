import React, { useState, useEffect } from 'react';
import {
  SlidersHorizontal,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Plus,
  Trash2,
  ShoppingCart,
  Zap,
  Info,
  ArrowLeft,
  Copy,
  Check,
  Flame,
  Activity,
  Award,
  ShieldCheck,
  Wrench,
  ChevronRight,
  Eye,
  Maximize2,
  Printer,
  FileText,
  Share2,
  Sparkles,
  X
} from 'lucide-react';
import { Product } from '../../types';
import { validatePCBuild, fetchProducts, submitPCQuotation } from '../../services/api';
import { useCart } from '../../context/CartContext';
import { sound } from '../../utils/sound';

interface PCBuilderViewProps {
  onBackToHome: () => void;
  onSelectProduct: (product: Product) => void;
  onToast?: (title: string, message?: string) => void;
}

interface SlotConfig {
  key: string;
  name: string;
  categorySlug: string;
  required: boolean;
  schematicLabel: string;
  subtitle: string;
}

const SLOTS: SlotConfig[] = [
  { key: 'cpu', name: '1. Vi xử lý (CPU)', categorySlug: 'cpu', required: true, schematicLabel: 'CPU SOCKET', subtitle: 'Intel Core thế hệ 12-14th hoặc AMD Ryzen 7000/9000' },
  { key: 'mainboard', name: '2. Bo mạch chủ (Mainboard)', categorySlug: 'mainboard', required: true, schematicLabel: 'MOTHERBOARD', subtitle: 'Chipset B760, Z790, B650, X870E chuẩn ATX/mATX' },
  { key: 'ram', name: '3. Bộ nhớ trong (RAM)', categorySlug: 'ram', required: true, schematicLabel: 'DIMM SLOTS', subtitle: 'Chuẩn DDR4 / DDR5 tản nhiệt RGB hiệu năng cao' },
  { key: 'vga', name: '4. Card màn hình (VGA)', categorySlug: 'vga', required: false, schematicLabel: 'PCIe x16 GPU', subtitle: 'NVIDIA GeForce RTX 30/40/50 Series chiến game 2K/4K' },
  { key: 'ssd', name: '5. Ổ cứng (SSD NVMe)', categorySlug: 'ssd', required: true, schematicLabel: 'M.2 NVMe', subtitle: 'PCIe Gen 4x4 / Gen 5 tốc độ đọc ghi 5000-7450 MB/s' },
  { key: 'psu', name: '6. Nguồn máy tính (PSU)', categorySlug: 'psu', required: true, schematicLabel: 'POWER SUPPLY', subtitle: 'Công suất thực 650W - 850W chuẩn 80 Plus Bronze / Gold' },
  { key: 'case', name: '7. Vỏ Case Thùng Máy', categorySlug: 'case', required: true, schematicLabel: 'CHASSIS', subtitle: 'Mặt kính cường lực, kèm quạt tản nhiệt LED RGB đối lưu' },
  { key: 'cooler', name: '8. Tản nhiệt CPU', categorySlug: 'cooler', required: false, schematicLabel: 'CPU COOLER', subtitle: 'Tản tháp khí kép hoặc Tản nhiệt nước AIO 240/360mm' }
];

// Rich 1-Click Hardware Presets with REAL Case & Component Photos
const PRESETS = [
  {
    id: 'preset-esport',
    title: 'Esport Gaming 1080p Ultra',
    badge: 'Phổ Biến Nhất',
    badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    tagline: 'Chiến mượt CS2, Valorant, LMHT 300+ FPS',
    targetPrice: '21.570.000₫',
    caseImage: '/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg',
    componentImages: [
      { name: 'Core i5-12400F', img: '/images/cpu/intel-core-i5-12400f-7719e9653761.jpg' },
      { name: 'RTX 3060 12GB', img: '/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg' },
      { name: 'DDR5 16GB', img: '/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg' },
      { name: 'SSD 1TB', img: '/images/internal-hard-drive/crucial-p3-plus-64dc7f047585.jpg' }
    ],
    parts: {
      cpu: '7719e96537610f3d2ae0fac067c7809bcbca00d7b7c13b69099130fe73992cb4', // i5-12400F
      mainboard: 'ee2d7931b81ddeaeb317d9e95d25217653675002f1d27ad1719734052a4797e8', // MSI B760
      ram: '517c4a98422aebc21becdfdb794bfe83b9eff9b2d5e7c8ad960366426829742a', // Corsair 16GB DDR5
      vga: '752d9ae6e8f14d830d0e400d1b154957fb249003791d7d1709f586b5b7a199e1', // RTX 3060 12G
      ssd: '64dc7f047585e37bf0becd21f1d5d8ec58a9b06dbcb991bb0ef34edbf525163c', // Crucial P3 Plus 1TB
      psu: '3df5e885dd92eb0757698f9765403d14d45f51b9266d10dd725511772d7f4ebe', // MSI 650W Bronze
      case: '21e32cbca4b2a85c6550e75b0e2aecf5d666af461cb946e5f94f9833dc3247ca' // Montech AIR 903
    }
  },
  {
    id: 'preset-streamer',
    title: 'Streamer & Đồ Họa 2K Pro',
    badge: 'Đề Xuất Hot',
    badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
    tagline: 'AMD Zen 5 + RTX 5060 Ti 16GB OC thế hệ mới',
    targetPrice: '30.530.000₫',
    caseImage: '/images/case/nzxt-h5-flow-2024-6d80f639a090.jpg',
    componentImages: [
      { name: 'Ryzen 5 7600X', img: '/images/cpu/amd-ryzen-5-7600x-c9ab253a5d81.webp' },
      { name: 'RTX 5060 Ti 16G', img: '/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg' },
      { name: '32GB RGB DDR5', img: '/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg' },
      { name: 'Kingston 1TB', img: '/images/internal-hard-drive/kingston-nv2-cdc875d18109.jpg' }
    ],
    parts: {
      cpu: 'c9ab253a5d81db91a15166655f5abdfad3fcf5210f55424a67e41111296e620f', // Ryzen 5 7600X
      mainboard: 'c6488d4e841b7392e018b629fdd6b8c8ce461577492399eef5b7cb292af86aa6', // Asus B650 PLUS
      ram: '3d8f348c2fc4efa25e9ee48c76bb796666ad8f793845a6e6a8483fd96900eb93', // Corsair 32GB RGB DDR5
      vga: '3a40ad6ac20ca8e772a09d6f23a7eb4f24755e6c8a31f3754bb5eb897d277e2a', // RTX 5060 Ti 16G OC
      ssd: 'cdc875d18109ca5c457ea2feee66cd5cb9f055700d6d0c0cffeacb398a8ea0bd', // Kingston NV2 1TB
      psu: '3335cb6d8ee5ff7444645ea3146c243526098ee5d1a9bf95e406f666661a8a1d', // Corsair 750W Gold
      case: '6d80f639a0901679845ecc8e6c0b895d6e47f7aca628afe12b64cc06ca119438' // NZXT H5 Flow
    }
  },
  {
    id: 'preset-flagship',
    title: 'Flagship 4K Ray Tracing Master',
    badge: 'Cực Hạn Hiệu Năng',
    badgeColor: 'bg-purple-100 text-purple-800 border-purple-300',
    tagline: 'Ryzen 7 9800X3D + RTX 4070 Ti Super 16GB',
    targetPrice: '46.660.000₫',
    caseImage: '/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg',
    componentImages: [
      { name: 'Ryzen 7 9800X3D', img: '/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg' },
      { name: 'RTX 4070 Ti 16G', img: '/images/video-card/msi-rtx-4060-ti-8g-gaming-slim-monster-hunter-edition-dca21cffcb61.jpg' },
      { name: 'Trident 64GB', img: '/images/memory/teamgroup-t-force-delta-rgb-32-gb-0cce20938aae.jpg' },
      { name: 'Samsung 990 2TB', img: '/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png' }
    ],
    parts: {
      cpu: '20627684ea0548ecdaef1e6d76270b0e9c733c5c4ea267c4a099c8832f4c3215', // Ryzen 7 9800X3D
      mainboard: '7ac8293143f64b96e17d87991c1b33ff6a850b5d8a7a8c75e9bb2ed3524c7b3d', // Asus TUF B850 PLUS
      ram: '92d139676d3d197432453358850c32977d1fd7a76a2a5f83c684f62ecb16e359', // G.Skill Trident 64GB
      vga: 'fc17a74f18090fc0987486a04ce4529961a6ff56408b2576b9674d5ed8599864', // RTX 4070 Ti Super 16G
      ssd: 'b182cda76ba681d381cb42f7cd4a01b11f7b0aa88fdec3667cd7b6ab66b69a58', // Samsung 990 Pro 2TB
      psu: '3335cb6d8ee5ff7444645ea3146c243526098ee5d1a9bf95e406f666661a8a1d', // Corsair 750W Gold
      case: '349a9bcb6e003baee5b28124c6d755ef4c51d12df241ed8bddf0127f9af0c9f6' // Corsair 4000D
    }
  }
];

// Stylized Hardware Blueprint SVGs for Empty Slots
const HardwareBlueprintIcon: React.FC<{ type: string; className?: string }> = ({ type, className = 'w-14 h-14' }) => {
  switch (type) {
    case 'cpu':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="10" y="10" width="44" height="44" rx="6" stroke="#059669" strokeWidth="2.5" fill="#ecfdf5" />
          <rect x="18" y="18" width="28" height="28" rx="4" fill="#d1fae5" stroke="#059669" strokeWidth="1.5" />
          <path d="M24 24H40V40H24V24Z" fill="#059669" fillOpacity="0.2" />
          <circle cx="15" cy="15" r="1.5" fill="#059669" />
          <line x1="2" y1="22" x2="10" y2="22" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
          <line x1="2" y1="32" x2="10" y2="32" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
          <line x1="2" y1="42" x2="10" y2="42" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
          <line x1="54" y1="22" x2="62" y2="22" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
          <line x1="54" y1="32" x2="62" y2="32" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
          <line x1="54" y1="42" x2="62" y2="42" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    case 'mainboard':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="6" y="6" width="52" height="52" rx="4" stroke="#2563eb" strokeWidth="2.5" fill="#eff6ff" />
          <rect x="14" y="12" width="16" height="16" rx="2" stroke="#2563eb" strokeWidth="1.5" fill="#dbeafe" />
          <line x1="36" y1="12" x2="36" y2="32" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="42" y1="12" x2="42" y2="32" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />
          <rect x="12" y="38" width="40" height="6" rx="1.5" stroke="#2563eb" strokeWidth="1.5" fill="#bfdbfe" />
          <rect x="12" y="48" width="28" height="4" rx="1" stroke="#2563eb" strokeWidth="1" fill="#dbeafe" />
        </svg>
      );
    case 'ram':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="8" y="20" width="48" height="24" rx="3" stroke="#9333ea" strokeWidth="2.5" fill="#faf5ff" />
          <rect x="8" y="20" width="48" height="6" rx="1" fill="#c084fc" />
          <rect x="14" y="30" width="6" height="8" rx="1" fill="#a855f7" />
          <rect x="24" y="30" width="6" height="8" rx="1" fill="#a855f7" />
          <rect x="34" y="30" width="6" height="8" rx="1" fill="#a855f7" />
          <rect x="44" y="30" width="6" height="8" rx="1" fill="#a855f7" />
          <line x1="12" y1="44" x2="52" y2="44" stroke="#eab308" strokeWidth="2" strokeDasharray="3 2" />
        </svg>
      );
    case 'vga':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="6" y="16" width="52" height="32" rx="4" stroke="#059669" strokeWidth="2.5" fill="#ecfdf5" />
          <circle cx="22" cy="32" r="9" stroke="#059669" strokeWidth="2" fill="#a7f3d0" />
          <circle cx="42" cy="32" r="9" stroke="#059669" strokeWidth="2" fill="#a7f3d0" />
          <line x1="16" y1="48" x2="48" y2="48" stroke="#eab308" strokeWidth="2.5" strokeLinecap="round" />
          <rect x="2" y="20" width="4" height="16" rx="1" fill="#64748b" />
        </svg>
      );
    case 'ssd':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="8" y="24" width="48" height="16" rx="2" stroke="#0891b2" strokeWidth="2.5" fill="#ecfeff" />
          <rect x="14" y="27" width="10" height="10" rx="1" fill="#a5f3fc" />
          <rect x="28" y="27" width="10" height="10" rx="1" fill="#a5f3fc" />
          <rect x="42" y="27" width="8" height="10" rx="1" fill="#67e8f9" />
          <path d="M56 28V36" stroke="#eab308" strokeWidth="3" strokeLinecap="round" />
        </svg>
      );
    case 'psu':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="10" y="12" width="44" height="40" rx="4" stroke="#d97706" strokeWidth="2.5" fill="#fffbeb" />
          <circle cx="32" cy="32" r="14" stroke="#d97706" strokeWidth="2" fill="#fde68a" />
          <circle cx="32" cy="32" r="4" fill="#d97706" />
          <line x1="16" y1="46" x2="24" y2="46" stroke="#d97706" strokeWidth="3" strokeLinecap="round" />
          <line x1="28" y1="46" x2="36" y2="46" stroke="#d97706" strokeWidth="3" strokeLinecap="round" />
        </svg>
      );
    case 'case':
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <rect x="14" y="8" width="36" height="48" rx="4" stroke="#059669" strokeWidth="2.5" fill="#ecfdf5" />
          <rect x="18" y="14" width="28" height="36" rx="2" stroke="#059669" strokeWidth="1" strokeDasharray="3 2" fill="#d1fae5" />
          <circle cx="24" cy="22" r="4" stroke="#059669" strokeWidth="1.5" />
          <circle cx="24" cy="32" r="4" stroke="#059669" strokeWidth="1.5" />
          <circle cx="24" cy="42" r="4" stroke="#059669" strokeWidth="1.5" />
        </svg>
      );
    default:
      return (
        <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
          <circle cx="32" cy="32" r="18" stroke="#059669" strokeWidth="2.5" fill="#ecfdf5" />
          <circle cx="32" cy="32" r="8" fill="#059669" />
          <path d="M32 18V24M32 40V46M18 32H24M40 32H46" stroke="#059669" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
  }
};

export const PCBuilderView: React.FC<PCBuilderViewProps> = ({ onBackToHome, onSelectProduct, onToast }) => {
  const { addToCart } = useCart();
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [selectedParts, setSelectedParts] = useState<Record<string, Product>>({});
  const [validationResult, setValidationResult] = useState<any>(null);
  const [activeSlot, setActiveSlot] = useState<SlotConfig | null>(null);
  const [availableProducts, setAvailableProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activePresetId, setActivePresetId] = useState<string | null>(null);
  const [showQuoteModal, setShowQuoteModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerNote, setCustomerNote] = useState('');
  const [submittingQuote, setSubmittingQuote] = useState(false);
  const [submittedQuoteId, setSubmittedQuoteId] = useState<string | null>(null);
  const [gameResolution, setGameResolution] = useState<'1080p' | '1440p' | '4k'>('1080p');

  const handleSubmitQuotation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName.trim() || !customerPhone.trim()) return;
    setSubmittingQuote(true);

    try {
      const partsList = Object.entries(selectedParts).map(([slotKey, prod]) => ({
        type: slotKey.toUpperCase(),
        name: prod.name,
        price: prod.price
      }));

      const res = await submitPCQuotation({
        customerName: customerName.trim(),
        phone: customerPhone.trim(),
        title: `Cấu hình PC Custom (${Object.keys(selectedParts).length} linh kiện)`,
        totalPrice,
        totalWatts: validationResult?.estimatedWattage || 450,
        recommendedPsu: validationResult?.recommendedPsu || '650W',
        compatibilityScore: validationResult?.compatibilityScore || 100,
        parts: partsList,
        note: customerNote.trim()
      });

      if (res.success && res.data) {
        setSubmittedQuoteId(res.data.id);
        sound.playVoucherSuccess();
      }
    } catch (err) {
      console.error(err);
      alert('Không thể gửi yêu cầu báo giá, vui lòng thử lại.');
    } finally {
      setSubmittingQuote(false);
    }
  };

  // Load all products in cache on mount
  useEffect(() => {
    fetchProducts({ limit: 100 })
      .then(res => {
        if (res.products) {
          setAllProducts(res.products);
        }
      })
      .catch(err => console.error('Failed to load builder inventory:', err));
  }, []);

  // Validate whenever parts change
  useEffect(() => {
    const partsPayload: Record<string, string> = {};
    Object.entries(selectedParts).forEach(([k, prod]) => {
      if (prod) partsPayload[k] = prod.id;
    });

    validatePCBuild(partsPayload)
      .then(res => setValidationResult(res))
      .catch(err => console.error(err));
  }, [selectedParts]);

  // Load a 1-click Hardware Preset
  const handleApplyPreset = (preset: typeof PRESETS[0]) => {
    setActivePresetId(preset.id);
    const newSelected: Record<string, Product> = {};

    Object.entries(preset.parts).forEach(([slotKey, productId]) => {
      const match = allProducts.find(p => p.id === productId);
      if (match) {
        newSelected[slotKey] = match;
      }
    });

    setSelectedParts(newSelected);
    if (onToast) {
      onToast(`Đã nạp cấu hình: ${preset.title}`, `Tổng ngân sách: ${preset.targetPrice}`);
    }
  };

  const handleOpenSlot = (slot: SlotConfig) => {
    setActiveSlot(slot);
    setLoadingProducts(true);

    const filtered = allProducts.filter(p => p.categorySlug === slot.categorySlug);
    if (filtered.length > 0) {
      setAvailableProducts(filtered);
      setLoadingProducts(false);
    } else {
      fetchProducts({ category: slot.categorySlug, limit: 20 })
        .then(res => setAvailableProducts(res.products || []))
        .catch(err => console.error(err))
        .finally(() => setLoadingProducts(false));
    }
  };

  const handleSelectPart = (product: Product) => {
    if (!activeSlot) return;
    setActivePresetId(null);
    setSelectedParts(prev => ({
      ...prev,
      [activeSlot.key]: product
    }));
    setActiveSlot(null);
    if (onToast) {
      onToast(`Đã gắn ${activeSlot.name}`, product.name);
    }
  };

  const handleRemovePart = (key: string) => {
    setActivePresetId(null);
    setSelectedParts(prev => {
      const copy = { ...prev };
      delete copy[key];
      return copy;
    });
  };

  const handleResetAll = () => {
    setActivePresetId(null);
    setSelectedParts({});
    if (onToast) {
      onToast('Đã làm mới cấu hình', 'Bạn có thể chọn lại từ đầu hoặc nạp cấu hình mẫu');
    }
  };

  const handleAddAllToCart = () => {
    Object.values(selectedParts).forEach(prod => {
      addToCart(prod);
    });
    if (onToast) {
      onToast('Đã thêm toàn bộ linh kiện vào giỏ hàng!', `${Object.keys(selectedParts).length} linh kiện sẵn sàng`);
    }
  };

  const handleCopySpecSheet = () => {
    const lines = [
      '🖥️ TECHSTORE STUDIO - BẢNG BÁO GIÁ CẤU HÌNH PC CHÍNH HÃNG:',
      '======================================================',
      ...Object.entries(selectedParts).map(([key, prod]) => {
        const slot = SLOTS.find(s => s.key === key);
        return `• ${slot?.name || key}: ${prod.name} (${new Intl.NumberFormat('vi-VN').format(prod.price)}₫)`;
      }),
      '======================================================',
      `💰 Tổng chi phí: ${new Intl.NumberFormat('vi-VN').format(totalPrice)}₫`,
      `⚡ Công suất tiêu thụ ước tính: ${validationResult?.estimatedWattage || 100}W`,
      `🔌 Khuyến nghị công suất nguồn tối thiểu: ${validationResult?.recommendedWattage || 500}W`,
      '🛡️ 1 Đổi 1 trong 30 ngày • Miễn phí lắp ráp & vệ sinh máy trọn đời',
      '🌐 TechStore Studio | Hotline miễn phí: 1800.6868'
    ];

    navigator.clipboard.writeText(lines.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
    if (onToast) {
      onToast('Đã sao chép cấu hình!', 'Bạn có thể gửi chia sẻ hoặc in báo giá');
    }
  };

  const totalPrice = Object.values(selectedParts).reduce((sum, p) => sum + p.price, 0);
  const errors = validationResult?.issues?.filter((i: any) => i.type === 'error') || [];
  const warnings = validationResult?.issues?.filter((i: any) => i.type === 'warning') || [];

  const hasVga = !!selectedParts['vga'];
  const hasCpu = !!selectedParts['cpu'];
  const vgaName = selectedParts['vga']?.name || '';
  const isHighEndVga = vgaName.includes('4070') || vgaName.includes('5060');

  const getRobotMessage = () => {
    const count = Object.keys(selectedParts).length;
    if (count === 0) {
      return 'Chào bạn! Hãy bấm chọn 1 trong 3 cỗ máy gaming mẫu bên dưới hoặc nhấp vào từng ô linh kiện để tự ráp nhé!';
    }
    if (errors.length > 0) {
      return `Ôi có ${errors.length} điểm xung đột chân cắm! Bot đã đánh dấu đỏ bên phải, bạn nhấp vào để đổi linh kiện phù hợp nha!`;
    }
    if (count < 4) {
      return `Đang lên cấu hình rất tốt! Đã gắn ${count}/8 linh kiện. Đừng quên chọn thêm Card đồ họa (VGA) để chơi game mượt nhé!`;
    }
    if (isHighEndVga) {
      return 'Quái vật đồ họa đã sẵn sàng! Cấu hình này chiến mượt Black Myth Wukong & Cyberpunk 2077 Ultra Ray Tracing cực đỉnh!';
    }
    return 'Cấu hình tương thích 100%! Socket chuẩn, công suất nguồn dồi dào. Đội kỹ thuật TechStore sẵn sàng lắp ráp ngay!';
  };

  const getGameFps = () => {
    if (!hasVga) {
      return {
        cs2: { fps: '60 FPS', pct: 20, note: 'Đồ họa tích hợp' },
        wukong: { fps: '< 25 FPS', pct: 15, note: 'Giật lag' },
        cyberpunk: { fps: '< 20 FPS', pct: 12, note: 'Khó chơi' },
        gta5: { fps: '45 FPS', pct: 35, note: 'Low Setting' }
      };
    }

    if (gameResolution === '1080p') {
      return {
        cs2: { fps: isHighEndVga ? '420+ FPS' : '280+ FPS', pct: 95, note: 'Siêu mượt 240Hz' },
        wukong: { fps: isHighEndVga ? '110 FPS' : '75 FPS', pct: isHighEndVga ? 85 : 68, note: 'High Setting' },
        cyberpunk: { fps: isHighEndVga ? '95 FPS' : '65 FPS', pct: isHighEndVga ? 80 : 60, note: 'Ray Tracing' },
        gta5: { fps: isHighEndVga ? '180 FPS' : '135 FPS', pct: 90, note: 'Max Setting' }
      };
    } else if (gameResolution === '1440p') {
      return {
        cs2: { fps: isHighEndVga ? '310 FPS' : '190 FPS', pct: isHighEndVga ? 85 : 70, note: 'Màn 2K 165Hz' },
        wukong: { fps: isHighEndVga ? '85 FPS' : '55 FPS', pct: isHighEndVga ? 72 : 50, note: 'DLSS Quality' },
        cyberpunk: { fps: isHighEndVga ? '75 FPS' : '48 FPS', pct: isHighEndVga ? 68 : 45, note: 'Ultra RT' },
        gta5: { fps: isHighEndVga ? '135 FPS' : '90 FPS', pct: isHighEndVga ? 80 : 65, note: '2K Sắc nét' }
      };
    } else {
      return {
        cs2: { fps: isHighEndVga ? '180 FPS' : '110 FPS', pct: isHighEndVga ? 70 : 50, note: '4K sắc sảo' },
        wukong: { fps: isHighEndVga ? '60 FPS' : '35 FPS', pct: isHighEndVga ? 55 : 32, note: 'DLSS Performance' },
        cyberpunk: { fps: isHighEndVga ? '52 FPS' : '30 FPS', pct: isHighEndVga ? 48 : 28, note: 'DLSS 3.5' },
        gta5: { fps: isHighEndVga ? '90 FPS' : '55 FPS', pct: isHighEndVga ? 65 : 45, note: '4K Chân thực' }
      };
    }
  };

  const caseProduct = selectedParts['case'];
  const currentCaseImage = caseProduct?.imageUrl || '/images/case/nzxt-h5-flow-2024-6d80f639a090.jpg';

  return (
    <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 sm:px-6 py-6 space-y-6 text-slate-800 dark:text-slate-100 transition-colors">
      {/* 1. Header (TechStore Light & Dark Theme with Emerald Accent) */}
      <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="space-y-2 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={onBackToHome}
                className="inline-flex items-center space-x-1 text-xs text-[#d70018] dark:text-red-400 hover:underline font-bold transition pr-3 border-r border-gray-200 dark:border-slate-700 cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Trang chủ</span>
              </button>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-[#d70018] dark:text-red-400 border border-emerald-200 dark:border-emerald-800">
                <span className="w-2 h-2 rounded-full bg-[#059669] animate-pulse" />
                <span>TECHSTORE BUILD PC • TỰ RÁP MÁY THEO NHU CẦU</span>
              </div>
            </div>

            <h1 className="text-xl sm:text-2xl lg:text-3xl font-black tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
              <span>XÂY DỰNG CẤU HÌNH PC</span>
              <span className="text-xs px-2 py-0.5 rounded bg-yellow-400 text-slate-950 font-black uppercase tracking-wider hidden sm:inline-block">
                Tương thích 100%
              </span>
            </h1>

            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Tự tay chọn linh kiện máy tính phù hợp ngân sách, tự động kiểm tra tương thích chân cắm CPU, RAM & công suất nguồn. Miễn phí công lắp ráp, cài đặt và bảo hành 1 đổi 1 30 ngày.
            </p>

            {/* TechStore Perks */}
            <div className="pt-1 flex flex-wrap items-center gap-3 text-[11px] text-slate-600 dark:text-slate-400 font-medium">
              <span className="flex items-center space-x-1 text-emerald-600 dark:text-red-400">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Bảo hành 1 đổi 1 30 ngày</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1 text-[#d70018] dark:text-red-400">
                <Wrench className="w-3.5 h-3.5" />
                <span>Miễn phí ráp máy & vệ sinh trọn đời</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1 text-blue-600">
                <Award className="w-3.5 h-3.5" />
                <span>Trả góp 0% duyệt 15 phút</span>
              </span>
            </div>
          </div>

          {/* Quick Action Toolbar */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-2 flex-shrink-0">
            <button
              onClick={handleCopySpecSheet}
              disabled={Object.keys(selectedParts).length === 0}
              className="px-3 py-2 rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold transition flex items-center space-x-1.5 disabled:opacity-40 shadow-xs cursor-pointer"
              title="Sao chép danh sách linh kiện dạng text để gửi bạn bè"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-600 dark:text-red-400" /> : <Copy className="w-4 h-4 text-slate-500" />}
              <span>{copied ? 'Đã sao chép' : 'Sao chép cấu hình'}</span>
            </button>

            <button
              onClick={() => {
                setShowQuoteModal(true);
                sound.playPop();
              }}
              disabled={Object.keys(selectedParts).length === 0}
              className="px-3.5 py-2 rounded-xl border border-emerald-300 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-950/50 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-[#d70018] dark:text-red-400 text-xs font-bold transition flex items-center space-x-1.5 disabled:opacity-40 shadow-xs cursor-pointer"
              title="Mở giao diện in bảng báo giá chính hãng TechStore có mã & dấu mộc"
            >
              <Printer className="w-4 h-4 text-[#d70018] dark:text-red-400" />
              <span>In báo giá / Tải PDF</span>
            </button>

            <button
              onClick={() => {
                setShowSubmitModal(true);
                setSubmittedQuoteId(null);
                sound.playPop();
              }}
              disabled={Object.keys(selectedParts).length === 0}
              className="px-3.5 py-2 rounded-xl border border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-950/50 hover:bg-blue-100 text-blue-700 dark:text-blue-300 text-xs font-bold transition flex items-center space-x-1.5 disabled:opacity-40 shadow-xs cursor-pointer"
              title="Gửi cấu hình này đến kỹ thuật viên TechStore để kiểm tra và nhận báo giá ưu đãi"
            >
              <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Gửi Báo Giá Cho Kỹ Thuật</span>
            </button>

            <button
              onClick={handleResetAll}
              disabled={Object.keys(selectedParts).length === 0}
              className="px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 hover:bg-gray-100 text-slate-600 text-xs font-semibold transition disabled:opacity-40"
            >
              Làm mới
            </button>

            <button
              onClick={handleAddAllToCart}
              disabled={Object.keys(selectedParts).length === 0 || errors.length > 0}
              className="px-4 py-2 bg-[#d70018] hover:bg-[#b91c1c] disabled:opacity-40 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-sm active:scale-95"
            >
              <ShoppingCart className="w-4 h-4" />
              <span>Thêm vào giỏ ({new Intl.NumberFormat('vi-VN').format(totalPrice)}₫)</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Virtual Rig Showcase Chamber (Clean Light & Obsidian Dark Pedestal) */}
      <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xs">
        <div className="flex flex-col lg:flex-row items-center gap-6">
          {/* Left: Case Photo Preview */}
          <div className="w-full lg:w-2/5 flex flex-col items-center justify-center">
            <div className="relative w-64 h-80 sm:w-72 sm:h-88 rounded-2xl bg-gray-50 dark:bg-slate-900/80 border border-gray-200 dark:border-slate-800 p-4 shadow-inner flex flex-col items-center justify-center overflow-hidden group">
              <img
                src={currentCaseImage}
                alt="Case Preview"
                className="max-h-60 sm:max-h-68 object-contain drop-shadow-md transition-transform duration-500 group-hover:scale-105"
              />

              {/* Status Badge on Case */}
              <div className="absolute bottom-2.5 left-2.5 right-2.5 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xs rounded-xl p-2 border border-gray-200 dark:border-slate-700 text-center shadow-xs">
                <span className="text-[9px] text-[#d70018] dark:text-red-400 font-bold block uppercase tracking-wider">THÙNG MÁY CHÍNH HÃNG</span>
                <span className="text-xs font-bold text-slate-800 dark:text-slate-100 truncate block">
                  {caseProduct?.name || 'Vỏ Case NZXT H5 Flow / Corsair 4000D'}
                </span>
              </div>

              {/* Click to change case button */}
              <button
                onClick={() => handleOpenSlot(SLOTS.find(s => s.key === 'case')!)}
                className="absolute top-2.5 right-2.5 p-1.5 bg-white dark:bg-slate-800 hover:bg-[#059669] dark:hover:bg-emerald-600 hover:text-white text-slate-600 dark:text-slate-300 rounded-lg border border-gray-200 dark:border-slate-700 text-xs transition shadow-xs cursor-pointer"
                title="Đổi Vỏ Case"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 font-mono">
              ★ Đã lắp: <strong className="text-[#d70018] dark:text-red-400 font-bold">{Object.keys(selectedParts).length}/8</strong> linh kiện
            </p>
          </div>

          {/* Right: Quick Matrix Inside the Rig */}
          <div className="w-full lg:w-3/5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-150 dark:border-slate-800">
              <div>
                <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-1.5">
                  <Zap className="w-4 h-4 text-amber-500 fill-amber-500" />
                  <span>Sơ Đồ Linh Kiện Lắp Ráp Trực Quan</span>
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Nhấp trực tiếp vào ô linh kiện bên dưới để chọn hoặc đổi sản phẩm
                </p>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-emerald-50 dark:bg-emerald-950/60 text-[#d70018] dark:text-red-400 border border-emerald-200 dark:border-emerald-800 font-bold font-mono">
                {new Intl.NumberFormat('vi-VN').format(totalPrice)}₫
              </span>
            </div>

            {/* 8 Component Slots */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {SLOTS.map(slot => {
                const part = selectedParts[slot.key];
                return (
                  <div
                    key={slot.key}
                    onClick={() => handleOpenSlot(slot)}
                    className={`p-2.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between h-26 group relative overflow-hidden ${
                      part
                        ? 'bg-emerald-50/50 dark:bg-emerald-950/40 border-[#d70018] dark:border-emerald-500 shadow-xs'
                        : 'bg-gray-50 dark:bg-slate-800/60 border-gray-200 dark:border-slate-700/80 hover:border-gray-300 dark:hover:border-slate-600 hover:bg-white dark:hover:bg-slate-800'
                    }`}
                  >
                    {/* Header: Label + LED */}
                    <div className="flex items-center justify-between z-10">
                      <span className="text-[9px] font-mono font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider group-hover:text-[#d70018] dark:group-hover:text-emerald-400 transition">
                        {slot.schematicLabel}
                      </span>
                      <span className={`w-2 h-2 rounded-full ${part ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300 dark:bg-slate-600'}`} />
                    </div>

                    {/* Middle: Product Image or Blueprint */}
                    <div className="my-auto flex items-center justify-center">
                      {part ? (
                        <img
                          src={part.imageUrl}
                          alt={part.name}
                          className="w-11 h-11 object-contain drop-shadow-xs group-hover:scale-105 transition-transform"
                        />
                      ) : (
                        <div className="opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all">
                          <HardwareBlueprintIcon type={slot.key} className="w-8 h-8" />
                        </div>
                      )}
                    </div>

                    {/* Bottom: Name & Price */}
                    <div className="z-10">
                      {part ? (
                        <div>
                          <p className="text-[10px] font-bold text-slate-800 dark:text-slate-100 truncate">{part.name}</p>
                          <p className="text-[10px] text-[#d70018] dark:text-red-400 font-bold font-mono">
                            {new Intl.NumberFormat('vi-VN').format(part.price)}₫
                          </p>
                        </div>
                      ) : (
                        <p className="text-[10px] text-slate-500 dark:text-slate-400 group-hover:text-[#d70018] dark:group-hover:text-emerald-400 font-bold flex items-center justify-center space-x-1 transition">
                          <Plus className="w-3 h-3" />
                          <span>Chọn {slot.name.split(' ')[1] || 'ngay'}</span>
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* 3. 1-Click Hardware Presets Bar (TechStore Clean Cards) */}
      <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-3.5">
        <div className="flex items-center justify-between pb-2 border-b border-gray-150 dark:border-slate-800">
          <div className="flex items-center space-x-2">
            <Flame className="w-5 h-5 text-amber-500 fill-amber-500" />
            <div>
              <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                Cấu Hình Mẫu Đề Xuất (1-Click Presets)
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Đã được kỹ thuật viên TechStore thẩm định chuẩn tương thích & công suất
              </p>
            </div>
          </div>
          <span className="text-[11px] text-emerald-600 dark:text-red-400 font-bold hidden sm:inline-block">
            ✓ Trả góp 0% duyệt 15P
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {PRESETS.map(preset => {
            const isActive = activePresetId === preset.id;
            return (
              <div
                key={preset.id}
                onClick={() => handleApplyPreset(preset)}
                className={`p-3.5 rounded-2xl border-2 transition-all cursor-pointer flex flex-col justify-between group relative overflow-hidden ${
                  isActive
                    ? 'border-[#d70018] dark:border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/30 shadow-md ring-2 ring-emerald-100 dark:ring-emerald-900/40'
                    : 'border-gray-200 dark:border-slate-700/80 hover:border-gray-300 dark:hover:border-slate-600 bg-white dark:bg-[#151c2c] hover:shadow-xs'
                }`}
              >
                <div>
                  {/* Top Badge & Target Price */}
                  <div className="flex items-center justify-between mb-2.5">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${preset.badgeColor} dark:bg-opacity-20`}>
                      {preset.badge}
                    </span>
                    <span className="text-sm font-black text-[#d70018] dark:text-red-400 font-mono">
                      {preset.targetPrice}
                    </span>
                  </div>

                  {/* Preset Visual Showcase */}
                  <div className="flex items-center space-x-3 bg-gray-50 dark:bg-slate-900/60 p-2.5 rounded-xl border border-gray-150 dark:border-slate-800 mb-2.5">
                    <img
                      src={preset.caseImage}
                      alt={preset.title}
                      className="w-14 h-14 object-contain flex-shrink-0 group-hover:scale-105 transition-transform"
                    />
                    <div className="flex-1 min-w-0">
                      <span className="text-[9px] text-slate-400 dark:text-slate-500 block font-mono font-bold">LINH KIỆN NỔI BẬT</span>
                      <div className="flex items-center space-x-1 mt-1 overflow-x-auto scrollbar-none">
                        {preset.componentImages.map((comp, cIdx) => (
                          <div key={cIdx} className="w-7 h-7 rounded-lg bg-white dark:bg-slate-800 p-0.5 border border-gray-200 dark:border-slate-700 flex-shrink-0" title={comp.name}>
                            <img src={comp.img} alt={comp.name} className="w-full h-full object-contain" />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Title & Tagline */}
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-[#d70018] dark:group-hover:text-emerald-400 transition">
                    {preset.title}
                  </h4>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-snug">
                    {preset.tagline}
                  </p>
                </div>

                <div className="mt-3 pt-2.5 border-t border-gray-150 dark:border-slate-800 flex items-center justify-between text-[11px] font-bold text-[#d70018] dark:text-red-400">
                  <span>{isActive ? '✓ Đang áp dụng' : 'Nạp cấu hình này'}</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. Professional Hardware Diagnostics & Live Gaming Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Technical Inspection Diagnostic Box */}
        <div className="lg:col-span-1 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs flex flex-col justify-between space-y-2.5">
          <div className="flex items-center justify-between pb-2 border-b border-gray-150 dark:border-slate-800 text-xs">
            <div className="flex items-center space-x-1.5 font-bold text-slate-900 dark:text-slate-100">
              <ShieldCheck className="w-4 h-4 text-[#d70018] dark:text-red-400" />
              <span>Thẩm Định Kỹ Thuật Phần Cứng</span>
            </div>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
              errors.length > 0
                ? 'bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300'
                : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
            }`}>
              {errors.length > 0 ? `${errors.length} Lỗi chân cắm` : 'Khớp 100%'}
            </span>
          </div>

          <div className="text-xs text-slate-600 dark:text-slate-300 bg-gray-50 dark:bg-slate-900/60 p-2.5 rounded-xl border border-gray-200 dark:border-slate-700/80 leading-relaxed font-medium">
            "{getRobotMessage()}"
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-1">
            <span>Kiểm tra: <strong>Socket CPU • RAM Type • TDP</strong></span>
            <span className="text-[#d70018] dark:text-red-400 font-bold">Kỹ thuật TechStore</span>
          </div>
        </div>

        {/* Live Gaming Telemetry Bar */}
        <div className="lg:col-span-2 bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-gray-150 dark:border-slate-800 gap-2 text-xs">
            <span className="font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-1.5">
              <Activity className="w-3.5 h-3.5 text-amber-500" />
              <span>Ước Tính Hiệu Năng Thực Chiến (Live Gaming Telemetry)</span>
            </span>

            {/* Resolution Switcher */}
            <div className="flex items-center space-x-1 bg-gray-100 dark:bg-slate-800 p-0.5 rounded-lg border border-gray-200 dark:border-slate-700 self-start sm:self-auto">
              {(['1080p', '1440p', '4k'] as const).map(res => (
                <button
                  key={res}
                  onClick={() => {
                    setGameResolution(res);
                    sound.playClick();
                  }}
                  className={`px-2 py-0.5 rounded text-[10px] font-bold transition cursor-pointer ${
                    gameResolution === res
                      ? 'bg-[#059669] text-white shadow-2xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  {res === '1080p' ? 'Full HD (1080p)' : res === '1440p' ? '2K (1440p)' : '4K Ultra'}
                </button>
              ))}
            </div>
          </div>

          {/* 4 Games Metric Cards with Animated Visual Progress Bars */}
          {(() => {
            const fpsData = getGameFps();
            return (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="bg-gray-50 dark:bg-slate-900/60 p-2.5 rounded-xl border border-gray-200 dark:border-slate-700/80 text-left space-y-1">
                  <div className="flex justify-between items-center text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                    <span>CS2 / Valorant</span>
                    <span className="text-[9px] text-emerald-600 dark:text-red-400 font-bold">{fpsData.cs2.note}</span>
                  </div>
                  <span className="text-base font-black text-emerald-600 dark:text-red-400 font-mono block">
                    {fpsData.cs2.fps}
                  </span>
                  <div className="w-full bg-gray-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${fpsData.cs2.pct}%` }} />
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-slate-900/60 p-2.5 rounded-xl border border-gray-200 dark:border-slate-700/80 text-left space-y-1">
                  <div className="flex justify-between items-center text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                    <span>Black Myth Wukong</span>
                    <span className="text-[9px] text-sky-600 dark:text-sky-400 font-bold">{fpsData.wukong.note}</span>
                  </div>
                  <span className="text-base font-black text-sky-600 dark:text-sky-400 font-mono block">
                    {fpsData.wukong.fps}
                  </span>
                  <div className="w-full bg-gray-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-sky-500 h-full rounded-full transition-all duration-500" style={{ width: `${fpsData.wukong.pct}%` }} />
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-slate-900/60 p-2.5 rounded-xl border border-gray-200 dark:border-slate-700/80 text-left space-y-1">
                  <div className="flex justify-between items-center text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                    <span>Cyberpunk 2077</span>
                    <span className="text-[9px] text-purple-600 dark:text-purple-400 font-bold">{fpsData.cyberpunk.note}</span>
                  </div>
                  <span className="text-base font-black text-purple-600 dark:text-purple-400 font-mono block">
                    {fpsData.cyberpunk.fps}
                  </span>
                  <div className="w-full bg-gray-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-purple-500 h-full rounded-full transition-all duration-500" style={{ width: `${fpsData.cyberpunk.pct}%` }} />
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-slate-900/60 p-2.5 rounded-xl border border-gray-200 dark:border-slate-700/80 text-left space-y-1">
                  <div className="flex justify-between items-center text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                    <span>GTA V / Forza 5</span>
                    <span className="text-[9px] text-amber-600 dark:text-amber-400 font-bold">{fpsData.gta5.note}</span>
                  </div>
                  <span className="text-base font-black text-amber-600 dark:text-amber-400 font-mono block">
                    {fpsData.gta5.fps}
                  </span>
                  <div className="w-full bg-gray-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full rounded-full transition-all duration-500" style={{ width: `${fpsData.gta5.pct}%` }} />
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      </div>

      {/* 5. Main Component Selection Rows (Left) & Real-time Compatibility Matrix (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: 8 Slots Rows With LARGE Product Imagery */}
        <div className="lg:col-span-2 space-y-3">
          {SLOTS.map(slot => {
            const selected = selectedParts[slot.key];

            return (
              <div
                key={slot.key}
                className={`bg-white dark:bg-[#151c2c] rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all shadow-xs border ${
                  selected
                    ? 'border-gray-200 dark:border-slate-800 shadow-xs'
                    : 'border-gray-200 dark:border-slate-800/80 hover:border-gray-300 dark:hover:border-slate-700'
                }`}
              >
                {/* Product Thumbnail / Blueprint Icon */}
                <div className="flex items-center space-x-3.5 flex-1 min-w-0">
                  <div className="w-16 h-16 rounded-xl bg-gray-50 dark:bg-slate-900/60 border border-gray-200 dark:border-slate-700/80 flex items-center justify-center p-1.5 flex-shrink-0 overflow-hidden relative">
                    {selected ? (
                      <img
                        src={selected.imageUrl}
                        alt={selected.name}
                        className="w-full h-full object-contain"
                      />
                    ) : (
                      <HardwareBlueprintIcon type={slot.key} className="w-10 h-10" />
                    )}
                  </div>

                  {/* Slot Details */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">{slot.name}</h4>
                      {slot.required && (
                        <span className="text-[10px] text-[#d70018] dark:text-red-400 font-bold">*Bắt buộc</span>
                      )}
                    </div>

                    {selected ? (
                      <div className="mt-1 space-y-1">
                        <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-slate-200 line-clamp-1">
                          {selected.name}
                        </p>
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="text-sm font-black text-[#d70018] dark:text-red-400 font-mono">
                            {new Intl.NumberFormat('vi-VN').format(selected.price)}₫
                          </span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold">
                            {selected.brandName}
                          </span>
                          {selected.specs.socket && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/60 font-medium">
                              {selected.specs.socket}
                            </span>
                          )}
                          {selected.specs.ram_type && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-900/60 font-medium">
                              {selected.specs.ram_type}
                            </span>
                          )}
                          {selected.specs.vram_gb && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-900/60 font-medium">
                              {selected.specs.vram_gb}GB VRAM
                            </span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                        {slot.subtitle}
                      </p>
                    )}
                  </div>
                </div>

                {/* Slot Action Buttons */}
                <div className="flex items-center space-x-2 self-end sm:self-auto flex-shrink-0">
                  {selected ? (
                    <>
                      <button
                        onClick={() => handleOpenSlot(slot)}
                        className="px-3 py-1.5 border border-gray-200 dark:border-slate-700 hover:border-[#d70018] dark:hover:border-emerald-500 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-[#d70018] dark:hover:text-emerald-400 rounded-xl transition bg-gray-50 dark:bg-slate-800 hover:bg-emerald-50 dark:hover:bg-slate-700 cursor-pointer"
                      >
                        Đổi
                      </button>
                      <button
                        onClick={() => handleRemovePart(slot.key)}
                        className="p-1.5 text-slate-400 dark:text-slate-500 hover:text-red-600 dark:hover:text-red-400 transition rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 cursor-pointer"
                        title="Gỡ bỏ"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleOpenSlot(slot)}
                      className="px-3.5 py-2 bg-[#d70018] hover:bg-[#b91c1c] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition active:scale-95 shadow-xs cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Chọn linh kiện</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Compatibility Engine & Power Specs */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-4 sticky top-20">
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-1.5">
              <Zap className="w-4 h-4 text-amber-500 fill-amber-500" />
              <span>Hệ Thống Thẩm Định Tương Thích</span>
            </h3>

            {errors.length > 0 ? (
              <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 rounded-xl p-3.5 space-y-2 text-xs">
                <div className="flex items-center space-x-1.5 font-bold text-red-600 dark:text-red-400">
                  <XCircle className="w-4 h-4" />
                  <span>Phát hiện xung đột chân cắm ({errors.length}):</span>
                </div>
                <ul className="space-y-1 text-red-700 dark:text-red-300 pl-4 list-disc text-[11px]">
                  {errors.map((e: any, idx: number) => (
                    <li key={idx} className="leading-relaxed">
                      {e.message}
                    </li>
                  ))}
                </ul>
              </div>
            ) : warnings.length > 0 ? (
              <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 rounded-xl p-3.5 space-y-2 text-xs">
                <div className="flex items-center space-x-1.5 font-bold text-amber-800 dark:text-amber-300">
                  <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                  <span>Lưu ý khuyến nghị ({warnings.length}):</span>
                </div>
                <ul className="space-y-1 text-amber-800/90 dark:text-amber-300/90 pl-4 list-disc text-[11px]">
                  {warnings.map((w: any, idx: number) => (
                    <li key={idx} className="leading-relaxed">
                      {w.message}
                    </li>
                  ))}
                </ul>
              </div>
            ) : Object.keys(selectedParts).length > 0 ? (
              <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-xl p-3.5 flex items-start space-x-2 text-xs text-emerald-800 dark:text-emerald-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold">Cấu hình tương thích 100%</p>
                  <p className="text-[11px] text-emerald-700 dark:text-red-400 mt-0.5 leading-relaxed">
                    Khớp chân Socket CPU, chuẩn RAM, kích thước vỏ case và công suất nguồn đáp ứng dồi dào.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 dark:bg-slate-800/60 border border-gray-200 dark:border-slate-700 rounded-xl p-3 text-xs text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                <Info className="w-4 h-4 text-slate-400" />
                <span>Hãy chọn linh kiện hoặc nạp cấu hình mẫu để thẩm định.</span>
              </div>
            )}

            {/* Wattage Calculator */}
            <div className="pt-2 border-t border-gray-150 dark:border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between items-center text-slate-600 dark:text-slate-400">
                <span>Công suất tiêu thụ ước tính:</span>
                <span className="font-bold text-slate-900 dark:text-slate-100 font-mono">{validationResult?.estimatedWattage || 100}W</span>
              </div>
              <div className="flex justify-between items-center text-slate-600 dark:text-slate-400">
                <span>Khuyến nghị công suất nguồn:</span>
                <span className="font-bold text-[#d70018] dark:text-red-400 font-mono">{validationResult?.recommendedWattage || 500}W</span>
              </div>
              <div className="w-full bg-gray-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-[#059669] dark:bg-emerald-500 h-full rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, ((validationResult?.estimatedWattage || 100) / 850) * 100)}%` }}
                />
              </div>
            </div>

            {/* Total Price Summary */}
            <div className="pt-3 border-t border-gray-150 dark:border-slate-800 space-y-3">
              <div className="flex items-baseline justify-between">
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Tổng tiền cấu hình:</span>
                <span className="text-xl sm:text-2xl font-black text-[#d70018] dark:text-red-400 font-mono">
                  {new Intl.NumberFormat('vi-VN').format(totalPrice)}₫
                </span>
              </div>

              {totalPrice > 0 && (
                <div className="text-[11px] text-slate-500 dark:text-slate-400 bg-gray-50 dark:bg-slate-900/60 p-2 rounded-lg text-center">
                  Trả góp 0% chỉ từ <strong className="text-[#d70018] dark:text-red-400">{new Intl.NumberFormat('vi-VN').format(Math.round(totalPrice / 12))}₫</strong>/tháng
                </div>
              )}

              <button
                onClick={handleAddAllToCart}
                disabled={Object.keys(selectedParts).length === 0 || errors.length > 0}
                className="w-full py-3 bg-[#d70018] hover:bg-[#b91c1c] dark:bg-emerald-600 dark:hover:bg-emerald-500 disabled:opacity-40 text-white font-bold rounded-xl text-xs flex items-center justify-center space-x-1.5 transition shadow-sm active:scale-95 cursor-pointer"
              >
                <ShoppingCart className="w-4 h-4" />
                <span>Thêm toàn bộ vào giỏ hàng</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 6. Part Selection Modal - VISUAL PRODUCT GRID */}
      {activeSlot && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#151c2c] border border-gray-200 dark:border-slate-800 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-150 overflow-hidden text-slate-800 dark:text-slate-100">
            <div className="p-4 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between bg-gray-50 dark:bg-slate-900/80">
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">
                  Chọn {activeSlot.name}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Hiển thị các mã linh kiện chính hãng sẵn có trong kho TechStore
                </p>
              </div>
              <button
                onClick={() => setActiveSlot(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-gray-200 dark:hover:bg-slate-800 text-lg leading-none transition cursor-pointer"
              >
                &times;
              </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto space-y-3">
              {loadingProducts ? (
                <div className="py-16 text-center text-xs text-slate-400">Đang tải danh sách linh kiện...</div>
              ) : availableProducts.length === 0 ? (
                <div className="py-16 text-center text-xs text-slate-400">Không có linh kiện nào trong mục này.</div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {availableProducts.map(prod => (
                    <div
                      key={prod.id}
                      className="p-3 border border-gray-200 dark:border-slate-700/80 hover:border-[#d70018] dark:hover:border-emerald-500 rounded-xl flex flex-col justify-between space-y-2.5 transition cursor-pointer bg-white dark:bg-slate-900/60 hover:shadow-xs group"
                      onClick={() => handleSelectPart(prod)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-16 h-16 rounded-lg bg-gray-50 dark:bg-slate-800 p-1 border border-gray-200 dark:border-slate-700 flex-shrink-0 flex items-center justify-center">
                          <img
                            src={prod.imageUrl}
                            alt={prod.name}
                            className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <span className="text-[10px] font-bold text-[#d70018] dark:text-red-400 uppercase block">
                            {prod.brandName}
                          </span>
                          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 line-clamp-2 leading-snug group-hover:text-[#d70018] dark:group-hover:text-emerald-400 transition">
                            {prod.name}
                          </h4>
                          <span className="text-xs font-black text-[#d70018] dark:text-red-400 font-mono mt-0.5 block">
                            {new Intl.NumberFormat('vi-VN').format(prod.price)}₫
                          </span>
                        </div>
                      </div>

                      {/* Specs Tags */}
                      <div className="flex flex-wrap items-center gap-1 pt-1.5 border-t border-gray-100 dark:border-slate-800">
                        {prod.specs.socket && <span className="text-[10px] px-1.5 py-0.5 bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/60 rounded font-medium">{prod.specs.socket}</span>}
                        {prod.specs.ram_type && <span className="text-[10px] px-1.5 py-0.5 bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-900/60 rounded font-medium">{prod.specs.ram_type}</span>}
                        {prod.specs.vram_gb && <span className="text-[10px] px-1.5 py-0.5 bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-900/60 rounded font-medium">{prod.specs.vram_gb}GB VRAM</span>}
                        {prod.specs.psu_watt && <span className="text-[10px] px-1.5 py-0.5 bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded font-medium">{prod.specs.psu_watt}W</span>}
                        {prod.specs.storage_gb && <span className="text-[10px] px-1.5 py-0.5 bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-900/60 rounded font-medium">{prod.specs.storage_gb}GB</span>}
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectPart(prod);
                        }}
                        className="w-full py-2 bg-[#d70018] hover:bg-[#b91c1c] dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition shadow-xs cursor-pointer"
                      >
                        Gắn linh kiện này
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 6. Printable Official Quotation Modal */}
      {showQuoteModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4 print:p-0 print:bg-white animate-in fade-in duration-200">
          <div className="bg-white text-slate-800 rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl border border-slate-200 relative print:border-none print:shadow-none print:p-0 print:max-w-none">
            {/* Modal Close & Action Header (Hidden in Print) */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 print:hidden">
              <div className="flex items-center space-x-2">
                <Printer className="w-5 h-5 text-[#d70018]" />
                <h3 className="font-bold text-sm text-slate-900">Bảng Báo Giá Linh Kiện & Cấu Hình Máy Tính</h3>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => window.print()}
                  className="px-3.5 py-1.5 bg-[#d70018] hover:bg-[#b91c1c] text-white text-xs font-bold rounded-xl flex items-center space-x-1.5 transition shadow-xs cursor-pointer"
                >
                  <Printer className="w-4 h-4" />
                  <span>In / Lưu PDF (Ctrl + P)</span>
                </button>
                <button
                  onClick={() => setShowQuoteModal(false)}
                  className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Printable Content Area */}
            <div className="pt-4 space-y-6">
              {/* Header Company Info */}
              <div className="flex justify-between items-start border-b border-slate-200 pb-5">
                <div>
                  <div className="flex items-baseline space-x-1.5">
                    <span className="text-2xl font-black text-slate-900 tracking-tight">Tech<span className="text-[#d70018]">Store</span></span>
                    <span className="text-[10px] font-black uppercase px-1.5 py-0.5 rounded bg-emerald-600 text-white">STUDIO</span>
                  </div>
                  <p className="text-xs text-slate-600 font-medium mt-1">CÔNG TY CỔ PHẦN CÔNG NGHỆ & GIẢI PHÁP MÁY TÍNH TECHSTORE</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">Địa chỉ: 45 Xuân Thủy, Cầu Giấy, Hà Nội | 123 Nguyễn Thị Minh Khai, Q.1, TP.HCM</p>
                  <p className="text-[11px] text-slate-500">Hotline: 1800.6868 (Miễn phí) | Website: www.techstore.vn</p>
                </div>
                <div className="text-right">
                  <span className="inline-block px-2.5 py-1 bg-emerald-50 border border-emerald-200 text-[#d70018] font-mono font-bold text-xs rounded-lg">
                    MÃ: TS-RIG-2026-9821
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1">Ngày lập: {new Date().toLocaleDateString('vi-VN')}</p>
                  <p className="text-[11px] text-slate-400">Hiệu lực báo giá: 15 ngày</p>
                </div>
              </div>

              {/* Customer Box */}
              <div className="grid grid-cols-2 gap-4 bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-500 block">Khách hàng:</span>
                  <strong className="text-slate-900 font-bold">Khách Hàng TechStore Studio</strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Tình trạng tương thích:</span>
                  <strong className="text-emerald-700 font-bold flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Tương thích phần cứng 100% (Đã kiểm định)</span>
                  </strong>
                </div>
              </div>

              {/* Items Table */}
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100 text-slate-700 border-b border-slate-200 font-bold">
                    <tr>
                      <th className="py-2.5 px-3 w-8">STT</th>
                      <th className="py-2.5 px-3">Linh kiện / Hạng mục</th>
                      <th className="py-2.5 px-3">Tên sản phẩm chính hãng</th>
                      <th className="py-2.5 px-3 text-center">Bảo hành</th>
                      <th className="py-2.5 px-3 text-right">Đơn giá</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {SLOTS.map((slot, idx) => {
                      const item = selectedParts[slot.key];
                      return (
                        <tr key={slot.key} className={idx % 2 === 1 ? 'bg-slate-50/50' : 'bg-white'}>
                          <td className="py-2.5 px-3 font-mono text-slate-400 text-center">{idx + 1}</td>
                          <td className="py-2.5 px-3 font-semibold text-slate-700">{slot.name}</td>
                          <td className="py-2.5 px-3">
                            {item ? (
                              <span className="font-bold text-slate-900">{item.name}</span>
                            ) : (
                              <span className="italic text-slate-400">Chưa lựa chọn</span>
                            )}
                          </td>
                          <td className="py-2.5 px-3 text-center text-slate-600">
                            {item ? `${item.specs?.warranty_months || 36}T` : '-'}
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono font-bold text-slate-900">
                            {item ? `${new Intl.NumberFormat('vi-VN').format(item.price)}₫` : '-'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pricing & Seal Summary */}
              <div className="flex justify-between items-end pt-2">
                <div className="space-y-1 text-xs text-slate-600">
                  <p>• <strong>Công suất ước tính:</strong> ~{validationResult?.estimatedWattage || 380}W (Nguồn đề xuất: {validationResult?.recommendedWattage || 650}W)</p>
                  <p>• <strong>Ưu đãi đi kèm:</strong> Tặng gói cân màu màn hình SpyderX & Miễn phí vệ sinh máy trọn đời.</p>
                  <p>• <strong>Chính sách:</strong> Lỗi 1 đổi 1 trong 30 ngày ngay tại cửa hàng.</p>
                </div>

                <div className="text-right space-y-1">
                  <span className="text-xs text-slate-500">Tổng thanh toán dự kiến:</span>
                  <div className="text-2xl font-black text-[#d70018] font-mono">
                    {new Intl.NumberFormat('vi-VN').format(totalPrice)}₫
                  </div>
                  <div className="pt-2 flex justify-end">
                    <div className="border-2 border-red-500 rounded-lg px-3 py-1 text-red-600 text-[10px] font-black uppercase tracking-wider rotate-[-6deg] shadow-xs">
                      ★ TECHSTORE VERIFIED ★<br />ĐÃ DUYỆT BÁO GIÁ
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 7. Modal Gửi Yêu Cầu Báo Giá Đến TechStore */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#151c2c] text-slate-800 dark:text-slate-100 rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 relative">
            <button
              onClick={() => setShowSubmitModal(false)}
              className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full"
            >
              <X className="w-5 h-5" />
            </button>

            {submittedQuoteId ? (
              <div className="text-center py-6 space-y-4">
                <div className="w-14 h-14 mx-auto rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-[#d70018] flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Gửi Cấu Hình Thành Công!
                </h3>
                <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-2xl text-xs space-y-1">
                  <span className="text-slate-500 dark:text-slate-400 block">Mã báo giá kỹ thuật của bạn:</span>
                  <strong className="text-sm font-mono text-[#d70018] dark:text-red-400">{submittedQuoteId}</strong>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Kỹ thuật viên phòng Lab TechStore đã nhận được cấu hình và sẽ liên hệ số <strong>{customerPhone}</strong> trong vòng 15 phút để tư vấn và tiến hành ráp máy!
                </p>
                <button
                  onClick={() => setShowSubmitModal(false)}
                  className="w-full py-2.5 bg-[#059669] text-white rounded-xl text-xs font-bold cursor-pointer"
                >
                  Đóng
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmitQuotation} className="space-y-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <span>Gửi Cấu Hình Nhận Báo Giá Kỹ Thuật</span>
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    Cấu hình gồm {Object.keys(selectedParts).length} linh kiện, trị giá <strong>{new Intl.NumberFormat('vi-VN').format(totalPrice)}₫</strong>
                  </p>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="block font-bold mb-1 text-slate-700 dark:text-slate-300">Họ và tên của bạn:</label>
                    <input
                      type="text"
                      required
                      value={customerName}
                      onChange={e => setCustomerName(e.target.value)}
                      placeholder="Ví dụ: Hoàng Anh Đức"
                      className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block font-bold mb-1 text-slate-700 dark:text-slate-300">Số điện thoại liên hệ:</label>
                    <input
                      type="tel"
                      required
                      value={customerPhone}
                      onChange={e => setCustomerPhone(e.target.value)}
                      placeholder="Ví dụ: 0912.345.678"
                      className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block font-bold mb-1 text-slate-700 dark:text-slate-300">Ghi chú yêu cầu kỹ thuật (tùy chọn):</label>
                    <textarea
                      rows={2}
                      value={customerNote}
                      onChange={e => setCustomerNote(e.target.value)}
                      placeholder="Ví dụ: Nhờ shop hỗ trợ cài sẵn Windows 11 và đi dây gọn gàng..."
                      className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 outline-none focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="pt-2 flex space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowSubmitModal(false)}
                    className="flex-1 py-2.5 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 cursor-pointer"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={submittingQuote}
                    className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold disabled:opacity-50 cursor-pointer"
                  >
                    {submittingQuote ? 'Đang gửi...' : 'Gửi Yêu Cầu Ngay'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
