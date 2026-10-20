import fs from 'fs';
import path from 'path';
import {
  Category,
  Brand,
  Product,
  ProductVariant,
  InventoryItem,
  InventoryMovement,
  Promotion,
  Order,
  OrderItem,
  OrderStatus,
  StrategicDocument,
  ChartSpec,
  StrategyProposal,
  StockStatus
} from '../types/index.js';
import {
  INITIAL_CATEGORIES,
  INITIAL_BRANDS,
  INITIAL_PRODUCTS,
  INITIAL_PROMOTIONS,
  INITIAL_STRATEGIC_DOCUMENTS
} from './seedData.js';

export interface StoreSettings {
  storeName: string;
  slogan: string;
  hotlineSales: string;
  hotlineWarranty: string;
  marqueeText: string;
  freeShippingThreshold: number;
  vatPercent: number;
  showrooms: { id: string; name: string; address: string; phone: string }[];
}

export interface CustomerQuotation {
  id: string;
  customerName: string;
  phone: string;
  title: string;
  totalPrice: number;
  totalWatts: number;
  recommendedPsu: string;
  compatibilityScore: number;
  createdAt: string;
  status: 'pending' | 'approved' | 'completed' | 'rejected';
  parts: { type: string; name: string; price: number }[];
  note?: string;
}

export interface CustomerReview {
  id: string;
  productSlug?: string;
  productId?: string;
  productName: string;
  customerName: string;
  rating: number;
  comment: string;
  createdAt: string;
  status: 'approved' | 'pending' | 'hidden';
  reply?: string;
}

interface DatabaseState {
  categories: Category[];
  brands: Brand[];
  products: Product[];
  inventory: Record<string, InventoryItem>; // variantId -> InventoryItem
  movements: InventoryMovement[];
  promotions: Promotion[];
  orders: Order[];
  documents: StrategicDocument[];
  proposals: StrategyProposal[];
  pinnedWidgets: ChartSpec[];
  settings?: StoreSettings;
  quotations?: CustomerQuotation[];
  reviews?: CustomerReview[];
}

const DATA_FILE = path.join(process.cwd(), 'data', 'store_state.json');

export class Store {
  private state: DatabaseState;

  constructor() {
    this.state = this.loadOrInitialize();
  }

  private loadOrInitialize(): DatabaseState {
    const dataDir = path.dirname(DATA_FILE);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    if (fs.existsSync(DATA_FILE)) {
      try {
        const raw = fs.readFileSync(DATA_FILE, 'utf-8');
        const parsed: DatabaseState = JSON.parse(raw);
        if (!parsed.settings) parsed.settings = this.defaultSettings();
        if (!parsed.quotations) parsed.quotations = this.defaultQuotations();
        if (!parsed.reviews) parsed.reviews = this.defaultReviews();
        return parsed;
      } catch (err) {
        console.error('Failed to parse database state file, re-initializing from seed:', err);
      }
    }

    return this.initializeFromSeed();
  }

  private initializeFromSeed(): DatabaseState {
    const inventory: Record<string, InventoryItem> = {};
    const movements: InventoryMovement[] = [];

    // Seed inventory for all product variants
    INITIAL_PRODUCTS.forEach(prod => {
      prod.variants.forEach(variant => {
        let qty = 15;
        let reserved = 0;

        // Specific test scenarios from BA document
        if (prod.id === 'prod-lap-07') {
          // E2: MSI Katana 15 - simulates out of stock event in gaming
          qty = 0;
        } else if (prod.id.includes('slow')) {
          // E5: Slow moving laptops - excessive stock (35 units)
          qty = 35;
        } else if (prod.id === 'prod-lap-03') {
          // Acer Swift Go 14 - low stock (2 units left)
          qty = 2;
        }

        inventory[variant.id] = {
          variantId: variant.id,
          productId: prod.id,
          qtyOnHand: qty,
          qtyReserved: reserved,
          reorderPoint: 5,
          warehouseId: 'wh-main-hanoi',
          updatedAt: new Date().toISOString()
        };
      });
    });

    // Seed realistic past orders to enable dashboard analytics & events
    const orders: Order[] = this.generateSeedOrders();

    const state: DatabaseState = {
      categories: INITIAL_CATEGORIES,
      brands: INITIAL_BRANDS,
      products: INITIAL_PRODUCTS,
      inventory,
      movements,
      promotions: INITIAL_PROMOTIONS,
      orders,
      documents: INITIAL_STRATEGIC_DOCUMENTS,
      proposals: [
        {
          id: 'prop-e5-clearance',
          topic: 'Xử lý 3 mã laptop mỏng nhẹ tồn kho lâu ngày (HP Envy, LG Gram, Zenbook S13)',
          createdAt: new Date().toISOString(),
          status: 'pending',
          options: [
            {
              id: 'opt-a',
              title: 'Phương án A: Giảm giá có chọn lọc 12-15% kết hợp đẩy truyền thông',
              description: 'Áp dụng giảm trực tiếp 2.500.000₫ cho HP Envy và LG Gram trong chiến dịch 14 ngày. Vẫn đảm bảo biên lợi nhuận gộp trên 11%.',
              impactMetrics: {
                expectedSalesIncrease: '+18 máy trong 2 tuần',
                budgetRequired: '60.000.000₫ (ngân sách khuyến mại)',
                projectedMargin: '11.4% (tuân thủ giới hạn sàn 10%)'
              },
              risks: ['Có thể kéo khách hàng từ phân khúc 20 triệu lên thay vì bán phân khúc cao cấp.'],
              assumptions: ['Hiệu ứng phản hồi của khách tương đương đợt Flash Sale tháng 6.'],
              citations: ['Chính sách giá và khuyến mãi 2026 > Mục 3 (Xử lý hàng tồn)'],
              isRecommended: true
            },
            {
              id: 'opt-b',
              title: 'Phương án B: Bundle combo với Balo cao cấp + Chuột Logitech Master',
              description: 'Giữ nguyên giá niêm yết, tặng kèm combo phụ kiện có biên lợi nhuận cao trị giá 1.800.000₫.',
              impactMetrics: {
                expectedSalesIncrease: '+10 máy/tháng',
                budgetRequired: '30.000.000₫ chi phí quà tặng',
                projectedMargin: '14.2% giữ vững biên'
              },
              risks: ['Tốc độ giải phóng kho sẽ chậm hơn phương án A.'],
              assumptions: ['Khách văn phòng chuộng phụ kiện xịn hơn giảm giá tiền mặt.'],
              citations: ['Kế hoạch Q4/2026 > Mục 3 (Chính sách hàng tồn)']
            }
          ]
        }
      ],
      pinnedWidgets: [],
      settings: this.defaultSettings(),
      quotations: this.defaultQuotations(),
      reviews: this.defaultReviews()
    };

    this.persist(state);
    return state;
  }

  private generateSeedOrders(): Order[] {
    const orders: Order[] = [];
    const customerNames = ['Nguyễn Văn An', 'Trần Thị Mai', 'Lê Hoàng Nam', 'Phạm Minh Đức', 'Vũ Quỳnh Nga', 'Đặng Quốc Huy', 'Hoàng Thu Trang'];
    const cities = ['Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ'];

    // Generate ~35 orders across recent months
    for (let i = 1; i <= 35; i++) {
      const isRecent = i > 25;
      const daysAgo = Math.floor(Math.random() * 60);
      const orderDate = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000).toISOString();
      const orderCode = `ORD-2026-${(1000 + i).toString()}`;
      const customerName = customerNames[i % customerNames.length];
      const customerPhone = `098${Math.floor(1000000 + Math.random() * 9000000)}`;

      // Pick a random product
      const product = INITIAL_PRODUCTS[i % INITIAL_PRODUCTS.length];
      const variant = product.variants[0];
      const qty = 1;
      const subtotal = variant.price * qty;
      const discount = (i % 3 === 0) ? 500000 : 0;
      const total = subtotal - discount;

      const statuses: OrderStatus[] = ['completed', 'completed', 'completed', 'shipping', 'confirmed', 'new'];
      const status: OrderStatus = isRecent ? statuses[i % statuses.length] : 'completed';

      orders.push({
        id: `ord-${i}`,
        orderCode,
        customerName,
        customerPhone,
        customerAddress: `Số ${12 + i}, Đường Giải Phóng`,
        customerCity: cities[i % cities.length],
        notes: i % 4 === 0 ? 'Giao giờ hành chính giúp em' : undefined,
        items: [
          {
            variantId: variant.id,
            productId: product.id,
            productName: product.name,
            sku: variant.sku,
            price: variant.price,
            costPrice: variant.costPrice,
            qty
          }
        ],
        subtotal,
        discount,
        total,
        status,
        paymentMethod: i % 2 === 0 ? 'cod' : 'bank_transfer',
        paymentStatus: status === 'completed' ? 'paid' : 'pending',
        createdAt: orderDate,
        statusTimeline: [
          { status: 'new', timestamp: orderDate, note: 'Khách hàng đặt trực tuyến' },
          ...(status !== 'new' ? [{ status: 'confirmed' as OrderStatus, timestamp: orderDate, note: 'Nhân viên xác nhận đơn hàng' }] : []),
          ...(status === 'completed' || status === 'shipping' ? [{ status: 'shipping' as OrderStatus, timestamp: orderDate, note: 'Đã xuất kho bàn giao vận chuyển' }] : []),
          ...(status === 'completed' ? [{ status: 'completed' as OrderStatus, timestamp: orderDate, note: 'Giao hàng thành công' }] : [])
        ]
      });
    }

    return orders;
  }

  private persist(state: DatabaseState) {
    try {
      fs.writeFileSync(DATA_FILE, JSON.stringify(state, null, 2), 'utf-8');
    } catch (err) {
      console.error('Error writing state file:', err);
    }
  }

  // --- PRODUCTS & CATEGORIES ---
  public getCategories(): Category[] {
    return this.state.categories;
  }

  public getBrands(): Brand[] {
    return this.state.brands;
  }

  public getProductStockStatus(productId: string): { status: StockStatus; availableQty: number } {
    const product = this.state.products.find(p => p.id === productId);
    if (!product || product.variants.length === 0) return { status: 'out_of_stock', availableQty: 0 };

    let totalAvailable = 0;
    product.variants.forEach(v => {
      const inv = this.state.inventory[v.id];
      if (inv) {
        const avail = Math.max(0, inv.qtyOnHand - inv.qtyReserved);
        totalAvailable += avail;
      }
    });

    if (totalAvailable <= 0) return { status: 'out_of_stock', availableQty: 0 };
    if (totalAvailable <= 3) return { status: 'low_stock', availableQty: totalAvailable };
    return { status: 'in_stock', availableQty: totalAvailable };
  }

  public getProducts(params: {
    category?: string;
    brand?: string;
    q?: string;
    minPrice?: number;
    maxPrice?: number;
    demand?: string;
    panel?: string;
    ram_gb?: number;
    inStockOnly?: boolean;
    hasInstallment0?: boolean;
    sort?: 'featured' | 'price_asc' | 'price_desc' | 'newest' | 'discount_desc';
    page?: number;
    limit?: number;
  }) {
    let list = this.state.products.filter(p => p.status === 'active');

    // Filter by Category
    if (params.category && params.category !== 'all') {
      list = list.filter(p => p.categorySlug === params.category || p.categoryId === params.category);
    }

    // Filter by Brand
    if (params.brand) {
      const brands = params.brand.split(',');
      list = list.filter(p => brands.includes(p.brandName.toLowerCase()) || brands.includes(p.brandId));
    }

    // Filter by Search Query
    if (params.q) {
      const qLower = params.q.toLowerCase().trim();
      list = list.filter(p =>
        p.name.toLowerCase().includes(qLower) ||
        p.brandName.toLowerCase().includes(qLower) ||
        p.description.toLowerCase().includes(qLower) ||
        (p.specs.cpu_model && p.specs.cpu_model.toLowerCase().includes(qLower)) ||
        (p.specs.gpu_model && p.specs.gpu_model.toLowerCase().includes(qLower))
      );
    }

    // Filter by Price
    if (params.minPrice !== undefined) {
      list = list.filter(p => p.price >= params.minPrice!);
    }
    if (params.maxPrice !== undefined) {
      list = list.filter(p => p.price <= params.maxPrice!);
    }

    // Filter by Demand
    if (params.demand) {
      list = list.filter(p => p.specs.demand && p.specs.demand.includes(params.demand as any));
    }

    // Filter by Panel (e.g. OLED, IPS)
    if (params.panel) {
      list = list.filter(p => p.specs.panel?.toLowerCase() === params.panel?.toLowerCase());
    }

    // Filter by RAM
    if (params.ram_gb) {
      list = list.filter(p => p.specs.ram_gb === params.ram_gb);
    }

    // Filter by In-Stock
    if (params.inStockOnly) {
      list = list.filter(p => this.getProductStockStatus(p.id).status !== 'out_of_stock');
    }

    // Filter by 0% Installment
    if (params.hasInstallment0) {
      list = list.filter(p => p.hasInstallment0);
    }

    // Dynamic Facet Counts calculation for UI
    const facets = {
      brands: {} as Record<string, number>,
      panels: {} as Record<string, number>,
      rams: {} as Record<string, number>,
      demands: {} as Record<string, number>,
      priceRanges: {
        under15m: 0,
        from15to20m: 0,
        from20to30m: 0,
        above30m: 0
      }
    };

    // Calculate facets based on category matches
    const baseCategoryList = params.category && params.category !== 'all'
      ? this.state.products.filter(p => p.categorySlug === params.category)
      : this.state.products;

    baseCategoryList.forEach(p => {
      facets.brands[p.brandName] = (facets.brands[p.brandName] || 0) + 1;
      if (p.specs.panel) facets.panels[p.specs.panel] = (facets.panels[p.specs.panel] || 0) + 1;
      if (p.specs.ram_gb) facets.rams[`${p.specs.ram_gb}GB`] = (facets.rams[`${p.specs.ram_gb}GB`] || 0) + 1;
      p.specs.demand?.forEach(d => {
        facets.demands[d] = (facets.demands[d] || 0) + 1;
      });

      if (p.price < 15000000) facets.priceRanges.under15m++;
      else if (p.price <= 20000000) facets.priceRanges.from15to20m++;
      else if (p.price <= 30000000) facets.priceRanges.from20to30m++;
      else facets.priceRanges.above30m++;
    });

    // Sorting
    const sort = params.sort || 'featured';
    if (sort === 'price_asc') {
      list.sort((a, b) => a.price - b.price);
    } else if (sort === 'price_desc') {
      list.sort((a, b) => b.price - a.price);
    } else if (sort === 'newest') {
      list.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    } else if (sort === 'discount_desc') {
      list.sort((a, b) => (b.discountPercent || 0) - (a.discountPercent || 0));
    } else {
      // Featured: hot items first
      list.sort((a, b) => (b.isHot ? 1 : 0) - (a.isHot ? 1 : 0));
    }

    const total = list.length;
    const page = Math.max(1, params.page || 1);
    const limit = params.limit || 12;
    const startIndex = (page - 1) * limit;
    const paginatedProducts = list.slice(startIndex, startIndex + limit).map(p => ({
      ...p,
      stockStatus: this.getProductStockStatus(p.id)
    }));

    return {
      products: paginatedProducts,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
      facets
    };
  }

  public getProductBySlug(slug: string) {
    const product = this.state.products.find(p => p.slug === slug || p.id === slug);
    if (!product) return null;

    const stockInfo = this.getProductStockStatus(product.id);
    const variantStock = product.variants.map(v => {
      const inv = this.state.inventory[v.id];
      const avail = inv ? Math.max(0, inv.qtyOnHand - inv.qtyReserved) : 0;
      return {
        variantId: v.id,
        availableQty: avail,
        isAvailable: avail > 0
      };
    });

    // Find similar products in same category
    const similar = this.state.products
      .filter(p => p.id !== product.id && p.categoryId === product.categoryId)
      .slice(0, 4)
      .map(p => ({
        ...p,
        stockStatus: this.getProductStockStatus(p.id)
      }));

    // Find frequently bought together items
    const boughtTogether = this.state.products
      .filter(p => p.categorySlug === 'ram' || p.categorySlug === 'ssd' || p.categorySlug === 'cooler')
      .slice(0, 3)
      .map(p => ({
        ...p,
        stockStatus: this.getProductStockStatus(p.id)
      }));

    return {
      ...product,
      stockStatus: stockInfo,
      variantStock,
      similarProducts: similar,
      frequentlyBoughtTogether: boughtTogether
    };
  }

  // --- CART & ORDERS WITH REAL-TIME RESERVATIONS ---
  public validateCart(items: { variantId: string; qty: number }[]) {
    let isValid = true;
    let subtotal = 0;
    const validatedItems: any[] = [];
    const errors: string[] = [];

    items.forEach(item => {
      let foundVariant: ProductVariant | undefined;
      let foundProduct: Product | undefined;

      for (const p of this.state.products) {
        const v = p.variants.find(varItem => varItem.id === item.variantId);
        if (v) {
          foundVariant = v;
          foundProduct = p;
          break;
        }
      }

      if (!foundVariant || !foundProduct) {
        isValid = false;
        errors.push(`Mã sản phẩm ${item.variantId} không tồn tại.`);
        return;
      }

      const inv = this.state.inventory[item.variantId];
      const available = inv ? Math.max(0, inv.qtyOnHand - inv.qtyReserved) : 0;

      if (available < item.qty) {
        isValid = false;
        errors.push(`Sản phẩm "${foundProduct.name}" (${foundVariant.name}) chỉ còn ${available} máy trong kho.`);
      }

      const itemTotal = foundVariant.price * item.qty;
      subtotal += itemTotal;

      validatedItems.push({
        variantId: item.variantId,
        productId: foundProduct.id,
        productName: foundProduct.name,
        variantName: foundVariant.name,
        sku: foundVariant.sku,
        imageUrl: foundProduct.imageUrl,
        price: foundVariant.price,
        costPrice: foundVariant.costPrice,
        qty: item.qty,
        availableQty: available,
        total: itemTotal
      });
    });

    return {
      isValid,
      errors,
      items: validatedItems,
      subtotal,
      shippingFee: 0, // Free shipping
      discount: 0,
      total: subtotal
    };
  }

  public createOrder(data: {
    customerName: string;
    customerPhone: string;
    customerAddress: string;
    customerCity: string;
    notes?: string;
    items: { variantId: string; qty: number }[];
    paymentMethod: 'cod' | 'bank_transfer';
  }) {
    // 1. Transactional check & reserve
    const cartVal = this.validateCart(data.items);
    if (!cartVal.isValid) {
      return { success: false, message: cartVal.errors.join('; ') };
    }

    const orderId = `ord-${Date.now()}`;
    const orderCode = `ORD-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(1000 + Math.random() * 9000)}`;
    const now = new Date().toISOString();

    const orderItems: OrderItem[] = cartVal.items.map(it => {
      // Reserve stock immediately
      const inv = this.state.inventory[it.variantId];
      if (inv) {
        inv.qtyReserved += it.qty;
        inv.updatedAt = now;
      }

      // Log movement
      this.state.movements.push({
        id: `mov-${Date.now()}-${Math.random()}`,
        variantId: it.variantId,
        productId: it.productId,
        type: 'reserve',
        qty: it.qty,
        refType: 'order',
        refId: orderId,
        note: `Giữ hàng cho đơn ${orderCode}`,
        createdAt: now
      });

      return {
        variantId: it.variantId,
        productId: it.productId,
        productName: it.productName,
        sku: it.sku,
        price: it.price,
        costPrice: it.costPrice,
        qty: it.qty,
        specsSummary: it.variantName
      };
    });

    const newOrder: Order = {
      id: orderId,
      orderCode,
      customerName: data.customerName,
      customerPhone: data.customerPhone,
      customerAddress: data.customerAddress,
      customerCity: data.customerCity,
      notes: data.notes,
      items: orderItems,
      subtotal: cartVal.subtotal,
      discount: cartVal.discount,
      total: cartVal.total,
      status: 'new',
      paymentMethod: data.paymentMethod,
      paymentStatus: 'pending',
      createdAt: now,
      statusTimeline: [
        { status: 'new', timestamp: now, note: 'Khách hàng tạo đơn trực tuyến thành công.' }
      ]
    };

    this.state.orders.unshift(newOrder);
    this.persist(this.state);

    return {
      success: true,
      order: newOrder
    };
  }

  public lookupOrder(phone: string, orderCode: string) {
    const cleanPhone = phone.trim().replace(/\D/g, '');
    const cleanCode = orderCode.trim().toUpperCase();

    const order = this.state.orders.find(o =>
      o.orderCode.toUpperCase() === cleanCode &&
      o.customerPhone.replace(/\D/g, '').endsWith(cleanPhone.slice(-6))
    );

    return order || null;
  }

  // --- PC BUILDER RULE ENGINE (BP-R1 TO BP-R10) ---
  public validatePCBuild(parts: Record<string, string>) {
    // parts: { cpu: 'prod-cpu-01', mainboard: 'prod-mb-01', ram: 'prod-ram-01', vga: 'prod-vga-01', ... }
    const selectedProducts: Record<string, Product> = {};
    for (const [slot, id] of Object.entries(parts)) {
      if (id) {
        const prod = this.state.products.find(p => p.id === id);
        if (prod) selectedProducts[slot] = prod;
      }
    }

    const issues: { rule: string; type: 'error' | 'warning'; message: string }[] = [];
    let estimatedWattage = 100; // Base motherboard/fans/drives wattage

    const cpu = selectedProducts.cpu;
    const mb = selectedProducts.mainboard;
    const ram = selectedProducts.ram;
    const vga = selectedProducts.vga;
    const psu = selectedProducts.psu;
    const pcCase = selectedProducts.case;
    const cooler = selectedProducts.cooler;

    if (cpu) estimatedWattage += cpu.specs.tdp_w || 65;
    if (vga) estimatedWattage += vga.specs.tgp_w || 115;

    // BP-R1: CPU Socket must match Mainboard Socket
    if (cpu && mb) {
      if (cpu.specs.socket && mb.specs.socket && cpu.specs.socket !== mb.specs.socket) {
        issues.push({
          rule: 'BP-R1',
          type: 'error',
          message: `Không tương thích Socket: CPU dùng socket ${cpu.specs.socket} nhưng Mainboard là socket ${mb.specs.socket}.`
        });
      }
    }

    // BP-R3: RAM type (DDR4 vs DDR5) must match Mainboard RAM type
    if (ram && mb) {
      if (ram.specs.ram_type && mb.specs.ram_type && ram.specs.ram_type !== mb.specs.ram_type) {
        issues.push({
          rule: 'BP-R3',
          type: 'error',
          message: `Không tương thích RAM: Mainboard yêu cầu chuẩn ${mb.specs.ram_type} nhưng bạn chọn thanh RAM chuẩn ${ram.specs.ram_type}.`
        });
      }
    }

    // BP-R4: Mainboard Form Factor supported by Case
    if (mb && pcCase) {
      const supported = pcCase.specs.supported_form_factors || ['ATX', 'mATX', 'ITX'];
      if (mb.specs.form_factor && !supported.includes(mb.specs.form_factor)) {
        issues.push({
          rule: 'BP-R4',
          type: 'error',
          message: `Kích thước Mainboard không vừa Case: Case chỉ hỗ trợ [${supported.join(', ')}] trong khi Mainboard là ${mb.specs.form_factor}.`
        });
      }
    }

    // BP-R5: GPU length <= Case max GPU length
    if (vga && pcCase) {
      const gpuLen = vga.specs.length_mm || 240;
      const maxGpu = pcCase.specs.max_gpu_length_mm || 350;
      if (gpuLen > maxGpu) {
        issues.push({
          rule: 'BP-R5',
          type: 'error',
          message: `Card đồ họa quá dài: VGA dài ${gpuLen}mm vượt quá giới hạn chiều dài của Case (${maxGpu}mm).`
        });
      }
    }

    // BP-R6: Cooler height <= Case max cooler height
    if (cooler && pcCase) {
      const coolerH = cooler.specs.height_mm || 155;
      const maxH = pcCase.specs.max_cooler_height_mm || 165;
      if (coolerH > maxH) {
        issues.push({
          rule: 'BP-R6',
          type: 'error',
          message: `Tản nhiệt CPU quá cao: Tản cao ${coolerH}mm trong khi Case chỉ cho phép tối đa ${maxH}mm.`
        });
      }
    }

    // BP-R7: PSU Wattage >= estimated wattage + 25% safety buffer
    const recommendedWatt = Math.ceil((estimatedWattage * 1.25) / 50) * 50;
    if (psu) {
      const psuWatt = psu.specs.psu_watt || 500;
      if (psuWatt < recommendedWatt) {
        issues.push({
          rule: 'BP-R7',
          type: 'error',
          message: `Công suất nguồn không đủ: Cấu hình cần khoảng ${recommendedWatt}W (đã gồm 25% an toàn), trong khi nguồn chỉ có ${psuWatt}W.`
        });
      }
    }

    // BP-R10: If no discrete VGA, CPU must have iGPU
    if (!vga && cpu && cpu.specs.has_igpu === false) {
      issues.push({
        rule: 'BP-R10',
        type: 'warning',
        message: 'CPU không có card đồ họa tích hợp (iGPU). Bạn cần chọn thêm Card màn hình rời để máy có thể xuất hình.'
      });
    }

    let totalPrice = 0;
    Object.values(selectedProducts).forEach(p => {
      totalPrice += p.price;
    });

    return {
      isValid: issues.filter(i => i.type === 'error').length === 0,
      issues,
      estimatedWattage,
      recommendedWattage: recommendedWatt,
      totalPrice,
      selectedPartsCount: Object.keys(selectedProducts).length
    };
  }

  // --- CUSTOMER CHATBOT LOGIC (CU-01..CU-11) ---
  public processCustomerChat(query: string, pageContext?: { currentProductSlug?: string }) {
    const qLower = query.toLowerCase().trim();

    // 1. CU-09: Handoff to human
    if (qLower.includes('nhân viên') || qLower.includes('người thật') || qLower.includes('tổng đài') || qLower.includes('gặp tư vấn')) {
      return {
        replyText: 'Dạ, em đã chuyển cuộc trò chuyện này sang cho chuyên viên tư vấn TechStore. Nhân viên trực hotline sẽ phản hồi bạn trong ít phút qua số điện thoại hoặc khung chat này ạ!',
        suggestedPills: ['Xem laptop khuyến mãi', 'Tra cứu bảo hành', 'Quay lại'],
        action: 'handoff'
      };
    }

    // 2. CU-03: Policies (Warranty, Return, 0% Installment)
    if (qLower.includes('trả góp') || qLower.includes('góp') || qLower.includes('lãi suất')) {
      return {
        replyText: 'Dạ TechStore hiện đang hỗ trợ chương trình **Trả góp 0% lãi suất** qua thẻ tín dụng của 25 ngân hàng đối tác (kỳ hạn 3, 6, 9, 12 tháng) hoặc qua CCCD duyệt hồ sơ online chỉ trong 15 phút ạ!\n\nBạn có thể chọn bất kỳ sản phẩm laptop hoặc máy bộ nào trên 15 triệu để áp dụng.',
        suggestedPills: ['Laptop tầm 20 triệu', 'Cách thức trả góp', 'Xem máy còn hàng'],
        action: 'none'
      };
    }

    if (qLower.includes('bảo hành') || qLower.includes('đổi trả') || qLower.includes('lỗi')) {
      return {
        replyText: 'Chính sách bảo hành tại TechStore:\n- **1 đổi 1 trong 30 ngày đầu** nếu máy có lỗi phần cứng do nhà sản xuất.\n- Bảo hành chính hãng 12 - 24 tháng theo đúng tiêu chuẩn hãng tại Việt Nam.\n- Hỗ trợ gửi bảo hành miễn phí và cho mượn máy tương đương trong thời gian chờ sửa chữa.',
        suggestedPills: ['Tìm laptop OLED', 'Gặp nhân viên'],
        action: 'none'
      };
    }

    // 3. CU-01 & CU-04: Stock check for current product or specific model
    if (qLower.includes('còn hàng không') || qLower.includes('còn không') || qLower.includes('hết hàng')) {
      if (pageContext?.currentProductSlug) {
        const prod = this.getProductBySlug(pageContext.currentProductSlug);
        if (prod) {
          if (prod.stockStatus.status === 'out_of_stock') {
            const similar = this.state.products
              .filter(p => p.id !== prod.id && p.categorySlug === prod.categorySlug && this.getProductStockStatus(p.id).status !== 'out_of_stock')
              .slice(0, 2);

            return {
              replyText: `Rất tiếc sản phẩm **${prod.name}** hiện tại đang tạm hết hàng. Tuy nhiên, shop có 2 mẫu tương đương về cấu hình và tầm giá sẵn hàng ngay:`,
              products: similar,
              suggestedPills: ['Báo khi có hàng', 'So sánh cấu hình', 'Xem máy khác'],
              action: 'none'
            };
          } else {
            return {
              replyText: `Dạ sản phẩm **${prod.name}** hiện **VẪN CÒN HÀNG** sẵn sàng giao ngay tại kho Hà Nội ạ! Giá hiện tại là ${new Intl.NumberFormat('vi-VN').format(prod.price)}₫.`,
              products: [prod],
              suggestedPills: ['Thêm vào giỏ', 'Hỏi về trả góp', 'Gặp nhân viên'],
              action: 'none'
            };
          }
        }
      }
    }

    // 4. CU-02: Budget & Needs Recommendation (Persona: "Laptop tầm 20 triệu, màn hình đẹp, không cần mạnh")
    const isBudgetSearch = qLower.includes('triệu') || qLower.includes('tr') || qLower.includes('laptop') || qLower.includes('tìm') || qLower.includes('tư vấn');
    if (isBudgetSearch) {
      let targetBudget = 20000000;
      const matchNumber = qLower.match(/(\d+)\s*(triệu|tr)/);
      if (matchNumber) {
        targetBudget = parseInt(matchNumber[1], 10) * 1000000;
      }

      const wantsBeautifulScreen = qLower.includes('màn hình đẹp') || qLower.includes('màn đẹp') || qLower.includes('oled') || qLower.includes('chuẩn màu');
      const wantsLightweight = qLower.includes('nhẹ') || qLower.includes('mỏng') || qLower.includes('mang đi');
      const wantsGaming = qLower.includes('game') || qLower.includes('đồ họa nặng') || qLower.includes('vga rời');

      // Rank matching laptops based on section 6.3.3 weights
      const candidates = this.state.products.filter(p => p.categorySlug === 'laptop' && this.getProductStockStatus(p.id).status !== 'out_of_stock');

      const scored = candidates.map(prod => {
        let score = 0;
        // Price proximity (±15%)
        const priceDiff = Math.abs(prod.price - targetBudget);
        const priceScore = Math.max(0, 1 - priceDiff / (targetBudget * 0.4));
        score += priceScore * 0.25;

        // Screen score
        let screenScore = 0.5;
        if (prod.specs.panel === 'OLED') screenScore = 1.0;
        else if (prod.specs.resolution?.includes('2.8K') || prod.specs.resolution?.includes('3K')) screenScore = 0.9;
        else if (prod.specs.panel === 'IPS') screenScore = 0.7;

        if (wantsBeautifulScreen) {
          score += screenScore * 0.45;
        } else {
          score += screenScore * 0.15;
        }

        // Portability score
        if (wantsLightweight) {
          const weight = prod.specs.weight_kg || 1.8;
          const weightScore = Math.max(0, 1 - (weight - 1.0) / 1.5);
          score += weightScore * 0.3;
        }

        if (wantsGaming) {
          score += (prod.specs.gpu_type === 'discrete' ? 1.0 : 0.2) * 0.4;
        }

        return { prod, score };
      });

      scored.sort((a, b) => b.score - a.score);
      const top3 = scored.slice(0, 3).map(s => s.prod);

      return {
        replyText: `Dạ em hiểu bạn đang cần tìm laptop trong khoảng **${new Intl.NumberFormat('vi-VN').format(targetBudget)}₫** ${wantsBeautifulScreen ? 'ưu tiên màn hình sắc nét chuẩn màu' : ''}. Dưới đây là 3 mẫu laptop phù hợp nhất, đều còn hàng tại shop:`,
        products: top3,
        suggestedPills: ['So sánh 3 máy này', 'Máy rẻ hơn một chút', 'Hỏi thủ tục trả góp', 'Cần tư vấn thêm'],
        action: 'none'
      };
    }

    // Default polite response
    return {
      replyText: 'Chào bạn! Em là trợ lý mua sắm AI của TechStore. Em có thể giúp bạn:\n1. Tư vấn chọn laptop theo ngân sách và nhu cầu (ví dụ: *"Laptop tầm 20 triệu màn hình đẹp"*).\n2. Kiểm tra tình trạng còn hàng và khuyến mại.\n3. Hướng dẫn tính tiền trả góp 0% lãi suất.\n4. Giải đáp thông số kỹ thuật linh kiện và Build PC.\n\nBạn đang quan tâm sản phẩm nào để em hỗ trợ nhé?',
      suggestedPills: ['Laptop tầm 20 triệu màn đẹp', 'Laptop Gaming tốt nhất', 'Khuyến mại đang chạy', 'Trả góp 0%'],
      action: 'none'
    };
  }

  // --- ADMIN DATA CHATBOT (DE / DA / DS ANALYTICS) ---
  public processAdminChat(query: string): {
    thoughtSummary: string;
    insight: string;
    chartSpec?: ChartSpec;
    tableData?: any[];
    citations: string[];
    proposal?: StrategyProposal;
  } {
    const qLower = query.toLowerCase().trim();

    // Q08 or Plan comparison: "Quý này đạt bao nhiêu phần trăm kế hoạch, vì sao lệch?"
    if (qLower.includes('kế hoạch') || qLower.includes('đạt bao nhiêu') || qLower.includes('lệch')) {
      const chartSpec: ChartSpec = {
        chart_id: 'plan_vs_actual_q3_2026',
        type: 'line',
        title: 'Doanh thu thực tế so với kế hoạch theo tuần, Q3/2026',
        x: { field: 'week', label: 'Tuần' },
        y: { label: 'Doanh thu (Tỷ VND)', format: 'number' },
        data: [
          { week: 'T1', actual: 2.1, plan: 2.4 },
          { week: 'T2', actual: 2.3, plan: 2.5 },
          { week: 'T3', actual: 2.5, plan: 2.5 },
          { week: 'T4', actual: 2.2, plan: 2.6 },
          { week: 'T5', actual: 2.8, plan: 2.6 },
          { week: 'T6', actual: 3.1, plan: 2.7 }, // Back to School peak
          { week: 'T7', actual: 2.9, plan: 2.7 },
          { week: 'T8', actual: 2.6, plan: 2.7 },
          { week: 'T9', actual: 1.8, plan: 2.8 }, // Gaming stockout begins
          { week: 'T10', actual: 1.9, plan: 2.8 },
          { week: 'T11', actual: 2.0, plan: 2.9 },
          { week: 'T12', actual: 2.2, plan: 2.9 }
        ],
        series: [
          { name: 'Thực tế', field: 'actual', style: 'solid', color: '#2563eb' },
          { name: 'Kế hoạch', field: 'plan', style: 'dashed', color: '#94a3b8' }
        ],
        filters: { period: '2026-Q3' },
        sources: [
          { type: 'table', name: 'mart_weekly_sales' },
          { type: 'document', title: 'Kế hoạch bán hàng Q3/2026', section: 'Mục 1 & 2', version: '1.2' }
        ],
        pinnable: true
      };

      return {
        thoughtSummary: 'Truy xuất mục tiêu từ tài liệu "Kế hoạch bán hàng Q3/2026" (RAG) và đối chiếu tổng doanh thu thực tế từ cơ sở dữ liệu bán hàng.',
        insight: `**Kết quả đối chiếu Kế hoạch Q3/2026:**\n- **Doanh thu mục tiêu:** 32,0 tỷ VND (theo Kế hoạch bán Q3/2026, phiên bản 1.2).\n- **Doanh thu thực tế:** 29,44 tỷ VND, đạt **92,0% kế hoạch** (hụt 2,56 tỷ VND).\n\n**Phân rã nguyên nhân chính:**\n1. **Sự cố hết hàng nhóm Gaming (E2):** 2 mã laptop gaming chủ lực (MSI Katana 15 và Asus TUF) bị đứt hàng 3 tuần liên tiếp trong tháng 9, làm giảm ước tính khoảng 2,8 tỷ VND doanh thu.\n2. **Điểm sáng:** Chiến dịch Tựu trường (Back-to-School) tháng 8 đạt 120% mục tiêu của nhóm laptop sinh viên văn phòng.`,
        chartSpec,
        citations: ['Kế hoạch bán hàng Q3/2026 & Báo cáo kết quả (v1.2) > Mục 1: Mục tiêu tổng & Mục 2: Phân rã']
      };
    }

    // Q05 & Q15 or Dead Stock: "Mã nào đang tồn lâu nhất" / "Tháng sau nên làm gì với nhóm laptop mỏng nhẹ đang tồn?"
    if (qLower.includes('tồn') || qLower.includes('mỏng nhẹ') || qLower.includes('lâu nhất') || qLower.includes('dead stock') || qLower.includes('hàng chậm')) {
      const slowProducts = [
        { name: 'HP Envy x360 13 OLED', stock: 12, daysInStock: 85, cost: 21500000, price: 24500000, sellThrough: '28%' },
        { name: 'LG Gram 14 Siêu Nhẹ', stock: 14, daysInStock: 92, cost: 22800000, price: 25990000, sellThrough: '22%' },
        { name: 'ASUS Zenbook S 13 OLED', stock: 9, daysInStock: 78, cost: 31200000, price: 35990000, sellThrough: '31%' }
      ];

      const chartSpec: ChartSpec = {
        chart_id: 'slow_moving_inventory',
        type: 'bar',
        title: 'Số ngày tồn kho bình quân các mã laptop mỏng nhẹ (Ngưỡng cảnh báo: 60 ngày)',
        x: { field: 'name', label: 'Sản phẩm' },
        y: { label: 'Số ngày tồn kho', format: 'number' },
        data: slowProducts,
        series: [
          { name: 'Số ngày tồn', field: 'daysInStock', color: '#f59e0b' }
        ],
        sources: [
          { type: 'table', name: 'inventory_aging_mart' },
          { type: 'document', title: 'Kế hoạch Q4/2026', section: 'Chính sách hàng tồn' }
        ],
        pinnable: true
      };

      const proposal = this.state.proposals.find(p => p.id === 'prop-e5-clearance');

      return {
        thoughtSummary: 'Phân tích bảng tuổi tồn kho (Aging Report), phát hiện 3 mã hàng vượt ngưỡng an toàn 60 ngày. Đối chiếu RAG chính sách giá tối thiểu 10% để sinh 2 đề xuất hành động.',
        insight: `**Phát hiện cảnh báo hàng tồn kho lâu (Sự kiện E5):**\nCó 3 mã laptop mỏng nhẹ cao cấp đang có số ngày tồn kho từ 78 đến 92 ngày (ngưỡng an toàn của shop là 60 ngày), tỉ lệ bán hết (Sell-through) dưới 35%.\n\nEm đã lập sẵn **2 phương án chiến lược** tuân thủ điều kiện biên lợi nhuận sàn của shop để chủ shop phê duyệt ngay bên dưới:`,
        chartSpec,
        tableData: slowProducts,
        citations: ['Kế hoạch kinh doanh & Phân bổ ngân sách Q4/2026 > Mục 3: Ràng buộc chính sách giá và xử lý hàng tồn'],
        proposal
      };
    }

    // Q06: Target for Q4
    if (qLower.includes('quý 4') || qLower.includes('q4') || qLower.includes('mục tiêu')) {
      return {
        thoughtSummary: 'Truy vấn RAG từ tài liệu "Kế hoạch kinh doanh & Phân bổ ngân sách Q4/2026".',
        insight: `Theo tài liệu **Kế hoạch kinh doanh Q4/2026 (v1.0)**:\n- **Mục tiêu doanh thu toàn shop:** 45,0 tỷ VND (tăng trưởng 40% so với Q3).\n- **Mục tiêu doanh thu nhóm Gaming & PC đồ họa:** 18,0 tỷ VND (chiếm 40% doanh thu).\n- **Mục tiêu nhóm Laptop mỏng nhẹ:** 16,0 tỷ VND.\n- **Tổng ngân sách Marketing:** 800 triệu VND (cho chiến dịch 11/11, Black Friday và chuẩn bị Tết).`,
        citations: ['Kế hoạch kinh doanh & Phân bổ ngân sách Q4/2026 > Mục 1: Mục tiêu kinh doanh']
      };
    }

    // Default KPI overview
    const kpis = this.getDashboardKPIs();
    return {
      thoughtSummary: 'Tính toán tổng hợp KPI doanh thu, lợi nhuận, đơn hàng và sức khỏe tồn kho từ kho dữ liệu thời gian thực.',
      insight: `**Tổng quan sức khỏe kinh doanh hiện tại:**\n- **Doanh thu tích lũy:** ${new Intl.NumberFormat('vi-VN').format(kpis.totalRevenue)}₫\n- **Lợi nhuận gộp:** ${new Intl.NumberFormat('vi-VN').format(kpis.grossProfit)}₫ (Biên lợi nhuận: ${kpis.grossMarginPercent}%)\n- **Tổng số đơn hàng:** ${kpis.totalOrders} đơn (AOV: ${new Intl.NumberFormat('vi-VN').format(kpis.aov)}₫)\n- **Giá trị vốn tồn kho:** ${new Intl.NumberFormat('vi-VN').format(kpis.inventoryValue)}₫\n- **Số ngày tồn kho bình quân:** ${kpis.avgInventoryDays} ngày\n- **Số mã hết hàng:** ${kpis.outOfStockCount} mã`,
      citations: ['Bảng tổng hợp dữ liệu giao dịch bán hàng thời gian thực (mart_orders_summary)']
    };
  }

  // --- DASHBOARD KPIS & CHARTS ---
  public getDashboardKPIs() {
    let totalRevenue = 0;
    let totalCost = 0;
    let completedOrders = 0;

    this.state.orders.forEach(o => {
      if (o.status !== 'cancelled' && o.status !== 'returned') {
        totalRevenue += o.total;
        completedOrders++;
        o.items.forEach(it => {
          totalCost += it.costPrice * it.qty;
        });
      }
    });

    const grossProfit = totalRevenue - totalCost;
    const grossMarginPercent = totalRevenue > 0 ? ((grossProfit / totalRevenue) * 100).toFixed(1) : '0';
    const aov = completedOrders > 0 ? Math.round(totalRevenue / completedOrders) : 0;

    // Inventory stats
    let inventoryValue = 0;
    let outOfStockCount = 0;
    this.state.products.forEach(p => {
      const stock = this.getProductStockStatus(p.id);
      if (stock.status === 'out_of_stock') outOfStockCount++;
      p.variants.forEach(v => {
        const inv = this.state.inventory[v.id];
        if (inv) {
          inventoryValue += inv.qtyOnHand * v.costPrice;
        }
      });
    });

    return {
      totalRevenue,
      grossProfit,
      grossMarginPercent,
      totalOrders: completedOrders,
      aov,
      inventoryValue,
      avgInventoryDays: 42,
      outOfStockCount,
      cancelRate: '3.2%'
    };
  }

  public getDashboardCharts(): ChartSpec[] {
    return [
      {
        chart_id: 'revenue_trend',
        type: 'line',
        title: 'Xu hướng doanh thu 8 tuần gần nhất (Tỷ VND)',
        x: { field: 'period', label: 'Tuần' },
        y: { label: 'Tỷ VND', format: 'number' },
        data: [
          { period: 'T1', actual: 1.8, target: 2.0 },
          { period: 'T2', actual: 2.1, target: 2.0 },
          { period: 'T3', actual: 2.3, target: 2.1 },
          { period: 'T4', actual: 2.5, target: 2.2 },
          { period: 'T5', actual: 2.4, target: 2.2 },
          { period: 'T6', actual: 2.9, target: 2.3 },
          { period: 'T7', actual: 2.7, target: 2.4 },
          { period: 'T8', actual: 3.1, target: 2.5 }
        ],
        series: [
          { name: 'Thực tế', field: 'actual', color: '#2563eb' },
          { name: 'Chỉ tiêu', field: 'target', style: 'dashed', color: '#94a3b8' }
        ],
        pinnable: true
      },
      {
        chart_id: 'category_breakdown',
        type: 'bar',
        title: 'Cơ cấu doanh thu theo nhóm hàng tháng này (%)',
        x: { field: 'category', label: 'Nhóm hàng' },
        y: { label: 'Tỉ trọng (%)', format: 'number' },
        data: [
          { category: 'Laptop Văn phòng', share: 38 },
          { category: 'Laptop Gaming', share: 29 },
          { category: 'Linh kiện PC', share: 19 },
          { category: 'Màn hình & Phụ kiện', share: 14 }
        ],
        series: [{ name: 'Tỉ trọng', field: 'share', color: '#3b82f6' }],
        pinnable: true
      }
    ];
  }

  public pinWidget(widget: ChartSpec) {
    if (!this.state.pinnedWidgets.some(w => w.chart_id === widget.chart_id)) {
      this.state.pinnedWidgets.push(widget);
      this.persist(this.state);
    }
    return this.state.pinnedWidgets;
  }

  public getPinnedWidgets(): ChartSpec[] {
    return this.state.pinnedWidgets;
  }

  // --- ADMIN INVENTORY MANAGEMENT & RECEIPT ---
  public getInventoryList() {
    return this.state.products.map(p => {
      const variantsWithStock = p.variants.map(v => {
        const inv = this.state.inventory[v.id] || { qtyOnHand: 0, qtyReserved: 0, reorderPoint: 5 };
        const available = Math.max(0, inv.qtyOnHand - inv.qtyReserved);
        return {
          ...v,
          qtyOnHand: inv.qtyOnHand,
          qtyReserved: inv.qtyReserved,
          availableQty: available,
          reorderPoint: inv.reorderPoint,
          isLowStock: available <= inv.reorderPoint && available > 0,
          isOutOfStock: available === 0
        };
      });

      return {
        productId: p.id,
        productName: p.name,
        categoryName: p.categorySlug,
        imageUrl: p.imageUrl,
        variants: variantsWithStock
      };
    });
  }

  public createStockReceipt(variantId: string, qty: number, note: string) {
    const inv = this.state.inventory[variantId];
    if (inv) {
      inv.qtyOnHand += qty;
      inv.updatedAt = new Date().toISOString();
      this.state.movements.push({
        id: `mov-${Date.now()}`,
        variantId,
        productId: inv.productId,
        type: 'in',
        qty,
        refType: 'purchase_order',
        refId: `PO-${Date.now()}`,
        note,
        createdAt: new Date().toISOString()
      });
      this.persist(this.state);
      return { success: true, updatedQty: inv.qtyOnHand };
    }
    return { success: false, message: 'Không tìm thấy biến thể' };
  }

  // --- ADMIN ORDER MANAGEMENT ---
  public getOrders(status?: string) {
    if (status && status !== 'all') {
      return this.state.orders.filter(o => o.status === status);
    }
    return this.state.orders;
  }

  public updateOrderStatus(orderId: string, newStatus: OrderStatus, note?: string) {
    const order = this.state.orders.find(o => o.id === orderId);
    if (!order) return { success: false, message: 'Không tìm thấy đơn hàng' };

    const oldStatus = order.status;
    order.status = newStatus;
    const now = new Date().toISOString();
    order.statusTimeline.push({
      status: newStatus,
      timestamp: now,
      note: note || `Đổi trạng thái từ ${oldStatus} sang ${newStatus}`
    });

    // If order is completed, formally release reservation and deduct qtyOnHand
    if (newStatus === 'completed' && oldStatus !== 'completed') {
      order.paymentStatus = 'paid';
      order.items.forEach(it => {
        const inv = this.state.inventory[it.variantId];
        if (inv) {
          inv.qtyOnHand = Math.max(0, inv.qtyOnHand - it.qty);
          inv.qtyReserved = Math.max(0, inv.qtyReserved - it.qty);
          inv.updatedAt = now;
        }
      });
    }

    // If cancelled, release reservation back to onHand
    if (newStatus === 'cancelled' && oldStatus !== 'cancelled') {
      order.items.forEach(it => {
        const inv = this.state.inventory[it.variantId];
        if (inv) {
          inv.qtyReserved = Math.max(0, inv.qtyReserved - it.qty);
          inv.updatedAt = now;
        }
      });
    }

    this.persist(this.state);
    return { success: true, order };
  }

  // --- STRATEGY DOCUMENTS (RAG) ---
  public getDocuments(): StrategicDocument[] {
    return this.state.documents;
  }

  public addDocument(doc: {
    title: string;
    docType: 'sales_plan' | 'marketing' | 'policy' | 'management_report';
    period: string;
    effectiveFrom: string;
    effectiveTo: string;
    version: string;
    content: string;
  }) {
    const newDoc: StrategicDocument = {
      id: `doc-${Date.now()}`,
      title: doc.title,
      docType: doc.docType,
      period: doc.period,
      effectiveFrom: doc.effectiveFrom,
      effectiveTo: doc.effectiveTo,
      version: doc.version,
      status: 'indexed',
      content: doc.content,
      chunks: [
        {
          id: `chunk-${Date.now()}-1`,
          headingPath: `${doc.title} > Toàn văn`,
          text: doc.content.slice(0, 500),
          keywords: doc.title.toLowerCase().split(' ')
        }
      ]
    };

    this.state.documents.push(newDoc);
    this.persist(this.state);
    return newDoc;
  }

  public decideProposal(proposalId: string, optionId: string, decision: 'approved' | 'rejected') {
    const prop = this.state.proposals.find(p => p.id === proposalId);
    if (!prop) return { success: false, message: 'Không tìm thấy đề xuất' };

    prop.status = decision;
    if (decision === 'approved') {
      prop.approvedOptionId = optionId;
    }
    this.persist(this.state);
    return { success: true, proposal: prop };
  }

  // --- ADMIN EXTENDED MANAGEMENT ---

  // 1. Products Management
  public getAllAdminProducts() {
    return this.state.products.map(p => {
      const stock = this.getProductStockStatus(p.id);
      return {
        ...p,
        stockStatus: stock.status,
        availableQty: stock.availableQty
      };
    });
  }

  public createProduct(data: any): Product {
    const id = `prod-${Date.now()}`;
    const slug = (data.name || 'product')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)+/g, '') + `-${Date.now().toString().slice(-4)}`;
    const variantId = `var-${Date.now()}`;

    const variant: ProductVariant = {
      id: variantId,
      productId: id,
      sku: `SKU-${Date.now().toString().slice(-6)}`,
      name: data.name,
      price: Number(data.price),
      originalPrice: data.originalPrice ? Number(data.originalPrice) : undefined,
      costPrice: Math.round(Number(data.price) * 0.8),
      status: 'active'
    };

    const newProduct: Product = {
      id,
      categoryId: data.categoryId || 'cat-laptop',
      categorySlug: data.categorySlug || 'laptop',
      brandId: data.brandId || 'b-asus',
      brandName: data.brandName || 'ASUS',
      name: data.name,
      slug,
      description: data.description || '',
      highlights: data.highlights || ['Chính hãng 100%', 'Bảo hành 24 tháng', 'Đầy đủ VAT'],
      imageUrl: data.imageUrl || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80',
      images: [data.imageUrl || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80'],
      price: Number(data.price),
      originalPrice: data.originalPrice ? Number(data.originalPrice) : undefined,
      discountPercent: data.discountPercent ? Number(data.discountPercent) : undefined,
      variants: [variant],
      specs: data.specs || {},
      isHot: !!data.isHot,
      isNew: !!data.isNew,
      hasInstallment0: !!data.hasInstallment0,
      status: 'active',
      createdAt: new Date().toISOString()
    };

    this.state.products.unshift(newProduct);

    // Initialize inventory for this variant
    this.state.inventory[variantId] = {
      variantId,
      productId: id,
      qtyOnHand: Number(data.initialQty || 15),
      qtyReserved: 0,
      reorderPoint: 5,
      warehouseId: 'wh-main-hanoi',
      updatedAt: new Date().toISOString()
    };

    this.persist(this.state);
    return newProduct;
  }

  public defaultSettings(): StoreSettings {
    return {
      storeName: 'TechStore PC Studio',
      slogan: 'PC Đồ Họa - PC Gaming & Linh Kiện Chuyên Nghiệp',
      hotlineSales: '1900.0323',
      hotlineWarranty: '1800.6868',
      marqueeText: 'Sản phẩm Chính hãng 100% - Xuất VAT đầy đủ • Miễn phí vận chuyển toàn quốc cho đơn từ 300.000₫ • 1 Đổi 1 trong 30 ngày',
      freeShippingThreshold: 300000,
      vatPercent: 10,
      showrooms: [
        { id: 'sr-1', name: 'Showroom 1 (Thái Hà - HN)', address: 'Số 377-379 Thái Hà, Q. Đống Đa, Hà Nội', phone: '097.111.3323' },
        { id: 'sr-2', name: 'Showroom 2 (Lê Thanh Nghị - HN)', address: 'Số 131 Lê Thanh Nghị, Q. Hai Bà Trưng, Hà Nội', phone: '098.333.6623' },
        { id: 'sr-3', name: 'Showroom 3 (TP.HCM)', address: 'Số 249 Lý Thường Kiệt, P.15, Q.10, TP.HCM', phone: '090.888.6623' },
        { id: 'sr-4', name: 'Showroom 4 (Đà Nẵng)', address: 'Số 83-85 Nguyễn Văn Linh, Q. Hải Châu, Đà Nẵng', phone: '091.777.9923' }
      ]
    };
  }

  public defaultQuotations(): CustomerQuotation[] {
    return [
      {
        id: 'TS-RIG-2026-9821',
        customerName: 'Trần Văn Hoàng',
        phone: '0978.889.921',
        title: 'Cấu hình Gaming Esports Wukong & CS2',
        totalPrice: 28450000,
        totalWatts: 485,
        recommendedPsu: '650W - 750W',
        compatibilityScore: 100,
        createdAt: '2026-10-18T14:30:00Z',
        status: 'approved',
        parts: [
          { type: 'CPU', name: 'Intel Core i5-13400F Tray', price: 4290000 },
          { type: 'Mainboard', name: 'ASUS TUF GAMING B760M-PLUS WIFI D4', price: 3890000 },
          { type: 'RAM', name: 'Kingston Fury Beast RGB 32GB (2x16GB) DDR4 3200MHz', price: 2150000 },
          { type: 'VGA', name: 'MSI GeForce RTX 4060 VENTUS 2X WHITE 8G OC', price: 8490000 },
          { type: 'SSD', name: 'Samsung 980 PRO 1TB PCIe NVMe 4.0', price: 2490000 },
          { type: 'PSU', name: 'Corsair RM750e 750W 80 Plus Gold ATX 3.0', price: 2890000 },
          { type: 'Case', name: 'NZXT H5 Flow 2024 White', price: 2450000 }
        ]
      },
      {
        id: 'TS-RIG-2026-7734',
        customerName: 'Nguyễn Minh Thắng',
        phone: '0912.345.678',
        title: 'Workstation Đồ Họa Kiến Trúc & Render 3D',
        totalPrice: 42900000,
        totalWatts: 620,
        recommendedPsu: '750W - 850W',
        compatibilityScore: 100,
        createdAt: '2026-10-19T09:15:00Z',
        status: 'pending',
        parts: [
          { type: 'CPU', name: 'AMD Ryzen 7 7800X3D', price: 10500000 },
          { type: 'Mainboard', name: 'GIGABYTE B650 AORUS ELITE AX', price: 5800000 },
          { type: 'RAM', name: 'Corsair Vengeance RGB 64GB (2x32GB) DDR5 6000MHz', price: 5400000 },
          { type: 'VGA', name: 'ASUS TUF Gaming GeForce RTX 4070 SUPER 12GB', price: 17500000 },
          { type: 'SSD', name: 'Kingston KC3000 2TB PCIe 4.0 NVMe', price: 3700000 }
        ]
      }
    ];
  }

  public defaultReviews(): CustomerReview[] {
    return [
      {
        id: 'rev-01',
        productSlug: 'asus-tuf-gaming-a15-fa506nf',
        productName: 'Asus TUF Gaming A15 FA506NF',
        customerName: 'Lê Hoàng Nam',
        rating: 5,
        comment: 'Máy chạy cực kỳ êm và mát, chơi CS2 với Black Myth Wukong mượt mà 120 FPS. Shop đóng gói cẩn thận, giao hỏa tốc 2H rất uy tín!',
        createdAt: '2026-10-18T10:20:00Z',
        status: 'approved'
      },
      {
        id: 'rev-02',
        productSlug: 'apple-macbook-air-late-2020',
        productName: 'Apple MacBook Air (Late 2020)',
        customerName: 'Trần Thị Thu Trang',
        rating: 5,
        comment: 'Pin siêu trâu dùng cả ngày không cần sạc. Cân màu chuẩn nét, viết code và làm văn phòng rất thích.',
        createdAt: '2026-10-17T15:45:00Z',
        status: 'approved'
      },
      {
        id: 'rev-03',
        productSlug: 'lenovo-legion-slim-5i-16irh8',
        productName: 'Lenovo Legion Slim 5i 16IRH8',
        customerName: 'Vũ Đức Mạnh',
        rating: 4,
        comment: 'Màn hình 165Hz sắc nét, build cứng cáp. Shop hỗ trợ cài sẵn Windows và tặng kèm balo rất đẹp.',
        createdAt: '2026-10-19T08:30:00Z',
        status: 'pending'
      }
    ];
  }

  public updateProduct(productId: string, data: any) {
    const index = this.state.products.findIndex(p => p.id === productId);
    if (index === -1) return null;

    const existing = this.state.products[index];
    const updated: Product = {
      ...existing,
      name: data.name !== undefined ? data.name : existing.name,
      price: data.price !== undefined ? Number(data.price) : existing.price,
      originalPrice: data.originalPrice !== undefined ? Number(data.originalPrice) : existing.originalPrice,
      discountPercent: data.discountPercent !== undefined ? Number(data.discountPercent) : existing.discountPercent,
      categorySlug: data.categorySlug !== undefined ? data.categorySlug : existing.categorySlug,
      brandName: data.brandName !== undefined ? data.brandName : existing.brandName,
      description: data.description !== undefined ? data.description : existing.description,
      imageUrl: data.imageUrl !== undefined ? data.imageUrl : existing.imageUrl,
      isHot: data.isHot !== undefined ? !!data.isHot : existing.isHot,
      isNew: data.isNew !== undefined ? !!data.isNew : existing.isNew,
      hasInstallment0: data.hasInstallment0 !== undefined ? !!data.hasInstallment0 : existing.hasInstallment0,
      status: data.status !== undefined ? data.status : existing.status,
      specs: data.specs ? { ...existing.specs, ...data.specs } : existing.specs
    };

    // Update variant price & stock in inventory
    if (updated.variants && updated.variants.length > 0) {
      updated.variants[0].price = updated.price;
      if (updated.originalPrice) updated.variants[0].originalPrice = updated.originalPrice;
      const varId = updated.variants[0].id;
      if (data.stockQty !== undefined && this.state.inventory[varId]) {
        this.state.inventory[varId].qtyOnHand = Number(data.stockQty);
        this.state.inventory[varId].updatedAt = new Date().toISOString();
      }
    }

    this.state.products[index] = updated;
    this.persist(this.state);
    return updated;
  }

  public deleteProduct(productId: string) {
    const index = this.state.products.findIndex(p => p.id === productId);
    if (index === -1) return false;
    this.state.products.splice(index, 1);
    this.persist(this.state);
    return true;
  }

  // 2. Promotions Management & Dynamic Validation
  public getAllPromotions() {
    return this.state.promotions;
  }

  public validatePromotion(code: string, orderTotal: number = 0) {
    if (!code) return { valid: false, message: 'Vui lòng nhập mã giảm giá' };
    const cleanCode = code.trim().toUpperCase();
    const now = new Date();

    const promo = this.state.promotions.find(p => {
      const pName = p.name.toUpperCase();
      const pId = p.id.toUpperCase();
      const matches = pName.includes(cleanCode) || pId.includes(cleanCode) ||
        (cleanCode === 'TECH500' && (pName.includes('TECH500') || pId.includes('01') || p.value === 500000)) ||
        (cleanCode === 'GAMING2026' && (pName.includes('GAMING') || p.value === 12 || p.value === 3)) ||
        (cleanCode === 'FREESHIP' && (pName.includes('FREESHIP') || pName.includes('VẬN CHUYỂN')));
      if (!matches) return false;
      const starts = p.startsAt ? new Date(p.startsAt) : new Date(0);
      const ends = p.endsAt ? new Date(p.endsAt) : new Date(9999999999999);
      return now >= starts && now <= ends;
    });

    if (!promo) {
      if (cleanCode === 'TECH500') {
        return {
          valid: true,
          code: 'TECH500',
          name: 'Voucher TechStore 500k',
          discountAmount: 500000,
          label: 'TECH500 (-500.000₫)'
        };
      }
      if (cleanCode === 'GAMING2026') {
        const discount = Math.min(1000000, Math.round(orderTotal * 0.03)) || 300000;
        return {
          valid: true,
          code: 'GAMING2026',
          name: 'Voucher Gaming 2026 (Giảm 3%)',
          discountAmount: discount,
          label: `GAMING2026 (-${new Intl.NumberFormat('vi-VN').format(discount)}₫)`
        };
      }
      if (cleanCode === 'FREESHIP') {
        return {
          valid: true,
          code: 'FREESHIP',
          name: 'Miễn phí vận chuyển toàn quốc',
          discountAmount: 30000,
          label: 'FREESHIP (Miễn phí ship)'
        };
      }
      return { valid: false, message: 'Mã giảm giá không hợp lệ hoặc đã hết hạn áp dụng.' };
    }

    let discountAmount = 0;
    if (promo.type === 'percentage') {
      discountAmount = Math.round(orderTotal * (promo.value / 100));
    } else {
      discountAmount = promo.value;
    }

    return {
      valid: true,
      code: promo.id,
      name: promo.name,
      discountAmount,
      label: `${cleanCode} (-${new Intl.NumberFormat('vi-VN').format(discountAmount)}₫)`
    };
  }

  public createPromotion(data: any): Promotion {
    const newPromo: Promotion = {
      id: `promo-${Date.now()}`,
      name: data.name,
      type: data.type || 'fixed_amount',
      value: Number(data.value),
      description: data.description || '',
      startsAt: data.startsAt || new Date().toISOString(),
      endsAt: data.endsAt || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      isFlashSale: !!data.isFlashSale,
      flashSaleTotalQuota: data.flashSaleTotalQuota ? Number(data.flashSaleTotalQuota) : undefined,
      flashSaleRemainingQuota: data.flashSaleRemainingQuota ? Number(data.flashSaleRemainingQuota) : undefined
    };

    this.state.promotions.unshift(newPromo);
    this.persist(this.state);
    return newPromo;
  }

  public togglePromotion(promoId: string) {
    const promo = this.state.promotions.find(p => p.id === promoId);
    if (!promo) return null;
    const isCurrentlyActive = new Date(promo.endsAt) > new Date();
    if (isCurrentlyActive) {
      promo.endsAt = new Date(Date.now() - 1000).toISOString();
    } else {
      promo.endsAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
    }
    this.persist(this.state);
    return promo;
  }

  public deletePromotion(promoId: string) {
    const index = this.state.promotions.findIndex(p => p.id === promoId);
    if (index === -1) return false;
    this.state.promotions.splice(index, 1);
    this.persist(this.state);
    return true;
  }

  // 3. Customers CRM Aggregation
  public getCustomersCRM() {
    const map = new Map<string, {
      id: string;
      name: string;
      phone: string;
      city: string;
      totalOrders: number;
      totalSpent: number;
      lastOrderDate: string;
      tier: 'T-Standard' | 'T-VIP' | 'T-Diamond';
    }>();

    this.state.orders.forEach(o => {
      const phone = o.customerPhone || '0901234567';
      const existing = map.get(phone);
      if (existing) {
        existing.totalOrders += 1;
        existing.totalSpent += o.total;
        if (new Date(o.createdAt) > new Date(existing.lastOrderDate)) {
          existing.lastOrderDate = o.createdAt;
          existing.name = o.customerName;
          existing.city = o.customerCity;
        }
      } else {
        map.set(phone, {
          id: `cust-${phone}`,
          name: o.customerName,
          phone: o.customerPhone,
          city: o.customerCity,
          totalOrders: 1,
          totalSpent: o.total,
          lastOrderDate: o.createdAt,
          tier: 'T-Standard'
        });
      }
    });

    const customers = Array.from(map.values()).map(c => {
      let tier: 'T-Standard' | 'T-VIP' | 'T-Diamond' = 'T-Standard';
      if (c.totalSpent >= 80000000) tier = 'T-Diamond';
      else if (c.totalSpent >= 30000000) tier = 'T-VIP';
      return { ...c, tier };
    });

    return customers.sort((a, b) => b.totalSpent - a.totalSpent);
  }

  // 4. PC Builder Quotations
  public getCustomerQuotations(): CustomerQuotation[] {
    if (!this.state.quotations) {
      this.state.quotations = this.defaultQuotations();
    }
    return this.state.quotations;
  }

  public createCustomerQuotation(data: any): CustomerQuotation {
    const quoteList = this.getCustomerQuotations();
    const newQuote: CustomerQuotation = {
      id: `TS-RIG-${Date.now().toString().slice(-4)}`,
      customerName: data.customerName || 'Khách hàng TechStore',
      phone: data.phone || '',
      title: data.title || 'Cấu hình PC Tự Ráp Custom',
      totalPrice: Number(data.totalPrice) || 0,
      totalWatts: Number(data.totalWatts) || 450,
      recommendedPsu: data.recommendedPsu || '650W',
      compatibilityScore: Number(data.compatibilityScore) || 100,
      createdAt: new Date().toISOString(),
      status: 'pending',
      parts: data.parts || [],
      note: data.note || ''
    };
    quoteList.unshift(newQuote);
    this.persist(this.state);
    return newQuote;
  }

  public updateQuotationStatus(id: string, status: 'pending' | 'approved' | 'completed' | 'rejected') {
    const quote = this.getCustomerQuotations().find(q => q.id === id);
    if (!quote) return null;
    quote.status = status;
    this.persist(this.state);
    return quote;
  }

  // 5. Customer Reviews Moderation
  public getCustomerReviews(productSlugOrId?: string): CustomerReview[] {
    if (!this.state.reviews) {
      this.state.reviews = this.defaultReviews();
    }
    if (!productSlugOrId) return this.state.reviews;
    return this.state.reviews.filter(r => r.productSlug === productSlugOrId || r.productId === productSlugOrId);
  }

  public getProductApprovedReviews(slugOrId: string): CustomerReview[] {
    const list = this.getCustomerReviews();
    return list.filter(r => (r.status === 'approved' || !r.status) && (r.productSlug === slugOrId || r.productId === slugOrId || slugOrId === 'all'));
  }

  public createReview(data: any): CustomerReview {
    const reviews = this.getCustomerReviews();
    const newRev: CustomerReview = {
      id: `rev-${Date.now()}`,
      productSlug: data.productSlug || '',
      productId: data.productId || '',
      productName: data.productName || 'Sản phẩm TechStore',
      customerName: data.customerName || 'Khách hàng',
      rating: Number(data.rating) || 5,
      comment: data.comment || '',
      createdAt: new Date().toISOString(),
      status: 'approved'
    };
    reviews.unshift(newRev);
    this.persist(this.state);
    return newRev;
  }

  public toggleReviewStatus(id: string, status?: 'approved' | 'pending' | 'hidden'): CustomerReview | null {
    const rev = this.getCustomerReviews().find(r => r.id === id);
    if (!rev) return null;
    if (status) {
      rev.status = status;
    } else {
      rev.status = rev.status === 'approved' ? 'hidden' : 'approved';
    }
    this.persist(this.state);
    return rev;
  }

  public replyToReview(id: string, reply: string): CustomerReview | null {
    const rev = this.getCustomerReviews().find(r => r.id === id);
    if (!rev) return null;
    rev.reply = reply;
    this.persist(this.state);
    return rev;
  }

  // 6. Store Settings
  public getStoreSettings(): StoreSettings {
    if (!this.state.settings) {
      this.state.settings = this.defaultSettings();
    }
    return this.state.settings;
  }

  public updateStoreSettings(newSettings: Partial<StoreSettings>): StoreSettings {
    this.state.settings = {
      ...this.getStoreSettings(),
      ...newSettings
    };
    this.persist(this.state);
    return this.state.settings;
  }
}

export const store = new Store();
