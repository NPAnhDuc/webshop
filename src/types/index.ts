export type CategorySlug = 'laptop' | 'pc' | 'cpu' | 'mainboard' | 'ram' | 'ssd' | 'vga' | 'psu' | 'case' | 'cooler' | 'monitor' | 'accessories';

export interface Category {
  id: string;
  name: string;
  slug: CategorySlug;
  parentId?: string;
  icon?: string;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
}

export type ProductStatus = 'active' | 'draft' | 'archived';
export type StockStatus = 'in_stock' | 'low_stock' | 'out_of_stock';

export interface ProductVariant {
  id: string;
  productId: string;
  sku: string;
  name: string; // e.g. "Core i5 / 16GB / 512GB / Xám"
  price: number;
  originalPrice?: number;
  costPrice: number;
  status: 'active' | 'inactive';
}

export interface ProductSpecs {
  // Common / Laptop specs
  cpu_brand?: string;
  cpu_model?: string;
  cpu_generation?: string;
  cores?: number;
  ram_gb?: number;
  ram_type?: 'DDR4' | 'DDR5' | 'LPDDR5' | 'LPDDR5X';
  ram_upgradable?: boolean;
  storage_gb?: number;
  storage_type?: 'NVMe' | 'SATA';
  gpu_type?: 'integrated' | 'discrete';
  gpu_model?: string;
  screen_inch?: number;
  resolution?: string;
  panel?: 'IPS' | 'OLED' | 'Mini-LED' | 'TN' | 'VA';
  refresh_hz?: number;
  brightness_nits?: number;
  color_gamut?: string; // e.g. "100% sRGB", "100% DCI-P3"
  touch?: boolean;
  weight_kg?: number;
  battery_wh?: number;
  warranty_months?: number;
  demand?: ('study_office' | 'gaming' | 'design_graphics' | 'thin_light' | 'technical')[];

  // Component specific specs for PC Builder BP-R1..BP-R10
  socket?: string; // e.g. "LGA1700", "AM5"
  chipset?: string; // e.g. "B760", "Z790", "B650"
  has_igpu?: boolean;
  tdp_w?: number;
  tgp_w?: number;
  psu_watt?: number;
  form_factor?: 'ATX' | 'mATX' | 'ITX';
  supported_form_factors?: ('ATX' | 'mATX' | 'ITX')[];
  ram_slots?: number;
  ram_max_gb?: number;
  ram_max_speed?: number;
  ram_speed_mhz?: number;
  vram_gb?: number;
  length_mm?: number;
  max_gpu_length_mm?: number;
  height_mm?: number;
  max_cooler_height_mm?: number;
  supported_sockets?: string[];
  interface?: 'NVMe M.2' | 'SATA III';
  power_connectors?: string;
  modular?: 'full' | 'semi' | 'non';
  certification?: '80 Plus Bronze' | '80 Plus Gold' | '80 Plus Platinum';
}

export interface Product {
  id: string;
  categoryId: string;
  categorySlug: CategorySlug;
  brandId: string;
  brandName: string;
  name: string;
  slug: string;
  description: string;
  highlights: string[];
  imageUrl: string;
  images: string[];
  price: number;
  originalPrice?: number;
  discountPercent?: number;
  variants: ProductVariant[];
  specs: ProductSpecs;
  isHot?: boolean;
  isNew?: boolean;
  hasInstallment0?: boolean;
  status: ProductStatus;
  createdAt: string;
  stockStatus?: { status: StockStatus; availableQty: number };
}

export interface InventoryItem {
  variantId: string;
  productId: string;
  qtyOnHand: number;
  qtyReserved: number;
  reorderPoint: number;
  warehouseId: string;
  updatedAt: string;
}

export interface InventoryMovement {
  id: string;
  variantId: string;
  productId: string;
  type: 'in' | 'out' | 'adjust' | 'reserve' | 'release';
  qty: number;
  refType: 'order' | 'purchase_order' | 'audit';
  refId: string;
  note?: string;
  createdAt: string;
}

export interface Promotion {
  id: string;
  name: string;
  type: 'percentage' | 'fixed_amount' | 'gift' | 'zero_installment';
  value: number; // e.g. 10 for 10%, or 500000 for 500k VND
  description: string;
  startsAt: string;
  endsAt: string;
  applicableProductIds?: string[];
  applicableCategorySlugs?: string[];
  isFlashSale?: boolean;
  flashSaleTotalQuota?: number;
  flashSaleRemainingQuota?: number;
}

export interface OrderItem {
  variantId: string;
  productId: string;
  productName: string;
  sku: string;
  price: number;
  costPrice: number;
  qty: number;
  specsSummary?: string;
}

export type OrderStatus = 'new' | 'confirmed' | 'shipping' | 'completed' | 'cancelled' | 'returned';

export interface Order {
  id: string;
  orderCode: string; // e.g. ORD-20261016-8921
  customerName: string;
  customerPhone: string;
  customerAddress: string;
  customerCity: string;
  notes?: string;
  items: OrderItem[];
  subtotal: number;
  discount: number;
  total: number;
  status: OrderStatus;
  paymentMethod: 'cod' | 'bank_transfer';
  paymentStatus: 'pending' | 'paid';
  createdAt: string;
  statusTimeline: {
    status: OrderStatus;
    timestamp: string;
    note?: string;
  }[];
}

export interface StrategicDocument {
  id: string;
  docType: 'sales_plan' | 'marketing' | 'policy' | 'management_report';
  title: string;
  period: string; // e.g. "2026-Q3", "2026-Q4", "2026-10"
  effectiveFrom: string;
  effectiveTo: string;
  version: string;
  status: 'indexed' | 'processing' | 'superseded';
  content: string;
  chunks: {
    id: string;
    headingPath: string;
    text: string;
    keywords: string[];
  }[];
}

export interface ChartSpec {
  chart_id: string;
  type: 'line' | 'bar' | 'pie';
  title: string;
  x?: { field: string; label: string };
  y?: { label: string; format: 'number' | 'currency' | 'percent' };
  data: any[];
  series?: { name: string; field: string; style?: 'solid' | 'dashed'; color?: string }[];
  filters?: Record<string, string>;
  sources?: { type: 'table' | 'document'; name?: string; title?: string; section?: string; version?: string }[];
  pinnable: boolean;
}

export interface StrategyProposalOption {
  id: string;
  title: string;
  description: string;
  impactMetrics: {
    expectedSalesIncrease: string;
    budgetRequired: string;
    projectedMargin: string;
  };
  risks: string[];
  assumptions: string[];
  citations: string[];
  isRecommended?: boolean;
}

export interface StrategyProposal {
  id: string;
  topic: string;
  createdAt: string;
  status: 'pending' | 'approved' | 'rejected';
  approvedOptionId?: string;
  options: StrategyProposalOption[];
}
